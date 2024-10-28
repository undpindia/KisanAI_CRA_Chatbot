from pydantic import BaseModel
from typing import List
from typing import Optional

class QuestionAnswer(BaseModel):
    """
    Pydantic BaseModel for representing a question-answer pair.
    
    Attributes:
    - question_format (str): The format in which the question was asked (e.g., "text", "audio").
    - question (str): The question asked.
    - answer (str): The answer provided.
    - timestamp (str): Timestamp indicating when the question was answered. Defaults to None.
    """

    question_format: str = None
    question: str = None
    answer: str = None
    timestamp: str = None

class UserDetail(BaseModel):
    """
    Pydantic BaseModel for representing user details.

    Attributes:
    - mobile (str): User's mobile number.
    - language (str, optional): User's preferred language. Defaults to None.
    - name (str, optional): User's name. Defaults to None.
    - location (str, optional): User's location. Defaults to None.
    - gender (str, optional): User's gender. Defaults to None.
    - created_at (str, optional): Timestamp indicating the creation time of the user details. Defaults to None.
    - questions_answers (List[QuestionAnswer]): List of QuestionAnswer objects associated with the user.
      Defaults to None.
    """
    
    mobile: str
    language: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    consent: Optional[bool] = None
    onboarded: Optional[bool] = None
    created_at: str = None
    
class UserConversation(BaseModel):
  """
  Pydantic BaseModel for representing user conversation details.

  Attributes:
  - mobile (str): User's mobile number.
  - chat_id (str): Chat ID of the conversation.
  - question_format (str): Format of the question.
  - question (str): User's question.
  - question_en (str): User's question in English.
  - answer (str): User's answer to the question.
  - answer_en (str): User's answer in English.
  - context (str): Context of the conversation.
  - timestamp (str): Timestamp indicating when the question was answered.
  """
  
  mobile: str
  chat_id: str
  question_format: Optional[str] = None
  question: Optional[str] = None
  question_en: Optional[str] = None
  answer: Optional[str] = None
  answer_en: Optional[str] = None
  location: Optional[str] = None
  context: Optional[str] = None
  timestamp: str = None
