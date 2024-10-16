from easygoogletranslate import EasyGoogleTranslate


class Translator_Google():

    @staticmethod
    def translate(text: str, target_language: str, source_language: str):
        translator = EasyGoogleTranslate(
            source_language='en',
            target_language='de',
            timeout=10
        )
        result = translator.translate('This is an example.')

        print(result) 
        # Output: Dies ist ein Beispiel.
