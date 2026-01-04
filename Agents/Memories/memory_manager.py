from click import prompt
import json
import Agents.prompt_manager as prompt_manager
import Agents.log_manager as log_manager
import Agents.api_manager as api_manager
import Agents.Memories.rag_manager as rag_manager
import Agents.model_manager as model_manager
import paths

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

def get_memory_for_response_prompt(user_input, target_persona, scene_num:int, client):
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
[scene_info]: {scene_info}
[dialog history]: {dialog_history}

**입력 데이터:**
[current_user_input]: {current_user_input}

**출력 포맷:**
json 형식으로 출력해. 
ex)
{{
    "text": (검색에 최적화된 한 문장)
}}

입력데이터를 바탕으로 memory RAG에 검색할 input query를 생성해줘.
user_input: {current_user_input}
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
    # model_name = model_manager.EMBEDDING_MODEL
    # client = rag_manager.database_check(collection_name = target_persona, embedding_model = model_name)
    
    retrieved_mem, context = rag_manager.search_memory(collection_name = target_persona,
                                                          client =  client,
                                                          emb_model = model_name,
                                                          query = input_query)
    print("==== retrieved memory ====")
    print(context)

    return context


# def observe():
#     """
#     관찰 정보. user input을 llm에게 줘서 관찰 정보 획득. -> 환경 변화 인식. 
#     """
#     prompt_path = "Prompts/observation_prompt.txt"
#     with open(prompt_path, 'r', 'utf-8') as f:

def save_to_memory(new_dataset):
    # with open(paths.MEMORY, "a", encoding="utf-8") as f:
    #     f.write(json.dumps(new_dataset, ensure_ascii=False) + "\n")
    with open(paths.MEMORY, "r", encoding="utf-8") as f:
        memory_list = json.load(f)  # 여기서 memory_list는 파이썬의 '리스트'가 됩니다.

    # 3. 리스트에 '뽁' 추가합니다.
    memory_list.append(new_dataset)

    # 4. 리스트 전체를 다시 파일에 씁니다.
    with open(paths.MEMORY, "w", encoding="utf-8") as f:
        # indent=2를 주면 보기 좋게 정렬되고, ensure_ascii=False는 한글 안 깨지게 해줍니다.
        json.dump(memory_list, f, ensure_ascii=False, indent=2)

def save_conversation_to_memory(collection_name, client, embedding_model, scene_num):
    """
    대화 내용을 요약해서 메모리에 저장. 
    """

    # 최근 대화 요약
    last_conversations = log_manager.get_last_conversations_list()
    system_prompt = f"""
<Instruction>
1. 아래 <dialogue history>를 읽고, 중요한 정보를 추출한다.
2. 추출한 정보를 바탕으로 1~3문장으로 요약문을 작성한다.

<perona>
다음은 너의 페르소나이다. 
{prompt_manager.get_persona()}

<dialogue history>
{last_conversations}

<output format>
{{
    "summary": (대화 요약문)
}}
"""
    prompt = "output: "
    raw_response = api_manager.get_model_response_google(system_prompt, prompt, model_name="gemini-2.5-flash", temperature=0.5, json=True)

    response = json.loads(raw_response)
    print("==== conversation summary ====")
    print(response["summary"])

    try:
    # 요약내용 메모리에 저장
        new_dataset =[{
                "level": 1,
                "type": "observation",
                "content": response["summary"],
                "scene_num": scene_num  
            }]
    
        save_to_memory(new_dataset)
        rag_manager.add_memory_to_db(collection_name, new_dataset, client, embedding_model,  batch_size= 0)

        return True
    except Exception as e:
        print(f"Error saving conversation to memory: {e}")
        return False

def reflect():
    """
    일정 임계치 도달 시 회고 수행. 세션이 끝나면 회고 수행. 
    """
    last_conversations = log_manager.get_last_conversations_list()
    # prompt_path = "Prompts/reflection_prompt.txt"
    # with open(prompt_path, 'r', 'utf-8') as f:
    #     system_prompt = f.read()

    input_prompt = f"""
<Instruction>
당신은 자아 인식이 있는 AI입니다. 
[최근 대화 내역]: {last_conversations}
"""
    
    