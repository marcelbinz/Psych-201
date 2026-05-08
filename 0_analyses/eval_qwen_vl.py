# --- HOTFIX: Triton PTX header .version 8.6 -> 8.5 before ptxas runs ---
import subprocess, re

_ORIG_RUN = subprocess.run
_PTX_FILE_RE = re.compile(r"(\S+\.ptx)(?:\s|$)")

def _maybe_downgrade_ptx_header(cmd: str):
    if "ptxas" not in cmd or ".ptx" not in cmd:
        return
    m = _PTX_FILE_RE.search(cmd)
    if not m:
        return
    ptx_path = m.group(1)
    try:
        with open(ptx_path, "r", encoding="utf-8") as f:
            txt = f.read()
        if ".version 8.6" in txt:
            with open(ptx_path, "w", encoding="utf-8") as f:
                f.write(txt.replace(".version 8.6", ".version 8.5"))
    except FileNotFoundError:
        pass

def run_patched(cmd, *args, **kwargs):
    if isinstance(cmd, str):
        _maybe_downgrade_ptx_header(cmd)
    return _ORIG_RUN(cmd, *args, **kwargs)

subprocess.run = run_patched
# -----------------------------------------------------------------------

import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'

from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration
import argparse
import torch
import gc
from pathlib import Path
from tqdm import tqdm
from datasets import load_dataset

_space_before_close = re.compile(r"\s+(?=>>)")  # whitespace right before >>

def safe_truncate_angle(text: str, max_len: int) -> str:
    """
    Truncate to <= max_len characters, ensuring we don't end with an unclosed <<...>>.
    Assumes markers are '<<' and '>>' and not nested.
    """
    t = (
        text[:max_len]
        .replace("<<skip>>", "<<skip>>.")
        .replace("<<-", "<< -")
        .replace("<<think>>", "<< think>>")
        .replace("More Details >>", "More Details ->")
    )

    if t.count("<<") > t.count(">>"):
        last_open = t.rfind("<<")
        if last_open != -1:
            t = t[:last_open]

    t = _space_before_close.sub("", t)
    return t

def find_subseq(seq, subseq, start=0):
    n, m = len(seq), len(subseq)
    for i in range(start, n - m + 1):
        if seq[i : i + m] == subseq:
            return i
    return -1

def collate(example):
    ids = example["input_ids"][0]
    labels = [-100] * len(ids)

    i = 0
    while True:
        s = find_subseq(ids, l_id, start=i)
        if s == -1:
            break

        content_start = s + len(l_id)
        e = find_subseq(ids, r_id, start=content_start)
        if e == -1:
            e = len(ids)

        labels[content_start:e] = ids[content_start:e]
        i = e + len(r_id)

    example["labels"] = [labels]
    return example

def tokenization(example):
    prompt = safe_truncate_angle(example["text"], args.max_seq_length)
    return tokenizer(text=[prompt], truncation=False)

def parse_logits(logits, labels):
    """
    logits: [T, V] on some device
    labels: [T] on same device, with -100 masked positions
    returns: Tensor of summed NLL per response span (on CPU)
    """
    nll = torch.nn.functional.cross_entropy(logits, labels, reduction="none")
    total_loss = []
    item_loss = 0.0
    item_counter = 0
    for i in range(nll.shape[0]):
        if int(labels[i].item()) != -100:
            item_loss = item_loss + nll[i]
            item_counter += 1
        else:
            if item_counter != 0:
                total_loss.append(item_loss)
                item_loss = 0.0
                item_counter = 0
    if item_counter != 0:
        total_loss.append(item_loss)
    if len(total_loss) == 0:
        return torch.empty(0, device="cpu")
    return torch.stack(total_loss).detach().cpu()

def get_inputs_for_model(participant, model, use_device_map: bool):
    """
    If model is sharded via device_map="auto": keep inputs on CPU and let Accelerate move them.
    If model is single-device: move inputs to that device.
    """
    if use_device_map:
        return participant["input_ids"], participant["attention_mask"]
    dev = next(model.parameters()).device
    return (
        participant["input_ids"].to(dev, non_blocking=True),
        participant["attention_mask"].to(dev, non_blocking=True),
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--num-proc", type=int, default=16)
    parser.add_argument("--max-seq-length", type=int, default=32768)
    args = parser.parse_args()

    print("cuda?", torch.cuda.is_available(), "n_gpus", torch.cuda.device_count(), flush=True)

    # -------- Load model in a way that works for:
    # (A) 1 process sees 4 GPUs -> device_map="auto"
    # (B) 4 processes each see 1 GPU -> single-device CUDA load
    use_device_map = torch.cuda.is_available() and (torch.cuda.device_count() > 1)

    common_kwargs = dict(
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
    )

    if use_device_map:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            args.model,
            device_map="auto",
            **common_kwargs,
        )
    else:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            args.model,
            **common_kwargs,
        ).to("cuda")

    model.eval()

    if hasattr(model, "hf_device_map"):
        print("device_map devices:", set(model.hf_device_map.values()), flush=True)
    else:
        print("no hf_device_map (single-device load)", flush=True)

    tokenizer = AutoProcessor.from_pretrained(
        args.model,
        local_files_only=True,
    )

    # marker token IDs
    l_id = tokenizer(text=" <<", add_special_tokens=False).input_ids[0]
    r_id = tokenizer(text=">>", add_special_tokens=False).input_ids[0]
    print("l_id:", l_id, flush=True)
    print("r_id:", r_id, flush=True)

    dataset_full = load_dataset("marcelbinz/Psych-201-test")["train"]

    for study in dataset_full.unique("study"):
        print(study, flush=True)

        dataset = dataset_full.filter(lambda ex: ex["study"] == study, num_proc=args.num_proc)
        dataset = dataset.map(tokenization, num_proc=args.num_proc)
        dataset = dataset.map(collate, num_proc=args.num_proc)
        dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"], output_all_columns=True)

        nlls = {}

        with torch.inference_mode():
            for participant in tqdm(dataset):
                input_ids, attention_mask = get_inputs_for_model(participant, model, use_device_map)

                model_outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    return_dict=True,
                    use_cache=False,
                )

                logits = model_outputs["logits"][0, :-1]                # [T-1, V] on model device
                labels = participant["labels"][0, 1:].to(logits.device, non_blocking=True)

                participant_nll = parse_logits(logits, labels)

                key = participant["participant_reindexed"]
                if torch.is_tensor(key):
                    key = int(key.item())
                nlls[key] = participant_nll

                del labels, model_outputs
                torch.cuda.empty_cache()
                gc.collect()

        folder_path = "data/" + study.replace("/", "-")
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        torch.save(nlls, folder_path + "/" + args.model.replace("/", "-") + ".pth")
