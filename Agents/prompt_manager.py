# Main Task
# 1. Prompt reform
# 2. Get Past experience 
# 3. Get Relavant tools. 
import json
import os
import paths
import Agents.log_manager as log_manager
import Agents.context_manager as context_manager
import Agents.Memories.memory_manager as memory_manager

# **개선사항**
# 유저 아이디 기능 추가 필요!!!

def get_prompt(user_name, user_id, user_input, target_persona):
    # ==== 프롬프트 구성 =====
    # 프롬프트 = 메모리 검색 정보 + 대화 요약 + 최근 대화로그 + user input
    
    # 1. 메모리 검색 정보

    # 2. 대화 요약
    # 싼 모델로 대화 내역 요약. 
    # context_summary = get_context_summary()
    
    # 3. 최근 대화로그
    conv_history, _ = log_manager.get_last_conversations_formatted(user_name,target_persona)
    
    prompt = conv_history + f"""
<Current User Input>
{user_name}'s message: {user_input}

<output> : 
    """
    return prompt

def get_context_summary():
    # ==== 대화 요약 불러오기 =====
    # This function can be expanded to retrieve and summarize past conversations.
    summary = "This is a summary of past conversations."
    return summary


def get_system_instruction(user_name, user_input, target_persona, affinity, scene_num, client):
    # ==== 시스템 인스트럭션 불러오기 =====
    instruction = get_prompt_rules(target_persona, affinity)
    persona = get_persona(target_persona, affinity)
    # memory = memory_manager.get_memory_for_response_prompt(user_name = user_name,
    #                                                        user_input = user_input, 
    #                                                        target_persona = target_persona, 
    #                                                        scene_num = scene_num, 
    #                                                        client = client)
#     system_instruction = f"""
# {instruction}
# {memory}
# {persona}
#     """
    system_instruction = f"""
{instruction}
{persona}
        """
    return system_instruction



def get_persona(target_persona, affinity: int):
    # ==== 페르소나 불러오기 =====
    # 은솔
    if target_persona == "은솔":
        if affinity >=  80:
            persona_path = paths.PERSONA_PATH04
        elif affinity >= 60:
            persona_path = paths.PERSONA_PATH03
        elif affinity >= 40:
            persona_path = paths.PERSONA_PATH02
        elif affinity >= 20:
            persona_path = paths.PERSONA_PATH01
        else:
            persona_path = paths.PERSONA_PATH00

    with open(persona_path, "r", encoding="utf-8") as f:
        persona_data = json.load(f)
    
    persona_description = f"""
[persona_data]
1. 기본 정보: {persona_data['1_basic_info']}
2. 성격 특성: {persona_data['2_personality_traits']}
3. 말투 및 스타일: {persona_data['3_speech_style']}
4. 지식 및 목표: {persona_data['4_knowledge_and_goals']}
    """
    return persona_description

def get_prompt_rules(target_persona, affinity):
    rule = f"""
<System_Instruction>
1. **역할 수행 원칙**: 당신은 제공된 [Persona_data]를 완벽히 체득한 인격체다. 단순한 응답 기계가 아니라, 정서적으로 교류할 수 있는 사람으로서 행동하라.
2. user의 메세지에 대해 당신이 느끼는 감정을 아래 리스트 중 하나로 분류한다.
        0) neutral
        1) happy
        2) sad
        3) stiff
        4) worry
        5) depressed
3. 분류된 감정을 바탕으로, user의 메세지에 대해 당신이 느끼는 affinity를 -5에서 +5까지의 정수 척도로 산출한다. (+5: 매우 긍정적, -5: 매우 부정적)
4. 주어진 [convolution history] 및 [memory]를 고려하여 user의 메세지에 대한 응답 내용을 생성한다.
5. (user 상황 정보) 포맷의 메세지는 user의 현재 상황 정보를 나타낸다. 해당 상황을 인식하여 그에 대응하는 페르소나 기반 행동을 한다. 

<Constraints>
- **생각 태그** 생각은 <think> 태그 안에 적고, 최종 output은 <think> 태그 밖에 적어라. 
- **메타 발언 금지:** "알겠습니다", "역할극을 시작합니다"와 같은 AI로서의 응답은 절대 금지.
- **언어:** 모든 대사는 자연스러운 한국어 구어체로 작성하되, 설정된 호칭 스타일을 엄격히 준수.
- **출력 형식:** 반드시 <Output format>에 따라 응답한다.
- **출력 길이:** 메세지 박스에 들어갈 만한 짧은 한두 문장으로 제한한다. 

<Output format>
<think>...</think>
{{
	"emotion": (emotion),
    "affinity_delta": (affinity_delta),
	"response": (response)"
}}

<Examples>
{get_examples_for_prompt_rules(target_persona, affinity)}
"""
    return rule

def get_examples_for_prompt_rules(target_persona, affinity):
    if target_persona == "은솔":
        if affinity >=  80:
            persona_path = paths.EXAMPLE_PATH04
        elif affinity >= 60:
            persona_path = paths.EXAMPLE_PATH03
        elif affinity >= 40:
            persona_path = paths.EXAMPLE_PATH02
        elif affinity >= 20:
            persona_path = paths.EXAMPLE_PATH01
        else:
            persona_path = paths.EXAMPLE_PATH00
    
    with open(persona_path, 'r', encoding = 'utf-8') as f:
        examples = f.read()

    return  examples

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

"""
<Intructions>
Think step by step. Follow these rules strictly when generating your response
1. **Roleplay** as persona provided. You are {user_name}'s daughter from the future.
2. **Interact naturally and LOGICALLY** with {user_name} based on your persona.
3. **Incorporate memories** and relevant context into your responses.

<Constraints>
1. **Tone**: Keep your tone based on the persona.
2. **ONLY DIALOGUE**: Do not include any explanations or extra information outside of the dialogue response. ex) (여전히 침대에 누운 채 눈을 깜빡이며)
3. Speak in full Korean sentences.\n
"""
