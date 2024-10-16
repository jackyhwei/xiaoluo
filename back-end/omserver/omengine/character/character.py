
class Character(): 
    '''统一自定义角色定义数据结构

    role_name: 角色名称
    persona: 角色基本信息定义
    personality: 角色的性格简短描述
    scenario: 角色的对话的情况和背景
    examples_of_dialogue: 角色的对话样例

    '''
    role_id: int
    role_name: str
    gender: int
    avatar: str
    persona: str
    personality: str
    scenario: str
    examples_of_dialogue: str
    custom_role_template_type: str
    model_id: str
    scene_id: str
    voice_id: str
    user_id: str

    def __init__(self, role_id:int, role_name: str, gender: int, avatar: str, persona: str, personality: str, scenario: str, examples_of_dialogue, custom_role_template_type: str, model_id: str, scene_id: str, voice_id: str, user_id: str) -> None:
        self.role_id = role_id
        self.role_name = role_name
        self.gender = gender
        self.avatar = avatar
        self.persona = persona
        self.personality = personality
        self.scenario = scenario
        self.examples_of_dialogue = examples_of_dialogue
        self.custom_role_template_type = custom_role_template_type
        self.model_id = model_id
        self.scene_id = scene_id
        self.voice_id = voice_id
        self.user_id = user_id

    def to_dict(self):
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "gender": self.gender,
            "avatar": self.avatar,
            "persona": self.persona,
            "personality": self.personality,
            "scenario": self.scenario,
            "examples_of_dialogue": self.examples_of_dialogue,
            "custom_role_template_type": self.custom_role_template_type,
            "model_id": self.model_id,
            "scene_id": self.scene_id,
            "voice_id": self.voice_id,
            "user_id": self.user_id
        }
