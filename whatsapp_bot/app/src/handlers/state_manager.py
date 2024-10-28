from datetime import datetime
from app.src.config.database import get_mongo_db_user_collection


class AppState:
    """
    Manages application state and user data persistence for the WhatsApp CRA assistant.
    
    This class handles user state tracking, database operations, and state management
    throughout the user's interaction with the system. It maintains various flags and
    properties for tracking the progress of onboarding, user preferences, and conversation
    state.

    Attributes:
        mobile (str): User's mobile number
        display_phone_number (str): Formatted display phone number
        onboarded (bool): Flag indicating if user has completed onboarding
        name (str): User's name
        location (str): User's location
        gender (str): User's gender
        consent (bool): User's consent status
        language (str): User's preferred language
        onboarding_video_sent (bool): Track if onboarding video was sent
        onboarding_audio_sent (bool): Track if onboarding audio was sent
        language_selection_sent (bool): Track if language selection was sent
        language_selection_received (bool): Track if language selection was received
        language_confirmation_sent (bool): Track if language confirmation was sent
        language_confirmation_received (bool): Track if language confirmation was received
        language_confirmed (bool): Track if language was confirmed
        consent_sent (bool): Track if consent request was sent
        consent_received (bool): Track if consent response was received
        consent_rejected (bool): Track if consent was rejected
        name_confirmation_sent (bool): Track if name confirmation was sent
        name_confirmation_received (bool): Track if name confirmation was received
        name_confirmed (bool): Track if name was confirmed
        gender_selection_sent (bool): Track if gender selection was sent
        gender_selection_received (bool): Track if gender selection was received
        gender_confirmation_sent (bool): Track if gender confirmation was sent
        gender_confirmation_received (bool): Track if gender confirmation was received
        gender_confirmed (bool): Track if gender was confirmed
        location_confirmation_sent (bool): Track if location confirmation was sent
        location_confirmation_received (bool): Track if location confirmation was received
        location_confirmed (bool): Track if location was confirmed
        selected_language (list): List of selected languages
        confirmation_button_sent_status (list): Track confirmation button send status
        confirmation_button_delivery_status (list): Track confirmation button delivery status
        confirmed_language (str): Final confirmed language
        confirmation_question (str): Current confirmation question
        user_name_text (str): User's name in text form
        user_location_text (str): User's location in text form
        user_gender_text (str): User's gender in text form
        user_consent (bool): User's consent status
        user_name_audio_transcription (str): Transcribed audio of user's name
        user_location_audio_transcription (str): Transcribed audio of user's location
        user_gender_audio_transcription (str): Transcribed audio of user's gender
        user_question_audio_transcription (str): Transcribed audio of user's question
        last_sent_message (list): List of last sent messages
        counter (dict): Counter for tracking various events
        temp_question_audio (list): Temporary storage for question audio
    """

    def __init__(self):
        self.mobile = None
        self.display_phone_number = None
        self.onboarded = False
        self.name = None
        self.location = None
        self.gender = None
        self.consent = False
        self.language = None
        self.onboarding_video_sent = False
        self.onboarding_audio_sent = False
        self.language_selection_sent = False
        self.language_selection_received = False
        self.language_confirmation_sent = False
        self.language_confirmation_received = False
        self.language_confirmed = False
        self.consent_sent = False
        self.consent_received = False
        self.consent_rejected = False
        self.name_confirmation_sent = False
        self.name_confirmation_received = False
        self.name_confirmed = False
        self.gender_selection_sent = False
        self.gender_selection_received = False
        self.gender_confirmation_sent = False
        self.gender_confirmation_received = False
        self.gender_confirmed = False
        self.location_confirmation_sent = False
        self.location_confirmation_received = False
        self.location_confirmed = False
        self.selected_language = []
        self.confirmation_button_sent_status = []
        self.confirmation_button_delivery_status = []
        self.confirmed_language = None
        self.confirmation_question = None
        self.user_name_text = None
        self.user_location_text = None
        self.user_gender_text = None
        self.user_consent = None
        self.user_name_audio_transcription = None
        self.user_location_audio_transcription = None
        self.user_gender_audio_transcription = None
        self.user_question_audio_transcription = None
        self.last_sent_message = []
        self.counter = {}
        self.temp_question_audio = []
    
    def values(self):
        for attr, value in self.__dict__.items():
            print(f"{attr}: {value}")
            
    # create or fetch user from mongodb based on mobile number
    def create_or_fetch_user(self):
        """
        Creates a new user or fetches existing user data from MongoDB.
        
        If user exists, updates the current state with stored values.
        If user is new, creates a new document with basic user details.
        """
        collection = get_mongo_db_user_collection()
        existing_user = collection.find_one({"mobile": self.mobile})
        if existing_user:
            # update state from user details, use every fetched field and update state
            for key, value in existing_user.items():
                setattr(self, key, value)
        else:
            self.created_at = datetime.utcnow()
            
            user_detail_data = {
                "mobile": self.mobile,
                "created_at": self.created_at,
            }
            collection.insert_one(user_detail_data)
                
    def update_state_from_user(self, user_details):
        """
        Updates the current state with provided user details.
        
        Args:
            user_details (dict): Dictionary containing user information to update
                               including mobile, name, location, gender, consent,
                               onboarded status, and language preferences.
        """
        if user_details.get("mobile") is not None:
            self.mobile = user_details.get("mobile")
        if user_details.get("name") is not None:
            self.user_name_text = user_details.get("name")
        if user_details.get("location") is not None:
            self.user_location_text = user_details.get("location")
        if user_details.get("gender") is not None:
            self.user_gender_text = user_details.get("gender")
        if user_details.get("consent") is not None:
            self.user_consent = user_details.get("consent")
        if user_details.get("onboarded") is not None:
            self.onboarded = user_details.get("onboarded")
        if user_details.get("language") is not None:
            self.confirmed_language = user_details.get("language")
            
    # save state to mongodb based on user_details
    def save(self):
        """
        Saves the current state to MongoDB.
        
        Converts all instance attributes to a dictionary and updates or creates
        a new document in the database based on the mobile number.
        """
        collection = get_mongo_db_user_collection()
        existing_user = collection.find_one({"mobile": self.mobile})

        # Convert instance attributes to a dictionary
        updated_data = {field: value for field, value in self.__dict__.items()}

        if existing_user:
            # Update existing user details
            collection.update_one({"mobile": self.mobile}, {"$set": updated_data})
        else:
            # Insert new user details
            collection.insert_one(updated_data)
    
    def reset(self, mobile):
        """
        Resets all state attributes to their default values.
        
        Args:
            mobile (str): Mobile number to maintain for the reset state
        """
        self.mobile = mobile
        self.onboarded = False
        self.name = None
        self.location = None
        self.gender = None
        self.consent = False
        self.language = None
        self.onboarding_video_sent = False
        self.onboarding_audio_sent = False
        self.language_selection_sent = False
        self.language_selection_received = False
        self.language_confirmation_sent = False
        self.language_confirmation_received = False
        self.language_confirmed = False
        self.consent_sent = False
        self.consent_received = False
        self.consent_rejected = False
        self.name_confirmation_sent = False
        self.name_confirmation_received = False
        self.name_confirmed = False
        self.gender_selection_sent = False
        self.gender_selection_received = False
        self.gender_confirmation_sent = False
        self.gender_confirmation_received = False
        self.gender_confirmed = False
        self.location_confirmation_sent = False
        self.location_confirmation_received = False
        self.location_confirmed = False
        self.selected_language = []
        self.confirmation_button_sent_status = []
        self.confirmation_button_delivery_status = []
        self.confirmed_language = None
        self.confirmation_question = None
        self.user_name_text = None
        self.user_location_text = None
        self.user_gender_text = None
        self.user_consent = None
        self.user_name_audio_transcription = None
        self.user_location_audio_transcription = None
        self.user_gender_audio_transcription = None
        self.user_question_audio_transcription = None
        self.last_sent_message = []
        self.counter = {}
        self.temp_question_audio = []
        
    
    def save_state(self):
        """
        Saves essential user details to MongoDB.
        
        Saves a subset of state attributes including mobile, language, name,
        gender, location, consent, and onboarding status.
        """
        user_detail_data = {
            "mobile": self.mobile,
            "language": self.confirmed_language,
            "name": self.user_name_text,
            "gender": self.user_gender_text,
            "location": self.user_location_text,
            "created_at": datetime.utcnow(),  # Ensure created_at is set
            "consent": self.user_consent,
            "onboarded": self.onboarded
        }

        collection = get_mongo_db_user_collection()
        existing_user = collection.find_one({"mobile": self.mobile})

        if existing_user:
            # Update existing user details
            updated_data = {field: value for field, value in user_detail_data.items() if value is not None}
            collection.update_one({"mobile": self.mobile}, {"$set": updated_data})
        else:
            # Insert new user details
            collection.insert_one(user_detail_data)
    
    # fetch data from mongodb based on mobile number and update state
    def fetch_state(self, mobile):
        """
        Fetches user state from MongoDB based on mobile number.
        
        Args:
            mobile (str): Mobile number to fetch state for
            
        Updates current state with fetched values if user exists.
        """
        collection = get_mongo_db_user_collection()
        user_details = collection.find_one({"mobile": mobile})
        if user_details:
            self.update_state_from_user(user_details)
        else:
            print("User not found")   
