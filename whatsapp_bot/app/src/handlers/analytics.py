import json
from app.src.config.database import get_mongo_db_user_collection,get_mongo_db_conversation_collection
from app.src.schema.schemas import user_serial_list_entity,user_conversation_serial_list_entity
from datetime import datetime,timedelta
from whatsapp_bot.app.logs.logger import logger

def user_analytics():
    """
    Get user analytics data.

    Returns:
    - user_count (dict): User count by date.
    - user_count_weeekly (dict): User count by weekly
    - onboarded_user_count (dict): Onboarded user count by date.
    - language_count (dict): User count by language.
    - location_count (dict): User count by location.
    - gender_count (dict): User count by gender.
    - question_format_count (dict): Question format count
    """
    
    try:
        user_details = user_serial_list_entity(get_mongo_db_user_collection().find())

        user_conversation_details = user_conversation_serial_list_entity(get_mongo_db_conversation_collection().find())

        # Prepare data for charts
        user_count = {}
        onboarded_user_count = {}
        language_count = {}
        location_count = {}
        user_count_weekly = {}
        user_onboared_count_weekly = {}
        question_format_count = {}
        gender_count = {"male": 0, "female": 0, "others": 0}
        
        gender_mapping = {
            "male": ["male", "पुरुष"],
            "female": ["female", "महिला"],
            "others": ["others", "अन्य", "इतर"]
        }
        
        def normalize_gender(gender):
            for key, values in gender_mapping.items():
                if gender.lower() in values:
                    return key
            return "others"  # Default to "others" if no match is found
        
        def parse_datetime(date_value):
            if isinstance(date_value, str):
                try:
                    return datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    # If microseconds are not present in the string
                    return datetime.strptime(date_value, "%Y-%m-%d %H:%M:%S")
            elif isinstance(date_value, datetime):
                return date_value
            else:
                raise ValueError(f"Unsupported date format: {date_value}")

        # Fetching detais from user_details
        for user in user_details:
            # ==============================
            # Section for Datetime Conversion
            # ==============================

            user_created_at = user["created_at"]
            created_at_dt = parse_datetime(user_created_at)
            user_created_at = created_at_dt.strftime("%Y-%m-%d")

            user_count[user_created_at] = user_count.get(user_created_at, 0) + 1

            # ==============================
            # Section for Weekly Calculation
            # ==============================

            user_created_weekly = user["created_at"]
            created_weekly = parse_datetime(user_created_weekly)

            # Calculate the start of the 7-day range
            start_of_range = created_weekly - timedelta(days=created_weekly.weekday() % 7)
            end_of_range = start_of_range + timedelta(days=6)
            
            # Ensure the end date does not exceed the current date
            current_date = datetime.now()
            if end_of_range > current_date:
                end_of_range = current_date

            # Format the start and end dates as strings (e.g., January-01)
            start_of_range_str = start_of_range.strftime("%B-%d")
            end_of_range_str = end_of_range.strftime("%B-%d")

            # Create a string key for the range (e.g., January-01 to January-07)
            range_key = f"{start_of_range_str} to {end_of_range_str}"

            user_count_weekly[range_key] = user_count_weekly.get(range_key, 0) + 1

            if user.get("onboarded"):
                onboarded_user_count[user_created_weekly] = onboarded_user_count.get(user_created_weekly, 0) + 1
                
                # Convert the string to a datetime object
                created_weekly = parse_datetime(user_created_weekly)

                # Calculate the start of the 7-day range
                start_of_range = created_weekly - timedelta(days=created_weekly.weekday() % 7)
                end_of_range = start_of_range + timedelta(days=6)

                # Ensure the end date does not exceed the current date
                current_date = datetime.now()
                if end_of_range > current_date:
                    end_of_range = current_date

                start_of_range_str = start_of_range.strftime("%B-%d")
                end_of_range_str = end_of_range.strftime("%B-%d")

                # Create a string key for the range
                range_key = f"{start_of_range_str} to {end_of_range_str}"

                # Increment the count for the range
                user_onboared_count_weekly[range_key] = user_onboared_count_weekly.get(range_key, 0) + 1

                # Language count
                language = user["language"]
                language_count[language] = language_count.get(language, 0) + 1

                # Location count
                location = user["location"]
                location_count[location] = location_count.get(location, 0) + 1

                # Gender count
                gender = normalize_gender(user["gender"])
                gender_count[gender] = gender_count.get(gender, 0) + 1

        # Sort the user count
        sorted_user_count_list = sorted(user_count.items())

        # Convert the sorted list of tuples back to a dictionary
        sorted_user_count = dict(sorted_user_count_list)

        # Fetching details from UserConversation Model
        for user_conversation in user_conversation_details:
            question_format = user_conversation["question_format"]
            question_format_count[question_format] = question_format_count.get(question_format, 0) + 1

        return {
            "user_count": json.dumps(sorted_user_count),
            "user_count_weekly": json.dumps(user_count_weekly),
            "onboarded_user_count": json.dumps(user_onboared_count_weekly),
            "language_count": json.dumps(language_count),
            "location_count": json.dumps(location_count),
            "gender_count": json.dumps(gender_count),
            "question_format_count": json.dumps(question_format_count),
        }
    except Exception as e:
        logger.error(f"Error in user analytics: {str(e)}")
        return {}