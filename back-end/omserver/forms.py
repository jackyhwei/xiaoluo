from django import forms
from omserver.model.model_character import CharacterRoleModel
from omserver.model.model_llm import LlmPromptModel

class CustomRoleForm(forms.ModelForm):
    class Meta:
        model = CharacterRoleModel
        fields = ['role_name', 'persona', 'personality', 'scenario', 'examples_of_dialogue', 'custom_role_template_type']

class LlmPromptForm(forms.ModelForm):
    class Meta:
        model = LlmPromptModel
        fields = ['prompt_name', 'prompt_type', 'prompt_language', 'prompt_scenario', 'prompt_personality', 'prompt_content']
