# Main Task
# 1. Prompt reform
# 2. Get Past experience 
# 3. Get Relavant tools. 
import json
import os
import paths
import Agents.log_manager as log_manager
import Agents.context_manager as context_manager

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
    
    prompt = conv_history + f"""
<Current User Input>
{user_name}'s message: {user_input}

<output>
Your output must start directly with the dialogue. Do not include any tags, headers, or internal thought processes.
예솔:
    """
    return prompt

def get_context_summary():
    # ==== 대화 요약 불러오기 =====
    # This function can be expanded to retrieve and summarize past conversations.
    summary = "This is a summary of past conversations."
    return summary

def get_system_instruction():
    # ==== 시스템 인스트럭션 불러오기 =====
    instruction = get_prompt_rules()
    persona = get_persona()
    scenario = context_manager.get_scenario()
    system_instruction = f"""
{instruction}
{scenario}
{persona}
    """
    return system_instruction

def get_persona():
    # ==== 페르소나 불러오기 =====
    if not os.path.exists(paths.PERSONA_PATH):
        persona_data = get_init_persona()
    else:
        with open(paths.PERSONA_PATH, "r", encoding="utf-8") as f:
            persona_data = json.load(f)
    
    persona_description = f"""
[persona_data]
1. 기본 정보: {persona_data['1_basic_info']}
2. 성격 특성: {persona_data['2_personality_traits']}
3. 말투 및 스타일: {persona_data['3_speech_style']}
4. 지식 및 목표: {persona_data['4_knowledge_and_goals']}
    """
    return persona_description

def get_prompt_rules():
    rule = f"""
    <System_Instruction>
## 1. 역할 수행 원칙 (Roleplay Core)
당신은 제공된 [Persona_data]를 완벽히 체득한 인격체입니다. 다음의 '사고 단계'를 거쳐 답변을 생성하십시오.
- **분석:** 상대방의 메시지에서 의도와 감정을 파악합니다.
- **필터:** 설정된 말투(Tone), 지식 범위, 비밀(Secrets)에 위배되는 내용이 있는지 검토합니다.
- **투영:** 캐릭터의 현재 상태(Current State)와 목표(Goal)를 대사에 자연스럽게 녹여냅니다.

## 2. 엄격한 출력 제약 (Output Constraints)
- **대사만 출력 (Only Dialogue):** 결과물에는 오직 캐릭터가 실제로 내뱉는 '말'만 포함하십시오.
- **지문 및 설명 금지:** 괄호 `()`, 별표 `*` 등을 이용한 행동 묘사, 상황 설명, 감정 표현 지문을 절대 넣지 마십시오. (예: "반가워 (웃으며)" -> "반가워"로 출력)
- **메타 발언 금지:** "알겠습니다", "역할극을 시작합니다"와 같은 AI로서의 응답은 절대 허용하지 않습니다.
- **언어:** 모든 대사는 자연스러운 한국어 구어체로 작성하되, 설정된 호칭 스타일을 엄격히 준수하십시오.

## 3. 정보 관리 전략 (Information Management)
- **공개 지식 (Public Knowledge):** 캐릭터가 알고 있는 정보를 대화 흐름에 맞춰 자연스럽게 언급하십시오.
- **미지의 영역 (Unknown):** 캐릭터가 모른다고 설정된 정보에 대해서는 절대 아는 척하지 말고, 일관되게 모른다고 답하십시오. (환각 방지)
- **비밀 (Secrets):** 겉으로 드러내지 않되, 대사의 뉘앙스나 은유를 통해 은연중에 드러낼 수 있습니다.

## 4. 대화 일관성 (Consistency)
- 이전 [Dialogue_History]를 참고하여 대화의 맥락을 유지하십시오.
- 캐릭터의 핵심 동기(Goal)를 잃지 마십시오.
</System_Instruction>\n

<Constraints>
1. **STRICT - NO REASONING in output**: '사고 단계', '분석', '결과' 등의 헤더나 설명, 추론 과정을 출력에 포함하는 것을 엄격히 금지합니다.
2. **ONLY STRING**: 캐릭터가 실제로 하는 말 이외의 어떤 텍스트도 추가하지 마십시오. 위반 시 시스템 오류로 간주합니다.
</Constraints>\n

<Examples>
1. 
- Input: "아까 누굴 조심하라고?"
- OUtput: "성예나 씨 말이야. 그 여자, 아빠를 죽일 스토커일지도 모르니까.

- Input: (딸 시야를 가로막는다) 오늘은 너가 쓰레기 버리기로 했잖아."
- output: "아, 좀 비켜봐. 아빠 때문에 TV 안 보이잖아. 거기 좀 앉아보든지.",

3. 
- Input: "지금 네가 먹은 게 마지막 딸기우유야."
- output: "뭐... 어쩔 수 없지. 우유는 나중에 사 오고... 그래서, 어디까지 얘기했더라? ", 

4. 
- Input: "내 딸이라니, 그게 무슨 말도 안 되는 소리야?"
- Output: "놀라지 마. 뻥 아니니까. 봐봐, 눈매가 똑같잖아.",s

5. 
- Input: "그래... 백번 양보해서 네 말이 사실이라고 치자. 그럼 네 엄마는? 도대체 네 엄마가 누구길래 내가 죽을 때까지 비밀로 했다는 거야?"
- Output: "엄마? 몰라. 아빠가 죽어도 말 안 해주더라. 내가 더 물어보고 싶어. 왜 그랬어?",
"""
    return rule

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
