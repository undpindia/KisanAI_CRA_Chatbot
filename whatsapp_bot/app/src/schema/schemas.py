def user_serial_entity(userdetail) -> dict:
    """
    Serializes a single user details into a dictionary.

    Args:
        userdetail (dict): The user details.

    Returns:
        dict: Serialized user details.
    """
    return{
        "id": str(userdetail["_id"]),
        "mobile": userdetail["mobile"],
        "language": userdetail["language"],
        "name": userdetail["name"],
        "location": userdetail["location"],
        "gender": userdetail["gender"],
        "onboarded": userdetail["onboarded"],
        "created_at": userdetail["created_at"],
        "question_answers": [
            {
            "question_format" : qa["question_format"],
            "question" : qa["question"],
            "answer" : qa["answer"],
            "timestamp" : qa["timestamp"]
            }
            for qa in userdetail.get("questions_answers", [])
        ]
    }

def user_serial_list_entity(userdetails) -> list:
    """
    Serializes a list of user details into a list of dictionaries.

    Args:
        userdetails (list): List of user details.

    Returns:
        list: List of serialized user details.
    """
    return [user_serial_entity(userdetail) for userdetail in userdetails]

def user_conversation_serial_entity(userconversationdetail) -> dict:
    """
    Serializes a single user conversation details into a dictionary.

    Args:
        userconversationdetail (dict): The user conversation details.

    Returns:
        dict: Serialized user conversation details.
    """

    return{
        "chat_id": str(userconversationdetail["chat_id"]),
        "mobile": userconversationdetail["mobile"],
        "question_format": userconversationdetail["question_format"],
        "question": userconversationdetail["question"],
        "question_en": userconversationdetail["question_en"],
        "answer": userconversationdetail["answer"],
        "answer_en": userconversationdetail["answer_en"],
        "location": userconversationdetail["location"],
        "context": userconversationdetail["context"],
    }

def user_conversation_serial_list_entity(userconversationdetails) -> list:
    """
    Serializes a list of user conversation details into a list of dictionaries.

    Args:
        userconversationdetails (list): List of user conversation details.

    Returns:
        list: List of serialized user conversation details.
    """
    return [user_conversation_serial_entity(userconversationdetail) for userconversationdetail in userconversationdetails]