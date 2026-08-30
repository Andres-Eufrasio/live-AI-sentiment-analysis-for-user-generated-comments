from lingua import Language, LanguageDetectorBuilder

"""
Notes
add langauge swiching
"""

class DetectLanguage:
    def __init__(self):
        self.detector = LanguageDetectorBuilder.from_languages(
            Language.ENGLISH
        ).build()

    def is_english(self, text: str) -> bool:
        detected = self.detector.detect_language_of(text)
        return detected == Language.ENGLISH

    def detect_english(self, text):
        if len(text) > 35:
            prediction = self.is_english(text)
            return True
        else:
            return False

detector = DetectLanguage()



if __name__ == "__main__":
    text = "test, this is the english language"
