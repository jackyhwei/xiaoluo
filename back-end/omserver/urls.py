"""
URL configuration for omserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.urls import re_path as url

from .views import index, view_tts, view_asr, view_character, view_background, view_translator, view_livestreaming
from .views import view_auth, view_llm, view_memory

urlpatterns = [
    url(r'^$', index.main, name='omserver/index'),
    path('index.html', index.main, name='omserver/index'),
    # path('admin/', admin.site.urls),

    # login views
    path('login.html', view_auth.login, name='omserver/login'),
    path('logout.html', view_auth.logout, name='omserver/logout'),
    path('user_pwd.html', view_auth.user_pwd, name='omserver/user_pwd'),
    path('login_face.html', view_auth.login_face, name='omserver/login_face'),
    path("register.html", view_auth.register, name="omserver/register"),
    path("forgot-password.html", view_auth.forgotpassword, name="omserver/forgotpassword"),
    path("recover-password", view_auth.recoverpassword, name="omserver/recoverpassword"),
    # login apis
    path('logout', view_auth.logout, name='omserver/logout'),
    path('login', view_auth.login, name='omserver/login'),
    path("register", view_auth.register, name="omserver/register"),

    # charactor
    # character roles APIs
    path('character_store.html', view_character.CharacterRole.character_store, name='omserver/charater_store'),
    path('character_role_add.html', view_character.CharacterRole.character_role_add, name='omserver/character_role_add'),
    path('character_role_modify.html', view_character.CharacterRole.character_role_modify, name='omserver/character_role_modify'),
    path('character_role_detail.html', view_character.CharacterRole.character_role_detail, name='omserver/character_role_detail'),
    path('character/role/list', view_character.CharacterRole.character_role_list, name='omserver/character_role_list'),
    path('character/role/create', view_character.CharacterRole.character_role_create, name='omserver/character_role_create'),
    path('character/role/delete/<int:pk>', view_character.CharacterRole.character_role_delete, name='omserver/character_role_delete'),
    path('character/role/edit/<int:pk>', view_character.CharacterRole.character_role_modify2, name='omserver/character_role_modify2'),
    # path('character/role/detail/<int:pk>', view_character.character_role_detail, name='omserver/character_role_detail'),

    path('character_role_template.html', view_character.CharacterRoleTemplate.character_role_template, name='omserver/character_role_template'),

    # charactor model APIs
    path('character_models.html', view_character.CharacterModel.character_models, name='omserver/character_models'),
    path('character_models_add', view_character.CharacterModel.character_model_add, name='omserver/character_model_create'),
    path('character/model/list', view_character.CharacterModel.character_model_list, name='omserver/character_model_list'),
    path('character/model/delete/<int:pk>', view_character.CharacterModel.character_model_delete, name='omserver/character_model_delete'),
    path('character/model/upload', view_character.CharacterModel.character_model_upload, name='omserver/character_model_upload'),
    path('character/model/user/show', view_character.CharacterModel.character_model_list, name='omserver/character_model_list_user'),
    path('character/model/enable/<int:pk>', view_character.CharacterModel.character_model_enable, name='omserver/character_model_enable'),

    # charactor action APIs
    path('character_action_store.html', view_character.CharacterAction.character_action_store, name='omserver/character_action_store'),
    path('character_action_detail/<int:pk>', view_character.CharacterAction.character_action_detail, name='omserver/character_action_detail'),
    path('character_action_modify/<int:pk>', view_character.CharacterAction.character_action_modify, name='omserver/character_action_modify'),
    path('character_action_add', view_character.CharacterAction.character_action_create, name='omserver/character_action_create'),
    path('character_actions.html', view_character.CharacterAction.character_actions, name='omserver/character_actions'),
    path('character/action/list', view_character.CharacterAction.character_action_list, name='omserver/character_action_list'),
    path('character/action/delete/<int:pk>', view_character.CharacterAction.character_action_delete, name='omserver/character_action_delete'),
    path('character/action/enable/<int:pk>', view_character.CharacterAction.character_action_enable, name='omserver/character_action_enable'),

    # charactor action APIs
    path('character_emotions.html', view_character.CharacterEmotion.character_emotions, name='omserver/character_emotions'),
    path('character/emotion/list', view_character.CharacterEmotion.character_emotion_list, name='omserver/character_emotion_list'),
    path('character/emotion/delete/<int:pk>', view_character.CharacterEmotion.character_emotion_delete, name='omserver/character_emotion_delete'),
    path('character/emotion/enable/<int:pk>', view_character.CharacterEmotion.character_emotion_enable, name='omserver/character_emotion_enable'),

    # background views
    path('background_list.html', view_background.background_list, name='background_list'),
    # background APIs
    path('scene/background/delete/<int:pk>', view_background.delete_background_image, name='delete_background_image'),
    path('scene/background/upload', view_background.upload_background_image, name='upload_background_image'),
    path('scene/background/list', view_background.show_background_image, name='show_background_image'),

    # translate
    path('translate_settings.html', view_translator.translate_settings, name='translate_settings'),
    path('translate_youdao.html', view_translator.translate_youdao, name='translate_youdao'),
    path('translate_huoshan.html', view_translator.translate_houshan, name='translate_huoshan'),
    path('translate_google.html', view_translator.translate_google, name='translate_google'),

    #livestreaming
    path('live_settings', view_livestreaming.live_settings, name='live_settings'),
    path('live_bilibili', view_livestreaming.live_bilibili, name='live_bilibili'),
    path('live_douyin', view_livestreaming.live_douyin, name='live_douyin'),
    path('live_douyv', view_livestreaming.live_douyv, name='live_douyv'),
    path('live_taobao', view_livestreaming.live_taobao, name='live_taobao'),
    path('live_rtmp', view_livestreaming.live_rtmp, name='live_rtmp'),
    path('live_kuaishou', view_livestreaming.live_kuaishou, name='live_kuaishou'),

    # memory views
    path('memory_shorttime.html', view_memory.view_shorttime_list, name='view_shorttime_list'),
    path('memory_longtime.html', view_memory.view_longtime_list, name='view_longtime_list'),
    # memory APIs
    path('memory/shorttime/list', view_memory.api_shorttime_list, name='api_shorttime_list'),
    path('memory/shorttime/delete', view_memory.api_shorttime_delete, name='api_shorttime_delete'),
    path('memory/longtime/list', view_memory.api_longtime_list, name='api_longtime_list'),
    path('memory/longtime/delete', view_memory.api_longtime_delete, name='api_longtime_delete'),
    path('memory/reflection', view_memory.reflection_generation, name='reflection_generation'),
    path('memory/clear', view_memory.clear_memory, name='clear_memory'),

    # llm views
    path('llm_chat.html', view_llm.llm_chat, name='omserver/llm_chat'),
    path('llm_kb.html', view_llm.llm_kb, name='omserver/llm_kb'),
    path('llm_bing_qa.html', view_llm.llm_bing_qa, name='omserver/llm_bing_qa'),
    path('llm_settings', view_llm.llm_settings, name='omserver/llm_settings'),

    # llm prompt

    path('chat', view_llm.chat, name='chat'),
    path('llm/kb/list', view_llm.llm_kb_list, name='llm_kb_list'),

    path('llm_prompt.html',  view_llm.llm_prompt, name='omserver/llm_prompt'),
    path('llm_prompt_new',  view_llm.llm_prompt_new, name='omserver/llm_prompt_new'),
    path('llm/prompt/edit/<int:pk>', view_llm.llm_prompt_modify, name='omserver/llm_prompt_modify'),
    path('llm/prompt/delete/<int:pk>', view_llm.llm_prompt_delete, name='omserver/llm_prompt_delete'),

    # tts
    path('tts_live.html', view_tts.tts_live, name='omserver/tts_live'),
    path('tts_clone.html', view_tts.tts_clone, name='omserver/tts_clone'),
    path('tts_settings.html', view_tts.tts_settings, name='omserver/tts_settings'),
    # asr
    path('asr_live.html', view_asr.asr_live, name='omserver/asr_live'),
    path('asr_file.html', view_asr.asr_file, name='omserver/asr_file'),
    path('asr_hotwords.html', view_asr.asr_hotwords, name='omserver/asr_hotwords'),
    path('asr_hotwords_show.html', view_asr.asr_hotwords, name='omserver/asr_hotwords_show'),
    path('asr_sensiwords.html', view_asr.asr_sensiwords, name='omserver/asr_sensiwords'),
    path('asr_sensiwords_show.html', view_asr.asr_sensiwords, name='omserver/asr_sensiwords_show'),
    path('asr_langmodel.html', view_asr.asr_langmodel, name='omserver/asr_langmodel'),
    
    # sysconfig
    path('config/get', index.get_config, name='get_config'),
    path('config/save', index.save_config, name='save_config'),
    # tts
    path('tts/generate', view_tts.generate, name='tts_generate'),
    path('tts/voices', view_tts.get_voices, name='get_voices'),
    # tts voice id
    path('tts/voiceid/list', view_tts.tts_voiceid_list, name='tts_voiceid_list'),
    path('tts/voiceid/new', view_tts.tts_voiceid_new, name='tts_voiceid_new'),
    path('tts/voiceid/delete', view_tts.tts_voiceid_delete, name='tts_voiceid_delete'),
    # tts voice clone
    path('tts/voiceclone/list', view_tts.tts_voiceclone_list, name='tts_voiceclone_list'),
    path('tts/voiceclone/new', view_tts.tts_voiceclone_new, name='tts_voiceclone_new'),
    path('tts/voiceclone/delete', view_tts.tts_voiceclone_del, name='tts_voiceclone_del'),
    # translate
    path('translation', view_translator.translation, name='translation'),

    #####################
    # tests
    #####################
    path('test_vrm.html', index.test_vrm, name='test_vrm'),
    path('login_face.html', view_auth.login_face, name='login_face'),

]
