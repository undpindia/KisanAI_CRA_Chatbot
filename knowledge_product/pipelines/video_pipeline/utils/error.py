

class Incorrect_lang_detect(Exception):
    """Raised when whisper is unable to detect a language"""
    
    def __init__(self, lang):
        self.lang= lang
        
    def __str__(self):
        return f"Invalid age. Got {self.lang}."