
from langdetect import detect_langs


def language_detection(text):
   
    
    try:
        result = detect_langs(text)
    except:
        return {'na': 0}
    
    lang, score = str(result[0]).split(':')
    
    return {lang:score}
    