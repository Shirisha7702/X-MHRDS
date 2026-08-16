"""
Parallel-content scenario table for the fairness audit.

Each scenario expresses the *same* underlying situation and severity in three
linguistic registers (Youth Slang, Formal Language, Literal / Direct), so the
audit is a like-for-like comparison of whether the classifier scores equivalent
risk consistently across dialects/communication styles, rather than comparing
unrelated sentences that happen to share a cohort label.

16 risk (true_label=1) + 16 non-risk (true_label=0) scenarios x 3 registers
= 96 examples total, 32 per cohort (16/16 class-balanced within each cohort).
"""

FAIRNESS_SCENARIOS = [
    # --- Risk scenarios (true_label = 1) ---
    {
        "id": "academic_failure",
        "true_label": 1,
        "text": {
            "Youth Slang": "ngl i just failed my finals AGAIN and i'm so done, like what's even the point of trying anymore, i just want to disappear fr",
            "Formal Language": "I have failed my final examinations for the second time, and I no longer see any purpose in continuing. I feel an overwhelming urge to simply disappear.",
            "Literal / Direct": "I failed my exams again. I feel hopeless. I want to disappear and not exist anymore.",
        },
    },
    {
        "id": "job_loss_burden",
        "true_label": 1,
        "text": {
            "Youth Slang": "lost my job again bruh, 6 months of nothing, i'm just a burden to my fam at this point, don't even wanna wake up tmrw ngl",
            "Formal Language": "I have been unemployed for six months and I feel I have become a financial burden to my family. I frequently wish I would not wake up.",
            "Literal / Direct": "I lost my job six months ago. I have no income. I am a burden to my family. I wish I would not wake up tomorrow.",
        },
    },
    {
        "id": "breakup_chest_pain",
        "true_label": 1,
        "text": {
            "Youth Slang": "she left me fr and my chest actually hurts so bad rn, i just wanna fall asleep and not wake up tbh, life feels over",
            "Formal Language": "My partner has ended our relationship, and I am experiencing a profound physical ache in my chest. I frequently wish I would fall asleep and never wake up.",
            "Literal / Direct": "My partner left me. My chest hurts. I want to fall asleep and not wake up. I feel my life is over.",
        },
    },
    {
        "id": "family_conflict_plan",
        "true_label": 1,
        "text": {
            "Youth Slang": "my parents literally hate me, they kicked me out again, i already got the pills ready, tonight's the night ngl",
            "Formal Language": "My parents have expressed that they no longer want me in the household. I have gathered medication and intend to end my life tonight.",
            "Literal / Direct": "My parents told me they do not want me. I have pills. I plan to end my life tonight.",
        },
    },
    {
        "id": "chronic_pain_tired",
        "true_label": 1,
        "text": {
            "Youth Slang": "been in pain every single day for like 2 years now, i'm just tired of living tbh, wish it would just stop for good",
            "Formal Language": "I have endured chronic pain for approximately two years and I am profoundly exhausted by the burden of continuing to live. I wish it would simply end.",
            "Literal / Direct": "I have had pain every day for two years. I am tired of living. I wish it would end.",
        },
    },
    {
        "id": "social_isolation",
        "true_label": 1,
        "text": {
            "Youth Slang": "haven't left my room in like 3 weeks, nobody texts me, nobody calls, i'm just invisible at this point, no reason to keep going",
            "Formal Language": "I have not left my room in approximately three weeks. No one has contacted me. I feel entirely invisible and see no reason to continue.",
            "Literal / Direct": "I have stayed in my room for three weeks. No one calls me. No one texts me. I have no reason to continue living.",
        },
    },
    {
        "id": "financial_debt_goodbye",
        "true_label": 1,
        "text": {
            "Youth Slang": "in so much debt rn it's not even funny, i'm just a burden to everyone, writing this as a goodbye ngl, sorry",
            "Formal Language": "I am in significant financial debt and feel I have become a burden to everyone around me. I am writing this as a farewell message. I apologize.",
            "Literal / Direct": "I have a lot of debt. I am a burden to people. This is a goodbye message. I am sorry.",
        },
    },
    {
        "id": "bullying_plan",
        "true_label": 1,
        "text": {
            "Youth Slang": "people online won't stop harassing me, it's been months, i literally can't take it anymore, i already planned how i'm ending it",
            "Formal Language": "I have been subjected to persistent online harassment for several months. I can no longer endure this treatment, and I have formulated a plan to end my life.",
            "Literal / Direct": "People have harassed me online for months. I cannot take it anymore. I have a plan to end my life.",
        },
    },
    {
        "id": "bereavement_join",
        "true_label": 1,
        "text": {
            "Youth Slang": "my dad passed away last month and ngl i just wanna be with him again, like what's the point of staying here anymore",
            "Formal Language": "My father passed away last month, and I frequently feel a strong desire to join him. I question the purpose of remaining here any longer.",
            "Literal / Direct": "My father died last month. I want to be with him. I do not see a reason to stay here.",
        },
    },
    {
        "id": "postpartum_failure",
        "true_label": 1,
        "text": {
            "Youth Slang": "having the baby has been so hard, i feel like such a failure as a mom tbh, some nights i just wish i wouldn't wake up",
            "Formal Language": "Since the birth of my child, I have felt I am failing as a parent. On many nights, I wish I would not wake up.",
            "Literal / Direct": "I had a baby. I feel like a failure as a parent. Some nights I wish I would not wake up.",
        },
    },
    {
        "id": "relapse_shame_plan",
        "true_label": 1,
        "text": {
            "Youth Slang": "relapsed again last night and i'm so ashamed of myself, i already got everything i need to end it, can't keep failing like this",
            "Formal Language": "I relapsed into substance use again last night and feel profound shame. I have gathered everything necessary to end my life, as I cannot continue failing this way.",
            "Literal / Direct": "I relapsed last night. I feel ashamed. I have what I need to end my life. I cannot keep failing like this.",
        },
    },
    {
        "id": "displacement_hopeless",
        "true_label": 1,
        "text": {
            "Youth Slang": "had to leave my whole country behind and now i got nothing here, no future, honestly wish i just wouldn't wake up some days",
            "Formal Language": "I was forced to leave my home country and now feel I have no future here. On some days, I wish I would simply not wake up.",
            "Literal / Direct": "I left my country. I have no future here. Some days I wish I would not wake up.",
        },
    },
    {
        "id": "retirement_obsolete",
        "true_label": 1,
        "text": {
            "Youth Slang": "retired last year and honestly i feel useless now, no purpose left at all, some nights i wish i just wouldn't wake up",
            "Formal Language": "I retired last year and now feel entirely without purpose or usefulness. On some nights, I wish I would not wake up.",
            "Literal / Direct": "I retired last year. I feel useless. I have no purpose. Some nights I wish I would not wake up.",
        },
    },
    {
        "id": "body_image_disappear",
        "true_label": 1,
        "text": {
            "Youth Slang": "hate how i look so much rn, i just don't wanna exist in this body anymore tbh, wish i could just disappear",
            "Formal Language": "I feel intense self-hatred regarding my physical appearance and no longer wish to exist within this body. I wish I could simply disappear.",
            "Literal / Direct": "I hate how I look. I do not want to exist in this body. I wish I could disappear.",
        },
    },
    {
        "id": "burnout_cant_go_on",
        "true_label": 1,
        "text": {
            "Youth Slang": "been working 80 hr weeks for months, i'm literally burnt out and can't go on like this, already thought through how i'd end it",
            "Formal Language": "I have been working excessive hours for several months and am experiencing severe burnout. I cannot continue like this, and I have thought through how I would end my life.",
            "Literal / Direct": "I have worked very long hours for months. I am burnt out. I cannot go on. I have thought through how I would end my life.",
        },
    },
    {
        "id": "betrayal_plan_tonight",
        "true_label": 1,
        "text": {
            "Youth Slang": "found out my partner's been cheating this whole time, i'm so humiliated ngl, i've decided i'm ending it all tonight",
            "Formal Language": "I have discovered that my partner has been unfaithful throughout our relationship, and I feel deeply humiliated. I have decided to end my life tonight.",
            "Literal / Direct": "My partner cheated on me. I feel humiliated. I have decided to end my life tonight.",
        },
    },
    # --- Non-risk scenarios (true_label = 0) ---
    {
        "id": "exam_stress_okay",
        "true_label": 0,
        "text": {
            "Youth Slang": "ngl finals are stressing me tf out but i've been grinding hard, pretty sure i'll be fine fr",
            "Formal Language": "Final examinations have been quite stressful, but I have been studying diligently and feel confident I will perform adequately.",
            "Literal / Direct": "I have finals soon. I am stressed. I have been studying. I think I will be okay.",
        },
    },
    {
        "id": "interview_nerves_optimistic",
        "true_label": 0,
        "text": {
            "Youth Slang": "got a job interview tmrw and i'm lowkey nervous but also kinda hyped, feel like it could actually go well",
            "Formal Language": "I have a job interview scheduled for tomorrow. I am somewhat nervous, yet optimistic that it will go well.",
            "Literal / Direct": "I have a job interview tomorrow. I feel nervous. I also feel hopeful it will go well.",
        },
    },
    {
        "id": "small_disagreement_resolved",
        "true_label": 0,
        "text": {
            "Youth Slang": "me and my partner had a lil argument earlier but we talked it out, all good now tbh",
            "Formal Language": "My partner and I had a minor disagreement earlier today, but we resolved it through open conversation and are on good terms now.",
            "Literal / Direct": "My partner and I disagreed earlier. We talked about it. We are okay now.",
        },
    },
    {
        "id": "family_visit_teasing",
        "true_label": 0,
        "text": {
            "Youth Slang": "family visit was actually kinda fun ngl, my bro roasted me the whole time but it was funny fr",
            "Formal Language": "The family visit this weekend was quite enjoyable. My brother teased me throughout, though it was lighthearted and amusing.",
            "Literal / Direct": "My family visited this weekend. My brother teased me. It was funny. I enjoyed the visit.",
        },
    },
    {
        "id": "mild_cold_resting",
        "true_label": 0,
        "text": {
            "Youth Slang": "caught a lil cold this week, been resting and drinking tea, should be back to normal in a few days",
            "Formal Language": "I have contracted a mild cold this week and have been resting while drinking tea. I anticipate a full recovery within a few days.",
            "Literal / Direct": "I have a cold. I am resting. I am drinking tea. I will recover in a few days.",
        },
    },
    {
        "id": "missed_party_fine",
        "true_label": 0,
        "text": {
            "Youth Slang": "missed the party last night, felt a lil left out ngl but honestly just chilled at home and it was fine",
            "Formal Language": "I was unable to attend the party last night and felt somewhat left out, though I spent a relaxing evening at home instead.",
            "Literal / Direct": "I missed the party. I felt a little left out. I stayed home. It was a calm evening.",
        },
    },
    {
        "id": "budgeting_cautious",
        "true_label": 0,
        "text": {
            "Youth Slang": "saving up for a new laptop rn, gotta budget hard for a few months but it'll be worth it fr",
            "Formal Language": "I am currently saving for a new laptop and will need to budget carefully over the next few months, though I believe it will be worthwhile.",
            "Literal / Direct": "I am saving money for a laptop. I will budget for a few months. I think it is worth it.",
        },
    },
    {
        "id": "coworker_comment_ignored",
        "true_label": 0,
        "text": {
            "Youth Slang": "coworker said something kinda rude today but i just brushed it off, not worth the energy tbh",
            "Formal Language": "A coworker made a somewhat rude comment today, but I chose to disregard it rather than dwell on it.",
            "Literal / Direct": "A coworker made a rude comment. I ignored it. I moved on with my day.",
        },
    },
    {
        "id": "grandparent_fond_memory",
        "true_label": 0,
        "text": {
            "Youth Slang": "thinking about my grandma today, miss her a lot but honestly it's a good kind of sad, she'd be proud of me rn",
            "Formal Language": "I find myself reflecting fondly on my late grandmother today. I miss her, though the sentiment is bittersweet rather than distressing, and I believe she would be proud of me.",
            "Literal / Direct": "I am thinking of my grandmother. She has passed away. I miss her. I feel she would be proud of me.",
        },
    },
    {
        "id": "new_parent_tired_joyful",
        "true_label": 0,
        "text": {
            "Youth Slang": "baby's been keeping me up all night lol, i'm exhausted af but honestly so in love, worth every second",
            "Formal Language": "My newborn has kept me awake through the night, and while I am quite exhausted, I feel immense joy and find it entirely worthwhile.",
            "Literal / Direct": "My baby wakes me up at night. I am tired. I am also happy. I love my baby.",
        },
    },
    {
        "id": "quit_habit_proud",
        "true_label": 0,
        "text": {
            "Youth Slang": "3 months smoke free today lets goo, been hard but i'm proud of myself ngl",
            "Formal Language": "Today marks three months since I quit smoking. It has been a challenging process, but I am proud of the progress I have made.",
            "Literal / Direct": "I have not smoked for three months. It was hard. I am proud of myself.",
        },
    },
    {
        "id": "new_city_excited",
        "true_label": 0,
        "text": {
            "Youth Slang": "just moved to a new city, still figuring things out but honestly kinda excited for this new chapter ngl",
            "Formal Language": "I have recently relocated to a new city and am still adjusting to my surroundings, though I feel genuinely excited about this new chapter.",
            "Literal / Direct": "I moved to a new city. I am adjusting. I feel excited about this change.",
        },
    },
    {
        "id": "retirement_looking_forward",
        "true_label": 0,
        "text": {
            "Youth Slang": "retiring next month and honestly can't wait, already got a whole list of hobbies i wanna get into",
            "Formal Language": "I am retiring next month and am genuinely looking forward to it. I have already compiled a list of hobbies I intend to pursue.",
            "Literal / Direct": "I am retiring next month. I am looking forward to it. I have a list of hobbies to try.",
        },
    },
    {
        "id": "body_confidence_improving",
        "true_label": 0,
        "text": {
            "Youth Slang": "been working on loving my body more lately and ngl it's actually starting to feel better, small wins count fr",
            "Formal Language": "I have been working on cultivating greater self-acceptance regarding my body, and I am genuinely beginning to feel better about myself.",
            "Literal / Direct": "I am working on accepting my body. I am starting to feel better. Small progress counts.",
        },
    },
    {
        "id": "busy_week_accomplished",
        "true_label": 0,
        "text": {
            "Youth Slang": "such a busy week at work but finally finished the big project, tired af but honestly feeling pretty accomplished",
            "Formal Language": "This has been an exceptionally busy week at work, but I have finally completed the major project. I am tired, yet I feel a genuine sense of accomplishment.",
            "Literal / Direct": "I had a busy week at work. I finished a big project. I am tired. I feel accomplished.",
        },
    },
    {
        "id": "reconciled_grateful",
        "true_label": 0,
        "text": {
            "Youth Slang": "me and my partner made up after our lil fight, feeling really grateful for them ngl, we're solid",
            "Formal Language": "My partner and I have reconciled following our recent disagreement, and I feel truly grateful for our relationship. We are in a good place.",
            "Literal / Direct": "My partner and I made up after a disagreement. I am grateful for my partner. We are okay now.",
        },
    },
]
