import random

class RandomEmotionMsg():
    random_action: str
    random_emote: str
    random_words: str

    def __init__(self, words: str, emote: str, action: str) -> None:
        self.random_words = words
        self.random_emote = emote
        self.random_action = action

    def to_dict(self):
        return {
            "words": self.random_words,
            "emote": self.random_emote,
            "action": self.random_action,
        }


class RandomEmotion():
    '''闲置动作控制管理'''
    idle_words: []
    idle_emote: []
    idle_action: []

    def __init__(self) -> None:
        # FIXME 改成从数据库查询当前有启用的动作列表
        self.idle_words = ["五个拉格朗日点都有两个点是稳定的，我的拉格朗日稳定点在哪里？", "半人马座的比邻星是距太阳系最近的一颗恒星，马斯克说要带我去那里。", "真头痛，天下什么时候才能掉老婆"]
        self.idle_action = ["跳舞-科目三","跳舞-伦巴", "生气", "兴奋", "思考", "talking_01", "idle_happy_01", "quick-bow", "idle-female", "idle-female2", "idle-male"]
        self.idle_emote = ["happy", "excited", "neutral", "angry", "sad", "relaxed", "surprised"]

    def random_action(self) -> RandomEmotionMsg:
        random_words = random.choice(self.idle_words)
        random_idle_action = random.choice(self.idle_action)
        random_emote = random.choice(self.idle_emote)

        return RandomEmotionMsg(random_words, random_emote,random_idle_action)
    



