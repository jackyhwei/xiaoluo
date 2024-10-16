import requests
import os
import json
from .AuthV3Util import addAuthParams

# 您的应用ID
APP_KEY = os.getenv("YOUDAO_APP_KEY")
# 您的应用密钥
APP_SECRET = os.getenv("YOUDAO_SECRET_KEY")

class Translator_Youdao:

    @staticmethod
    def translation(self, text: str, target_language: str, source_language: str) -> str:
        q = text
        lang_from = source_language     # 'zh-CHS'
        lang_to = target_language       # 'ja'
        data = {'q': q, 'from': lang_from, 'to': lang_to}
        addAuthParams(APP_KEY, APP_SECRET, data)
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        res = requests.post('https://openapi.youdao.com/api', data, header)
        content = str(res.content, 'utf-8')
        return json.loads(content)