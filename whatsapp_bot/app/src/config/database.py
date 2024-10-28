from pymongo import MongoClient
from datetime import datetime
from app.src.config.config import settings
from app.src.models.user_details import UserDetail

# Check if MongoDb collection exists, create it if it doesn't
def check_mongo_db_collections():
    """
    Checks if the MongoDB collection exists, and creates it if it doesn't.
    """
    # Create a MongoClient instance
    client = MongoClient(settings.DATABASE_URL)
    # print('Connected to MongoDB...')
    
    mongo_db = client[settings.MONGO_DB_NAME]
    
    if settings.MONGO_DB_USER_COLLECTION not in mongo_db.list_collection_names():
        mongo_db.create_collection(settings.MONGO_DB_USER_COLLECTION)
        print(f"Collection '{settings.MONGO_DB_USER_COLLECTION}' created successfully.")
    else:
        print(f"Collection '{settings.MONGO_DB_USER_COLLECTION}' already exists.")
        
    if settings.MONGO_DB_CONVERSATION_COLLECTION not in mongo_db.list_collection_names():
        mongo_db.create_collection(settings.MONGO_DB_CONVERSATION_COLLECTION)
        print(f"Collection '{settings.MONGO_DB_CONVERSATION_COLLECTION}' created successfully.")
    else:
        print(f"Collection '{settings.MONGO_DB_CONVERSATION_COLLECTION}' already exists.")

def get_mongo_db_user_collection():
    """
    Establishes a connection to MongoDB and returns the collection instance.

    Returns:
    - collection
    """
    # Create a MongoClient instance
    client = MongoClient(settings.DATABASE_URL)
    # print('Connected to MongoDB...')
    
    mongo_db = client[settings.MONGO_DB_NAME]
    collection = mongo_db[settings.MONGO_DB_USER_COLLECTION]

    return collection

def get_mongo_db_conversation_collection():
    """
    Establishes a connection to MongoDB and returns the collection instance.

    Returns:
    - collection
    """
    # Create a MongoClient instance
    client = MongoClient(settings.DATABASE_URL)
    # print('Connected to MongoDB...')
    
    mongo_db = client[settings.MONGO_DB_NAME]
    collection = mongo_db[settings.MONGO_DB_CONVERSATION_COLLECTION]

    return collection

def store_user_conversation(mobile,language,name,gender,location,question_format,question,answer):
    """
    Stores user conversation to MongoDB.

    Args:
    - mobile (str): User's mobile number. Defaults to None.
    - language (str): User's preferred language. Defaults to None.
    - name (str): User's name. Defaults to None.
    - gender (str): User's gender. Defaults to None.
    - location (str): User's location. Defaults to None.
    - question_format (str): Format of the question.
    - question (str): User's question. Defaults to None.
    - answer (str): User's answer to the question. Defaults to None.

    Returns:
    - dict: A dictionary indicating the success status and a message.
    """

    # Get the current UTC datetime
    current_datetime = datetime.utcnow()

    # Format the datetime object as a string with your desired format
    formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Create a dictionary representing the QuestionAnswer
    question_answer_dict = {"question_format": question_format,"question": question, "answer": answer, "timestamp": formatted_date}

    collection_name = get_mongo_db_user_collection()

    existing_user = collection_name.find_one({"mobile": mobile})
    # existing_user_gender = collection_name.find_one({"mobile": mobile,"gender":gender})

    if existing_user:
        # Preserve the existing created_at value
        created_at = existing_user.get("created_at")
    else:
        # Get the current UTC datetime if the user doesn't exist
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Create a UserDetail instance
    user_detail_data = {
        "mobile": mobile,
        "language": language,
        "name": name,
        "gender": gender,
        "location": location,
        "created_at": created_at,
        "questions_answers": [question_answer_dict] if question else []
    }

    user_detail = UserDetail(**user_detail_data)

    if existing_user:
        # Update existing user details
        updated_data  = {field: value for field, value in user_detail.dict().items() if value is not None}
        collection_name.update_one({"mobile": user_detail.mobile}, {"$set": updated_data})
        if question:
            # Append new question-answer pair to existing user's questions_answers list
            existing_user["questions_answers"].append(question_answer_dict)
            collection_name.update_one({"mobile": user_detail.mobile},{"$set": {"questions_answers": existing_user["questions_answers"]}})
    else:
        # Insert new user details
        collection_name.insert_one(user_detail.dict())

    return {"success": True, "message": "User conversation updated successfully"}

def store_conversation(mobile, 
                       chat_id, 
                       language, 
                       question_format, 
                       question, 
                       answer, 
                       question_en=None, 
                       answer_en=None,
                       answer_status=False,
                       answer_audio_status=False, 
                       location=None, 
                       context=None):
    
    current_datetime = datetime.utcnow()
    formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    conversation_data = {
        "mobile": mobile,
        "chat_id": chat_id,
        "language": language,
        "question_format": question_format,
        "question": question,
        "question_en": question_en,
        "answer": answer,
        "answer_en": answer_en,
        "answer_status": answer_status,
        "answer_audio_status": answer_audio_status,
        "location": location,
        "context": context,
        "timestamp": datetime.utcnow()
    }
    
    collection = get_mongo_db_conversation_collection()
    collection.insert_one(conversation_data)
    
    return {"success": True, "message": "Conversation stored successfully"}

def update_conversation(chat_id, **kwargs):
    collection = get_mongo_db_conversation_collection()
    update_fields = {key: value for key, value in kwargs.items() if value is not None}
    collection.update_one({"chat_id": chat_id}, {"$set": update_fields})

def get_last_conversation(mobile):
    collection = get_mongo_db_conversation_collection()
    last_conversation = collection.find({"mobile": mobile}).sort("timestamp", -1).limit(1)
    last_conversation_list = list(last_conversation)  # Convert cursor to list
    return last_conversation_list[0] if last_conversation_list else None

def get_conversation_by_chat_id(chat_id):
    collection = get_mongo_db_conversation_collection()
    conversation = collection.find_one({"chat_id": chat_id})
    return conversation
        
def get_user_details(mobile):
    """
    Retrieves user details from MongoDB.

    Args:
    - mobile (str): User's mobile number.

    Returns:
    - dict: A dictionary containing the user details.
    """
    collection = get_mongo_db_user_collection()
    user_details = collection.find_one({"mobile": mobile})
    
    return user_details

def get_collection_details(mobile):
    collection = get_mongo_db_conversation_collection()
    user_conversation_details = collection.find_one({"mobile":mobile})

    return user_conversation_details

def create_or_fetch_user(mobile):
    collection = get_mongo_db_user_collection()
    existing_user = collection.find_one({"mobile": mobile})

    if existing_user:
        return existing_user
    else:
        user_detail_data = {
            "mobile": mobile,
            "name": None,
            "language": None,
            "gender": None,
            "location": None,
            "consent": False,
            "onboarded": False,
            "created_at": datetime.utcnow(),
        }
        collection.insert_one(user_detail_data)
        return user_detail_data