import Agents.prompt_manager as prompt_manager
import Agents.log_manager as log_manager
import Agents.api_manager as api_manager
import Agents.Memories.memory_manager as memory_manager
import Agents.model_manager as model_manager

"""
Docstring for Agents.Memories.memory_manager

memory manager.
메모리 관리
Goals
상황에 적합한 메모리 검색 및 응답에 반영. 
- 1. 대화 생동감 확보
- 2. 플레이어와의 정서적 교감 (추억, 기억 공유 등)
- 3. (중요!) 정보 레벨에 따라 말하는 내용이 달라짐. 

기본적으로 플레이어가 대화, 증거 획득 등을 통해서 인게임 내에서 정보 레벨을 올릴 수 있음. 
정보 레벨이 오르면 오를 수록 ai가 플레이어에게 제공하는 정보의 중요도가 증가함. 
정보 레벨을 max를 찍고 모든 정보를 해금해서 진엔딩으로  향하는 루트를 확보하면 게임 승리. 
정보레벨에 영향을 미치는 것들
- 캐릭터 호감도
- 단서 
- 논리적 추론 (judged by AI)

파이프라인


"""

def get_memory_for_response_prompt(user_input, target_persona, scene_num:int):
    """
    응답 생성 프롬프트에 필요한 메모리 검색 메소드.
    Input Query
    - scene info(공간 맥락 정보)
    - dialog history (발화, 시간 맥락 정보)
    - current user input 

    return 
    - memory text
    """
    scene_info = "scene_info[scene_num]"
    dialog_history = log_manager.get_last_conversations_formatted()
    current_user_input = user_input

    system_prompt = f"""
당신은 검색 최적화 AI입니다.
사용자의 입력을 보고, RAG 시스템(Vector DB) 검색에 사용할 수 있는 '완전하고 구체적인 하나의 질문(Query)'으로 변경하세요.

**규칙:**
1. 대명사(그것, 그 사람, 거기)를 구체적인 명사로 바꾸세요. (`dialog_history` 참고)
2. 질문의 배경이 되는 상황(`scene_info`)이 중요하다면 키워드로 포함하세요.
3. 절대로 질문에 대해 직접 답변하지 마세요. 오직 '검색용 쿼리'만 출력하세요.
4. 사용자의 의도가 명확하지 않다면, 가장 개연성 있는 의도로 구체화하세요.

"""
    input_prompt = f"""
**입력 데이터:**
[scene_info]: {scene_info}
[dialog history]: {dialog_history}
[current_user_input]: {current_user_input}

**출력 포맷:**
json 형식으로 출력해. 
ex)
{{
    "text": (검색에 최적화된 한 문장)
}}

입력데이터를 바탕으로 memory RAG에 검색할 input query를 생성해줘.
Your Output: 
"""
    
    # get input query from LLM
    model_name = api_manager.get_model("gemini-2.5-flash-lite") 
    input_query = api_manager.get_model_response_google(system_prompt,
                                          input_prompt,
                                          model_name,
                                          temperature = 0.5,
                                          json = True)
    
    print("==== input query ====")
    print(input_query)
    model_name = model_manager.EMBEDDING_MODEL
    client = memory_manager.database_check(collection_name = target_persona, embedding_model = model_name)
    
    retrieved_mem, context = memory_manager.search_memory(collection_name = target_persona,
                                                          client =  client,
                                                          emb_model = model_name,
                                                          query = input_query)
    print("==== retrieved memory ====")
    print(context)

    return context


def observe():
    """
    관찰 정보. user input을 llm에게 줘서 관찰 정보 획득. 
    """
    # prompt_path = ""
    # with open("")
