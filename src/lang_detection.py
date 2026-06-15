from lingua import Language, LanguageDetectorBuilder

class Detectlanguage (Language: Lang):
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_languages(
            Lang
            
        ).build()

    def is_english(text: str) -> bool:
        return detector.detect_language_of(text) == Language.ENGLISH

if text.len() > 50:
    prediction = is_english("test, this is the english language")
    print(prediction)