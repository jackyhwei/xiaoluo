from rest_framework import serializers

from .model.model_character import CharacterRoleModel, CharacterModelModel, CharacterActionModel, CharacterEmotionModel
from .model.model import BackgroundImageModel
from .model.model_asr import AsrHotwordsModel, AsrSensitivewordsModel, AsrRecordsModel
from .model.model_tts import TtsVoiceIdModel, TtsVoiceCloneModel, TtsRecordsModel
from .model.model_llm import LlmPromptModel
from .model.model_schedule import SchedulesModel

#######################
# Background image
#######################
class BackgroundImageSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(required=False)
    class Meta:
        model = BackgroundImageModel
        fields = '__all__'

#######################
# Character
#######################
class CharacterRoleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(required=True)
    class Meta:
        model = CharacterRoleModel
        fields = '__all__'

class CharacterEmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterEmotionModel
        fields = '__all__'

class CharacterActionSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(required=False)
    class Meta:
        model = CharacterActionModel
        fields = '__all__'

class CharacterModelSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(required=False)
    vrm_type = serializers.CharField(required=False)
    class Meta:
        model = CharacterModelModel
        fields = '__all__'

#######################
# LLM
#######################
class LlmPromptSerializer(serializers.ModelSerializer):
    prompt_name = serializers.CharField(required=True)
    class Meta:
        model = LlmPromptModel
        fields = '__all__'

# class ChatlogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ChatlogModel
#         fields = '__all__'

#######################
# ASR
#######################
class AsrHotwordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsrHotwordsModel
        fields = '__all__'

class AsrSensitivewordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsrSensitivewordsModel
        fields = '__all__'


#######################
# TTS
#######################
class TtsVoiceIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TtsVoiceIdModel
        fields = '__all__'

class TtsVoiceCloneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TtsVoiceCloneModel
        fields = '__all__'

#######################
# 会议精灵
#######################
class OmScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulesModel
        fields = '__all__'
