from fastapi import APIRouter
from fastapi import HTTPException
from bson import ObjectId
from app.src.models.user_details import UserDetail
from app.src.config.database import get_mongo_db_user_collection
from app.src.schema.schemas import user_serial_list_entity

# Create an instance of APIRouter
router = APIRouter()

# Endpoint for getting user count
@router.get("/user_count") 
async def get_user_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of users for each date
    user_count = {}
    for user in user_details:
        user_created_at = user["created_at"].split()[0]
        print(user_created_at)
        if user_created_at in user_count:
            user_count[user_created_at] += 1
        else:
            user_count[user_created_at] = 1
    return user_count

# Endpoint to fetch user chat history
@router.get("/user/details")
async def fetch_user_details():
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())
    return user_details

# Endpoint for getting language count
@router.get("/user/language_count") 
async def get_language_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of users for each language
    language_count = {}
    for user in user_details:
        language = user["language"]
        if language in language_count:
            language_count[language] += 1
        else:
            language_count[language] = 1
    return language_count

# Endpoint for getting location count
@router.get("/user/location_count") 
async def get_location_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of users for each location
    location_count = {}
    for user in user_details:
        location = user["location"]
        if location in location_count:
            location_count[location] += 1
        else:
            location_count[location] = 1
    return location_count

# Endpoint for getting gender count
@router.get("/user/gender_count") 
async def get_gender_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of users for each gender
    gender_count = {}
    for user in user_details:
        gender = user["gender"]
        if gender in gender_count:
            gender_count[gender] += 1
        else:
            gender_count[gender] = 1
    return gender_count

# Endpoint for getting user question input count
@router.get("/user/question/input_count") 
async def get_user_question_input_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of question inputs for each users
    input_count = {}

    # Iterate over each entry in user_details
    for user in user_details:
        question_answers = user["question_answers"]
        
        # Iterate over each question-answer pair
        for qa in question_answers:
            question_format = qa['question_format']

            if question_format in input_count:
                input_count[question_format] += 1
            else:
                input_count[question_format] = 1

    return input_count

# Endpoint for getting user question conversation count
@router.get("/user/question/conversation_count") 
async def get_conversation_count():
    # User detais
    user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

    # Count the number of user's conversation count
    conversation_count = {}

    # Iterate over each entry in user_details
    for user in user_details:
        question_answers = user["question_answers"]

        # Iterate over each question-answer pair
        for qa in question_answers:
            timestamp = qa['timestamp'].split()[0]

            if timestamp in conversation_count:
                conversation_count[timestamp] += 1
            else:
                conversation_count[timestamp] = 1

    return conversation_count

# Endpoint to delete user by ID
@router.delete("/user/delete/{id}")
async def delete_user(id: str):
    # Find and delete the record with the specified ObjectId
    get_mongo_db_user_collection().find_one_and_delete({"_id": ObjectId(id)})
    return "Record delete successfully"