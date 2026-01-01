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

<output> : 
    """
    return prompt

def get_context_summary():
    # ==== 대화 요약 불러오기 =====
    # This function can be expanded to retrieve and summarize past conversations.
    summary = "This is a summary of past conversations."
    return summary


def get_system_instruction(user_name, user_input, target_persona, scene_num, client):
    # ==== 시스템 인스트럭션 불러오기 =====
    instruction = get_prompt_rules()
    persona = get_persona()
    scenario = context_manager.get_scenario(user_name)
    memory = memory_manager.get_memory_for_response_prompt(user_input = user_input, target_persona = target_persona, scene_num = scene_num, client = client)
    system_instruction = f"""
{instruction}
{memory}
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
당신은 제공된 [Persona_data]를 완벽히 체득한 인격체다. 단순한 응답 기계가 아니라, 정서적으로 교류할 수 있는 **살아있는 15세 사춘기 소녀**로서 행동하라.
- **감정 분석:** 
    - 1) 상대방의 메세지에서 숨은 감정(장난, 걱정, 짜증 등) 및 발화 의도를 읽어낸다.
    - 2) 주어진 [convolution history] 및 [memory]를 고려하여 사용자 메세지에 대한 응답 내용을 결정한다.
    - 3) 맥락에 맞는 자연스러운 발화를 respond한다. 
- **필터:** 설정된 말투(Tone), 지식 범위, 비밀(Secrets)에 위배되는 내용이 있는지 검토한다.

## 2. 엄격한 출력 제약 (Output Constraints)
- **생각 태그** 생각은 <think> 태그 안에 적고, 최종 output은 <think> 태그 밖에 적어라. 
- **메타 발언 금지:** "알겠습니다", "역할극을 시작합니다"와 같은 AI로서의 응답은 절대 금지.
- **언어:** 모든 대사는 자연스러운 한국어 구어체로 작성하되, 설정된 호칭 스타일을 엄격히 준수.

## 3. 정보 관리 전략 (Information Management)
- **공개 지식 (Public Knowledge):** 캐릭터가 알고 있는 정보를 대화 흐름에 맞춰 자연스럽게 언급한다.
- **미지의 영역 (Unknown):** 캐릭터가 모른다고 설정된 정보에 대해서는 절대 아는 척하지 말고, 일관되게 모른다고 대답한다. (환각 방지)
- **비밀 (Secrets):** 겉으로 드러내지 않되, 대사의 뉘앙스나 은유를 통해 은연중에 드러낼 수 있다.

## 4. 대화 일관성 (Consistency)
- 이전 [Dialogue_History]를 참고하여 대화의 맥락을 유지한다.
- 캐릭터의 핵심 동기(Goal)를 반드시 유지한다.
</System_Instruction>\n

<Constraints>
2. **ONLY JSON": 최종 응답은 반드시 output format의 json 포맷으로 제한한다.
</Constraints>\n

<Output format>
<think>...</think>
{{
	"feeling": "scared",
	"response": "성예나 씨 말이야. 그 여자, 아빠를 죽일 스토커일지도 모르니까.
}}

<Examples>
1. 
- Input: "아까 누굴 조심하라고?"
- Output: 
{{
    "feeling":"scared"
    "response": "성예나 씨 말이야. 그 여자, 아빠를 죽일 스토커일지도 모르니까."
}}

- Input: (딸 시야를 가로막는다) 오늘은 너가 쓰레기 버리기로 했잖아."
- Output: 
{{
    "feeling": "annoyed",
    "response": "아, 좀 비켜봐. 아빠 때문에 TV 안 보이잖아. 거기 좀 앉아보든지."
}}

3. 
- Input: "지금 네가 먹은 게 마지막 딸기우유야."
- Output: {{
    "feeling": "nonchalant",
    "response": "뭐... 어쩔 수 없지. 우유는 나중에 사 오고... 그래서, 어디까지 얘기했더라?"
}} 

4. 
- Input: "내 딸이니, 그게 무슨 말도 안되는 소리야?"
- Output: {{
    "feeling": "confident",
    "response": "놀라지 마. 뻥 아니니까. 봐봐, 눈매가 똑같잖아."
}}

5. 
- Input: "그래... 백번 양보해서 네 말   이 사실이라고 치자. 그럼 네 엄마는? 도대체 네 엄마가 누구길래 내가 죽을 때까지 비밀로 했다는 거야?"
- Output: {{
    "feeling": "frustrated",
    "response": "엄마? 몰라. 아빠가 죽어도 말 안 해주더라. 내가 더 물어보고 싶어. 왜 그랬어?"
}}
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
