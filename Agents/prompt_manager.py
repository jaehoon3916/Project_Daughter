# Main Task
# 1. Prompt reform
# 2. Get Past experience 
# 3. Get Relavant tools. 
import json
import os
import paths

def get_prompt(user_name, user_input: str) -> str:
    # ==== 프롬프트 구성 =====
    # 프롬프트 = 메모리 검색 정보 + 대화 요약 + 최근 대화로그 + user input
    
    # 1. 메모리 검색 정보

    # 2. 대화 요약
    # 싼 모델로 대화 내역 요약. 
    # context_summary = get_context_summary()
    
    # 3. 최근 대화로그
    conv_history = get_last_conversations_formatted()
    
    prompt = conv_history + f"""
    Make sure to follow the persona characteristics strictly.
    Based on the memory, context and dialog history, 
    respond to the given {user_name}'s input sentence. 
    Your response must be in Korean.
    {user_name}: {user_input}\n 
    """
    return prompt

def get_context_summary():
    # ==== 대화 요약 불러오기 =====
    # This function can be expanded to retrieve and summarize past conversations.
    summary = "This is a summary of past conversations."
    return summary

def get_last_conversations_list(n = -1):
    # ==== 최근 대화 불러오기 =====
    # This function can be expanded to retrieve the last n conversations.
    if os .path.exists(paths.CONVERSATION_LOG_PATH):
        with open(paths.CONVERSATION_LOG_PATH, "r", encoding="utf-8") as f:
            conv_history = json.load(f)
    else: 
        conv_history = []
    
    if(n != -1):
        return conv_history[-n:] if len(conv_history) >= n else conv_history
    else:
        return conv_history

def get_last_conversations_formatted(n=10):
    # ==== 최근 n 대화 불러오기 =====
    conv_history = get_last_conversations_list()
    last_convs = conv_history[-n:]
    formatted_convs = f"past {n} turns conversations: \n"
    for i in range(0, len(last_convs), 2): # 2개씩(질문+답변) 묶어서 처리
        # 안전장치: 짝이 안 맞을 수도 있으니 체크
        if i+1 < len(last_convs):
            user_msg = last_convs[i]['parts'][0]['text']   # User 대사 꺼내기
            agent_msg = last_convs[i+1]['parts'][0]['text'] # Model 대사 꺼내기
            
            formatted_convs += f"User: {user_msg}\nAgent: {agent_msg}\n"
    
    return formatted_convs

def get_persona():
    # ==== 페르소나 불러오기 =====
    if not os.path.exists(paths.PERSONA_PATH):
        persona_data = get_init_persona()
        with open(paths.PERSONA_PATH, "w", encoding="utf-8") as f:
            json.dump(persona_data, f, ensure_ascii=False, indent=4)
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