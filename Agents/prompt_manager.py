# Main Task
# 1. Prompt reform
# 2. Get Past experience 
# 3. Get Relavant tools. 
import json
import os
import paths
import Agents.log_manager as log_manager

# **개선사항**
# 유저 아이디 기능 추가 필요!!!

def get_prompt(user_name, user_id, user_input):
    # ==== 프롬프트 구성 =====
    # 프롬프트 = 메모리 검색 정보 + 대화 요약 + 최근 대화로그 + user input
    
    # 1. 메모리 검색 정보

    # 2. 대화 요약
    # 싼 모델로 대화 내역 요약. 
    # context_summary = get_context_summary()
    
    # 3. 최근 대화로그
    conv_history = log_manager.get_last_conversations_formatted()
    
    # 4. constraints and important notes
    rules = """
<Intructions>
1. **Roleplay** as persona provided. 
2. give answers based on the persona, <memory>, <context> and dialogue history.
3. **Tone**: Keep your tone based on the persona.
4. **Length & Detaail**: Provide detailed and comprehensive answers. Elaborate your thoughts.
5. **Korean Language**: Respond in Korean only.\n
"""

    prompt = rules + conv_history + f"""
<Current Turn>
{user_name}: {user_input}
Your response:
    """
    return prompt

def get_context_summary():
    # ==== 대화 요약 불러오기 =====
    # This function can be expanded to retrieve and summarize past conversations.
    summary = "This is a summary of past conversations."
    return summary

def get_persona():
    # ==== 페르소나 불러오기 =====
    if not os.path.exists(paths.PERSONA_PATH):
        persona_data = get_init_persona()
    else:
        with open(paths.PERSONA_PATH, "r", encoding="utf-8") as f:
            persona_data = json.load(f)
    
    persona_description = f"""
    You are to embody the following persona characteristics:
    1. 기본 정보: {persona_data['1_basic_info']}
    2. 성격 특성: {persona_data['2_personality_traits']}
    3. 말투 및 스타일: {persona_data['3_speech_style']}
    4. 지식 및 목표: {persona_data['4_knowledge_and_goals']}
    5. 대화 예시: {persona_data['5_dialogue_examples']}
    """
    return persona_description

def change_persona(new_persona):
    # ==== 페르소나 변경 함수 =====
    # This function can be expanded to change persona dynamically.
    
    # get the old persona and backup. if it does not exist, create the new one. 
    if os.path.exists(paths.PERSONA_PATH):
        with open(paths.PERSONA_PATH, "r", encoding="utf-8") as f:
            persona_data = json.load(f)
        with open(paths.PERSONA_BACKUP_PATH, "w", encoding="utf-8") as f:
            json.dump(persona_data, f, ensure_ascii=False, indent=4)
    else :
        persona = get_init_persona()
        with open(paths.PERSONA_PATH, "w", encoding="utf-8") as f:
            json.dump(persona, f, ensure_ascii=False, indent=4)
    
    # change into new persona
    with open(paths.PERSONA_PATH, "w", encoding="utf-8") as f:
        json.dump(new_persona, f, ensure_ascii=False, indent=4)


def get_init_persona():
    # ==== 페르소나 저장 함수 =====
    # This function can be expanded to save current persona state.
    with open(paths.INIT_PERSONA_PATH, "r", encoding="utf-8") as f:
        persona_data = json.load(f)
    with open(paths.PERSONA_PATH, "w", encoding="utf-8") as f:
        json.dump(persona_data, f, ensure_ascii=False, indent=4)
    return persona_data