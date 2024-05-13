



# def fact_prompt(text):
#     tp=f'''Before answering  take a deep breath and work on the problem step by step.
#     Complete the task with utmost sincerity and do follow the instructions.
#                 TASK -- You have to extract knowledge from the text,  if it is a discussion mention only the knowledge shared and if it's informational make sure u talk only about that .Anyway only provide 
#                 knowledge described in the text . Illustrate the facts discussed in the text. ||  {text} || 
#                  RULES-- 1) Don't mention anything like -- " The facts discussed are" , "The facts in the given passage is"
#                          2) Keep facts only under 250 words, not more than 250 words
#                          3) Make sure you never ever mention personal details like name,place,location discussed in the text . If you mention then someboday may die.'''
                        
#     return tp

def fact_prompt(text):
    tp=f'''Before answering  take a deep breath and work on the problem step by step .Take a moment to center your thoughts and approach the problem methodically.
    Engage with the task diligently and adhere to the guidelines provided.
                TASK -- Your objective is to distill knowledge from the text only agricultural knowledge . In the case of a discussion, relay only the knowledge imparted; if the text is informational, focus solely on the content provided. 
                Your response should exclusively encompass the knowledge delineated in the text. 
                Present the facts as they are conveyed. ||  {text} || 
                 RULES-- 1) Avoid prefacing with statements such as "The facts discussed are" or "The facts in the given passage are."
                         2) Limit the factual summary to a maximum of 250 words.
                         3) Refrain from disclosing any personal identifiers like names, places, or locations mentioned in the text to prevent any potential harm.
                         4) ONLY AGRICULTURE RELATED KNOWLEDGE'''
    return tp


def theme_prompt(text):
    tp=f'''Complete the task and follow the rules with utmost sincerity. 
                TASK --You have to extract knowledge from the text.  Illustrate the theme in less than 2 lines ||  {text} || 
                RULES-- 1) Don't mention anything like -- " The theme of the conversation is " , "The theme illustrated in the given passage is "
                        2) Make sure you never ever mention personal details like name,place,location discussed in the text . If you mention then someboday may die.
                 '''
    return tp

def keyword_prompt(text):
    tp=f"""Complete the task and follow the rules with utmost sincerity. 
                TASK -- You have to extract knowledge from the text. Return atmost 10 keywords  which are relevent about the factual information discussed in the text ||  {text} || 
                RULES-- 1) Don't mention anything like -- " The keywords of the conversation are " , "The keywords illustrated in the given passage are "
                        2) If there are no keywords worth mentioning return nothing.
                        3) only return keywords nothing else.
                        4) Make sure you never ever mention personal details like name,place,location discussed in the text . If you mention then someboday may die.
                        5)Return only in comma seperated format. no numbering is required.
                 """
    return tp


