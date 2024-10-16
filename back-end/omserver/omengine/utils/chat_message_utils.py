
import re

def format_chat_text(role_name: str, your_name: str, text: str):
    # 去除特殊字符 * 、`role_name：`、`your_name:`
    # text = text.replace(f'*', "")
    pattern = r'\*.*?\*'
    text = text.replace(f'`', "")
    text = re.sub(pattern, '', text)
    text = text.replace(f'{role_name}：', "")
    text = text.replace(f'{your_name}：', "")
    text = text.replace(f'{role_name}:', "")
    text = text.replace(f'{your_name}:', "")
    text = text.replace(f'AI角色：', "")
    text = text.replace(f'AI（{role_name}）：', "")
    text = text.replace(f'AI:', "")
    text = text.replace(f'ai：', "")
    text = text.replace(f'Ai：', "")
    text = text.replace(f'{role_name}说：', "")     # FIXME jacky：未被正常替换，为什么？
    text = text.replace('[', "")
    text = text.replace(']', "")
    return text

def format_user_chat_text(text: str):
    text = text.replace('[', "")
    text = text.replace(']', "")
    return text