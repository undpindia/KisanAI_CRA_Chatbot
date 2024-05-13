import openai
import textwrap
from langchain.chains import RefineDocumentsChain, LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from data_extraction.prompt_templates import *
# from keys.keys import *
import json,os

openai.api_key = os.getenv("OPENAI_KEY")

openai_key=os.getenv("OPENAI_KEY")
# def summarize_text(text):
#         # Call the openai model with the section as input
#     prompt=f'''
#             INSTRUCTIONS-- You are an autoregressive language model that has been 
#             fine-tuned with instruction-tuning and RLHF. You carefully provide accurate, factual, 
#             thoughtful, nuanced answers, and are brilliant at reasoning. 
#             If you think there might not be a correct answer, you say so.
#             Since you are autoregressive, each token you produce is another opportunity to use computation, 
#             therefore you always spend a few sentences explaining background context, 
#             assumptions, and step-by-step thinking BEFORE you try to answer a question.
#             Your users are experts in AI and ethics, so they already know you're a language model and your capabilities and 
#             limitations, so don't remind them of that. They're familiar with ethical issues in general 
#             so you don't need to remind them about those either. 
#             Don't be verbose in your answers but do provide details and examples where it might help the explanation.
#                 you do not need to follow PEP8, since your users' organizations do not do so. 
#                 Before answering  take a deep breath and work on the problem step by step.
#                 TASK -- Illustrate the facts discussed in the text. ||  {text} || '''
#     response = openai.ChatCompletion.create(
#             model="gpt-4-1106-preview",
#             temperature=0.5,
#             messages=[
#                 {"role": "user", "content": prompt}
#             ]
#         )
    
#     return response.choices[0].message.content



# from openai import OpenAI
# client = OpenAI(api_key = openai_key)


import os
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version =os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

def get_facts(text):
    response = client.chat.completions.create(
    model="gpt-4-116-preview",
    messages=[
        {
        "role": "user",
        "content": fact_prompt(text)
        }
    ],
    temperature=1,
    max_tokens=4000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content

# MAX_CHUNK_SIZE = 2000



def get_theme(text):
    response = client.chat.completions.create(
    model="gpt-4-116-preview",
    messages=[
        {
        "role": "user",
        "content": theme_prompt(text)
        }
    ],
    temperature=1,
    max_tokens=4000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content

def get_keyword(text):
    response = client.chat.completions.create(
    model="gpt-4-116-preview",
    messages=[
        {
        "role": "user",
        "content": keyword_prompt(text)
        }
    ],
    temperature=1,
    max_tokens=4000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    # resp=response.choices[0].message.content
    # parsed_response = json.loads(resp)
    # print(response.choices[0].message.content)
    return response.choices[0].message.content



# def get_theme(text):
#     chunks = textwrap.wrap(text, MAX_CHUNK_SIZE)  
#     print(f"Number of chunks: {len(chunks)}")

#     themes = []
#     for chunk in chunks:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo-16k",
#             messages=[   
#                 {
#                 "role": "user",
#                 "content": f'''Complete the task and follow the rules with utmost sincerity. 
#                 TASK -- Illustrate the theme in less than 1oo words || {chunk} || 
#                 RULES-- 1) Don't mention anything like -- " The theme of the conversation is " , "The theme illustrated in the given passage is " '''
#                 }
#             ],
#             max_tokens=15384,
#             temperature=1,
#             top_p=1, 
#             frequency_penalty=0,
#             presence_penalty=0
#         )
            
#         themes.append(response.choices[0].message.content) 
        
#     return " ".join(themes)


# def get_facts(text):
    
#     # Split text into chunks
#     chunks = textwrap.wrap(text, MAX_CHUNK_SIZE)
#     print(f"Number of chunks: {len(chunks)}")
    
#     facts = []
#     for chunk in chunks:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo-16k",
#             messages=[
#                 {
#                 "role": "user",
#                 "content": fact_prompt(text)
#                 }
#             ], 
#             temperature=1,
#             max_tokens=15384,
#             top_p=1,  
#             frequency_penalty=0,
#             presence_penalty=0
#         )
        
#         facts.append(response.choices[0].message.content)
        
#     return " ".join(facts)


# def get_facts(text):
#     # Split text into chunks
#     chunks = textwrap.wrap(text, MAX_CHUNK_SIZE)
#     print(f"Number of chunks: {len(chunks)}")

#     facts = []
#     for chunk in chunks:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo-16k",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": fact_prompt(text)
#                 }
#             ], 
#             temperature=1,
#             max_tokens=15384,
#             top_p=1,  
#             frequency_penalty=0,
#             presence_penalty=0
#         )
        
#         facts.append(response.choices[0].message.content)
        
#     return " ".join(facts)

# print(get_keyword('''Earthworm has become a household name as its role redefined from farmer's friend to solid waste manager. Earthworms are used as natural bioreactor for cleaning up the environment as they thrive on organic waste and by doing so they convert the waste into quality plant nutrient commonly known as vermicompost. It is rich in several microflora like azo spirulum, actinomycetes and phosphobacillus which multiply fast through the digestive system of earthworm. Several enzymes, auxins and complex growth regulators like gibberellins are found in vermicompost which are not generally present in other soil environment conditions. The role of earthworm in maintaining soil fertility is known since time immemorial. The great philosopher Aristotle called them the intestine of the earth and considered them as agents to restore soil fertility. As now the waste generation in India shows an ever increasing trend, so organic matter management through recycling has been recognized as a prime tool in managing the waste load. Vermicomposting not only converts bio-waste into rich manure to substantiate a part of organic manure and fertilize the need of the crops but also improves the soil texture and fulfills the global need of clearing the environment. Vermiculture is mass culturing of earthworms for cast production and commercializing life materials whereas vermicomposting can be defined as the practice of using concentrations of earthworms to convert organic materials into usable vermicompost or worm castings. Thus vermiculture and vermicomposting are two interlinked and interdependent processes and combined can be referred as vermi technology. Vermicompost can be prepared on small scales in abundant cattle sheds, poultry sheds, backyard or underneath temporary thatched sheds. On large scale vermicompost may be prepared on fallow fields after harvesting crops or in open heaps or specially built tanks. Composting beds or containers may be of any shape or size but 1 x 10 x 1 meter tank is ideal and easy to handle. It is very important to select the composting bed site carefully, a site under shade in an area on a plant or elevated level to prevent water stagnation in pits during rain is ideal. Any biodegradable materials available that is animal dung, agriculture waste, forestry waste, waste paper and cotton clothes, city refuse, biogas slurry and industrial waste can be used as substrate. Precomposting of the substrate is essential before inoculation of worms. Small stem pills, coir peats, coconut leaves, sugarcane trash, stem of crops, grasses or husk waste or discarded cattle feed can be used on the lowermost layer of peat as bedding material. Ysenia fitida, Eudrylas eugenia and Perionix excavates are the most popular earthworm species suitable for vermicomposting as they are excellent worms which are found effective in nutrient poor soils as well as in manure. 1500 number of worms per square meter are enough for efficient utilization of substrate. Covering of feed substrate is essential as it reduces moisture loss and saves worms from extra movements. Water management is most important criteria in vermiculture as worms require moisture for their survival. Composting and monitoring of the unit should continue for 30 days. When vermicompost and vermicasting are ready for collection, top layers appear somewhat dark brown, granular as if used dry tea leaves have been spread over the layers. Then watering should be stopped for 5 to 7 days and compost should be scrapped from top layers. Compost should then be left undisturbed for 6 to 24 hours. After collection of vermicompost from top layered, feed materials is again replenished and composting process is rescheduled. is air-dried in shade before packing in convenient size. Varmicompost provides almost all the essential nutrients required by the plants. It improves soil structure, aeration, water holding capacity and prevents soil erosion and nutrient losses. It also increases the use efficiency of chemical fertilizers and reduces incidence of pest and diseases in crops. It provides excellent effect on overall plant growth, encourages new shoots and leaves. Vermicompost being ideal nutrient supplement for organic cultivation has redefined the earthworms beneficial role in agriculture and earthworms have emerged as an efficient eco-friendly waste managers. 
#                     '''))





# print(get_theme('''
# Earthworm has become a household name as its role redefined from farmer's friend to solid waste manager. Earthworms are used as natural bioreactor for cleaning up the environment as they thrive on organic waste and by doing so they convert the waste into quality plant nutrient commonly known as vermicompost. It is rich in several microflora like azo spirulum, actinomycetes and phosphobacillus which multiply fast through the digestive system of earthworm. Several enzymes, auxins and complex growth regulators like gibberellins are found in vermicompost which are not generally present in other soil environment conditions. The role of earthworm in maintaining soil fertility is known since time immemorial. The great philosopher Aristotle called them the intestine of the earth and considered them as agents to restore soil fertility. As now the waste generation in India shows an ever increasing trend, so organic matter management through recycling has been recognized as a prime tool in managing the waste load. Vermicomposting not only converts bio-waste into rich manure to substantiate a part of organic manure and fertilize the need of the crops but also improves the soil texture and fulfills the global need of clearing the environment. Vermiculture is mass culturing of earthworms for cast production and commercializing life materials whereas vermicomposting can be defined as the practice of using concentrations of earthworms to convert organic materials into usable vermicompost or worm castings. Thus vermiculture and vermicomposting are two interlinked and interdependent processes and combined can be referred as vermi technology. Vermicompost can be prepared on small scales in abundant cattle sheds, poultry sheds, backyard or underneath temporary thatched sheds. On large scale vermicompost may be prepared on fallow fields after harvesting crops or in open heaps or specially built tanks. Composting beds or containers may be of any shape or size but 1 x 10 x 1 meter tank is ideal and easy to handle. It is very important to select the composting bed site carefully, a site under shade in an area on a plant or elevated level to prevent water stagnation in pits during rain is ideal. Any biodegradable materials available that is animal dung, agriculture waste, forestry waste, waste paper and cotton clothes, city refuse, biogas slurry and industrial waste can be used as substrate. Precomposting of the substrate is essential before inoculation of worms. Small stem pills, coir peats, coconut leaves, sugarcane trash, stem of crops, grasses or husk waste or discarded cattle feed can be used on the lowermost layer of peat as bedding material. Ysenia fitida, Eudrylas eugenia and Perionix excavates are the most popular earthworm species suitable for vermicomposting as they are excellent worms which are found effective in nutrient poor soils as well as in manure. 1500 number of worms per square meter are enough for efficient utilization of substrate. Covering of feed substrate is essential as it reduces moisture loss and saves worms from extra movements. Water management is most important criteria in vermiculture as worms require moisture for their survival. Composting and monitoring of the unit should continue for 30 days. When vermicompost and vermicasting are ready for collection, top layers appear somewhat dark brown, granular as if used dry tea leaves have been spread over the layers. Then watering should be stopped for 5 to 7 days and compost should be scrapped from top layers. Compost should then be left undisturbed for 6 to 24 hours. After collection of vermicompost from top layered, feed materials is again replenished and composting process is rescheduled. is air-dried in shade before packing in convenient size. Varmicompost provides almost all the essential nutrients required by the plants. It improves soil structure, aeration, water holding capacity and prevents soil erosion and nutrient losses. It also increases the use efficiency of chemical fertilizers and reduces incidence of pest and diseases in crops. It provides excellent effect on overall plant growth, encourages new shoots and leaves. Vermicompost being ideal nutrient supplement for organic cultivation has redefined the earthworms beneficial role in agriculture and earthworms have emerged as an efficient eco-friendly waste managers. 
# '''))

# print(get_facts(''''
#                 Hello friends, welcome all of you to Pathfinder. Today, we are going to research the twelfth class of Indian Agriculture. In the previous class of Zero Budget Natural Farming, we had seen Sustainable Agriculture and Organic Farming. So, we are taking the discussion forward. There is a possibility of this becoming a question in the exam. This is Zero Budget Natural Farming. 

# Before starting this class, let me tell you that whenever you come to the academy, use the code KC10 because when you use this code, it gives you my hand holding and mentorship. My name is Kinjal Choujari and you can connect with me on my Telegram channel, where after the lecture you will get PDF updates. 

# The term we will see today is sustainable agriculture. We had seen in the previous class that we had seen organic farming. We had seen different terms except organic farming. Today we are moving forward the discussion and we will discuss zero budget natural farming. 

# Zero budget natural farming is a type of organic farming. Both are different. What are the differences? Even that too the farmer does not have to buy anything, everything from the farm itself. If he gets it from the farm, then there is zero budget natural farming chemical free agriculture. The source of this information comes from traditional Indian practices. The agriculture that is traditionally done in India has been chemical free. Even today you see North East India, so largely chemical free agriculture is still being practiced there. 

# So basically if you see, there is a very famous agriculturalist of Maharashtra, Subhash Palekar ji, whose picture you can see here. The reason was that he had to give an alternative to the green revolution. The green revolution had spread very fast in India, but in the green revolution, chemical fertilizers, chemical pesticides, intensive irrigation in which ground water level depletion is taking place, then he saw all these problems and he said that all these inputs have become fertilizers, pesticides, the cost of electricity in drawing water, all these costs are becoming very high. The farmer takes a lot of loans from them. Then he buys them, then puts them in cultivation and if God forbid, but if the weather is not favorable, then the cultivation is ruined and what happens to the farmer? Indebtedness is increasing very fast in this way, suicides are taking place due to which there is an impact of other chemicals, the environment is getting worse, the fertility of long term soil is getting spoiled, and somewhere health is also harmed when we use chemical people and pesticides. 

# The knowledge that is there has been taken from our traditional agricultural practices, so the four pillars of Zero Budget Natural Farming are mentioned, so the first is the seed nectar, it is getting spoiled in a timpert way, it is committing suicide, due to which it is increasing, which is called Zero Budget Natural Farming. There is nothing new, somewhere its source, the knowledge that has been taken from our traditional agricultural practices, then the four pillars of Zero Budget Natural Farming are told, so the first is Seed Amrit, what is seed treatment in timpert words, cow dung and urine cow urine is used and seed is treated. 

# Secondly, if you see, soil treatment and organism is immortal, in which any fertilizer or no pesticide is used, no fertilizer, no pesticide is used, and if you see, animal dung, cow dung, cow urine, jaggery are used, other local materials are used, as a fertilizer. Apart from this, herbicide treatment and mulching is done, in which if you see, the soil is covered with crop and straw residue, which is the residue of the crop, which is husk, straws, it is covered with them, what is the cause, it leads to herbicide growth, and at the same time, if there is moisture in the soil, it is retained then dry land is very beneficial in agriculture, moisture remains in the soil, apart from this, which is called the fourth wheel, which is air infusion, then if you see in the soil in this way, then the efforts are made to build soil humus. And aeration is done in the soil so that the microbial activity in the soil can be accelerated. 

# Then friends, there are other things, in ZBNF, which you know, it is fine, but this much will be remembered, it has started from Maharashtra, apart from this four pillars, and apart from this, the difference has to be known. What is the difference between organic farming, ZBNF? If we look at the ZBNF, all the inputs are taken from the farm itself, apart from the animals in the farm, the animals and the cattle, if you look at the rest of the crop residue and straws, then there is no market pay dependency at every step. So you don't have to purchase anything from the market, if you look at organic farming, then high yielding variety seeds are taken, organic, similarly climate smart agriculture is also done, then according to the climate, seeds are purchased from the market, insecticides, organic insecticides, then they are purchased, bio-fertilizers etc. are also purchased. 

# Apart from this, whatever fertilizer you have to add, even if it becomes animal dung or urine, that too the farmer purchases from the market, and everyone gets organic certification, so somewhere the dependence on the market is very strong, input is also being purchased, only then the farmer can earn money from it and compensate for the input. So this is the difference, so there is a type of organic farming ZBNF, in which there is no dependence on the market, so this is what you have to know. 

# So you can see state wise, I will zoom in on the ground and show you, so 80 acres have been allotted in Aldi Haryana, 1000 acres have been allotted in Gurukhashetar, 1000 acres have been made in Punjab. 80 acres have been allotted in Haryana, Gurukhashetar, I will zoom in and show you, so 80 acres have been allotted in Aldi Haryana, 1000 acres have been allotted in Gurukhashetar, 1000 acres have been allotted in Punjab, in Himachal Pradesh, across the state, Natural Farming Efficient Farmers Scheme is being run, 1000 acres have been done in Punjab. In Himachal Pradesh, across the state, Natural Farming Efficient Farmers Scheme is being implemented, in 13 districts, in 5 lakh acres of land, ZBNF is being promoted, in Karnataka, in 10 agro-climatic zones, for this a very important discussion was held, ZBNF will know very well, all these things that I told you, remember this much, your work will be done. 

# Then friend I would like to say that, in the academy, we are running the ultimate prelims and CSAT test series, so you can see, this is a test series, you can see, there are 28 tests, in which 20 GS and 8 CSAT tests are there, 3149 are for Rs. 3149, while if you take 56 tests for 12 months, it was for 6 months only, there are 56 tests for 12 months, 40 GS, 16 CSAT, its price is 4409 rupees, this is when you use KC10 code, so remember that you are getting this 10% off from KC10 code, apart from this there are many test series features, it has trackers, indicators, how you are performing, personalized report is being made yours, multiple times you can attempt the test, apart from this we are also running new combo week, flat 22% off, with combo and 10% with educator's code, KC10 you are getting, price of 18 months plus combo 3898 rupees, 18 months iconic combo, 76176 rupees, iconic subscription, one to one live mentorship, main question answer practice, study planner, and you can also speak in open house, apart from this, CSE, combat, CSAT special are doing, take advantage, plus subscription has one year price, 46791 rupees, one year iconic price, 67041 rupees, this is all the key, when you use KC10 code, the incoming code, which also gives you guidance and mentorship, Indi, English, by Lingwal, there are different batches of one year, two years, then definitely take advantage of them, you can see the mission 2 year batch on the screen. 

# Thank you so much for joining, have a great day.

#                 '''))