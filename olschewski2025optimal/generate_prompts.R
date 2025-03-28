########################### Data and Code by Sebastian Olschewski #########################

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
dat <- read.csv("study2_finaldata_no_trialwise_exclusions.csv",stringsAsFactors = F )
pids <- unique(dat$participant.label);lpids <- length(pids)

# make choices A for Option A and B for option B, NA if no response due to time limit per block reached
dat$choiceoption <- ifelse(dat$player.choice==0, "A", ifelse(dat$player.choice==1, "B", NA))

# Container
all_prompts <- list()

# General Instructions
prom <- "A lottery consists of two monetary outcomes in Experimental Pounds that each occur with a given probability. For example: Lottery A: £50 with 40% or £30 with 60%. Imagine you play this lottery for real money and the computer determines randomly which outcome you will get according to the stated probabilities. You can think of the probabilities as the number of balls with a given outcome in an urn of 100 balls. In case of Lottery A this means there are 40 balls with a win of £50 and 60 balls with a win of £30 in the urn. You will be shown two lotteries side by side, and you should say which of the two you would prefer to play. There are no right or wrong choices, your task is just to indicate which lottery is more attractive to you personally. There will be 2 different types of blocks that we will explain immediately before each block.\n"

for (cparticipant in pids) {
  df_participant <- subset(dat, cparticipant == dat$participant.label)
  
  for (cblock in 1:8) {
    df_task <- subset(df_participant, cblock == df_participant$player.block)
    
    # Block instructions
    if (unique(df_task$timed)==0) {
      prom <- paste0(prom, "Block ", cblock, ":\n Self-Paced Block: you will make 20 choices between two lotteries. You will be shown them one after the other and you can take as much time as possible to give your answers to these 20 choices.")

      } else if(unique(df_task$timed)==1) {
      prom <- paste0(prom, "Block ", cblock, ":\n Time-Limit Block: you have a time limit of 1:20 minutes to choose repeatedly between two lotteries the one you prefer. There are up to 40 lottery pairs and you can make decisions until your time is up. In the Time-Limit Block, it is very likely that you cannot process all available lotteries until the time runs up. Thus, there is a trade-off between the careful selection of the preferred lottery in a given trial and the number of trials you can finish in the given time. If you go too slow, you will not have the chance to choose your preferred lottery in later trials. If you go too fast, you might choose by accident a lottery that you do not really prefer.") 
      }

    prom <- paste0(prom, "It is in the best of your interest and important for us and our research for you to honestly choose according to your subjective preferences for as many trials as you can. At the end of the experiment the computer will select randomly one trial out of all blocks that will determine which lottery you will play for real money. There are two possible cases: If for the selected trial you made a choice, the computer will play out the lottery that you chose. In this case, if you chose carefully you get your preferred lottery played out. If for the selected trial you did not make a choice due to the time limit, the computer will play out one of the two lotteries randomly. So in this case, you may get a worse gamble played out than you would have chosen. Finally, a random draw of the computer according to the stated probabilities will determine which real monetary bonus you will get from the lottery you play. All outcomes are presented in Experimental Pounds. The exchange rate for your bonus is 20 Experimental £ are 1 real British £. So, a lottery that states a win of Experimental £80 could result in an additional payment for you of £4.\n")
    
    # Extract the trial numbers within each block 
    ctrialrange <- sort(df_task$subsession.round_number)
    for (ctrial in ctrialrange) {
      df_trial <- subset(df_task, ctrial == df_task$subsession.round_number)
      
      # Choice trial and response
      if (is.na(df_trial$choiceoption)) {
        prom <- paste0(prom,"Which lottery do you want to play? Option A: £", df_trial$player.oa1," with ",df_trial$player.pa1," % or £", df_trial$player.oa2," with ",df_trial$player.pa2," %. Option B: £", df_trial$player.ob1," with ",df_trial$player.pb1," % or £", df_trial$player.ob2," with ",df_trial$player.pb2," %. You failed to respond in time.")
                       
      } else {
        prom <- paste0(prom,"Which lottery do you want to play? Option A: £", df_trial$player.oa1," with ",df_trial$player.pa1," % or £", df_trial$player.oa2," with ",df_trial$player.pa2," %. Option B: £", df_trial$player.ob1," with ",df_trial$player.pb1," % or £", df_trial$player.ob2," with ",df_trial$player.pb2," %. You choose <<", df_trial$choiceoption, ">>")
      }
      
      # Make list with prompt and additional infos 
      prom <- trimws(prom)
      all_prompts[[length(all_prompts) + 1]] <- list(
        text = prom,
        experiment = paste0("olschewski2025optimal/1"),
        participant = cparticipant,
        age = df_trial$age,
        nationality = df_trial$Nationality)
      
      # delete old prompt 
      prom <- ""
    }
  }
}

# write file
writeLines(sapply(all_prompts, toJSON, auto_unbox = TRUE), "prompts.jsonl")
  