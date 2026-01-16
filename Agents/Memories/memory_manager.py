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
CONV_TURN_LIMIT = 100

def get_memory_for_response_prompt(user_name, user_input, target_persona, scene_num:int, client):
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
    dialog_history, _ = log_manager.get_last_conversations_formatted(user_name, target_persona)
    current_user_input = user_input

    system_prompt = f"""
당신은 검색 최적화 AI입니다.
<dialog history> 및 user_input을 보고, {target_persona}의 RAG 메모리 검색에 사용할 수 있는 '완전하고 구체적인 하나의 질문(Query)'으로 변경해.

<Instruction>
1.<dialogue history> 및 user_input으로부터 **대화 맥락** 및 **중요한 정보**를 추출해.
2.추출한 대화맥락과 중요한 정보를 바탕으로 검색 쿼리를 작성해.
3.검색 쿼리는 최대한 대화 맥락을 설명해야 하며, **중요한 정보**를 포함해야 해.
4.절대로 질문에 대해 직접 답변하지 마. 오직 '검색용 쿼리'만 출력해.


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

def save_to_memory(new_dataset, target_persona):
    # with open(paths.MEMORY, "a", encoding="utf-8") as f:
    #     f.write(json.dumps(new_dataset, ensure_ascii=False) + "\n")

    if target_persona == "은솔":
        memory_path  = paths.MEMORY_PATH0

    with open(memory_path, "r", encoding="utf-8") as f:
        memory_list = json.load(f)  # 여기서 memory_list는 파이썬의 '리스트'가 됩니다.

    # 3. 리스트에 '뽁' 추가합니다.
    for new_data in new_dataset:
        memory_list.append(new_data)

    # 4. 리스트 전체를 다시 파일에 씁니다.
    with open(memory_path, "w", encoding="utf-8") as f:
        # indent=2를 주면 보기 좋게 정렬되고, ensure_ascii=False는 한글 안 깨지게 해줍니다.
        json.dump(memory_list, f, ensure_ascii=False, indent=2)

def save_conversation_to_memory(collection_name, persona,client, scene_num):
    """
    대화 내용을 요약해서 메모리에 저장. 
    """

    # 최근 대화 요약
    last_conversations, conv_length= log_manager.get_last_conversations_list()
    # if conv_length < CONV_TURN_LIMIT:
    #     return
    target_persona = collection_name
    system_prompt = f"""
<Instruction>
1. 주어진 <dialogue history>에서 {target_persona}가 기억해야 할 핵심 정보를 추출한다.
2. **맥락적 그룹화**: 하나의 에피소드는 절대 나누지 말고 하나의 완성된 문장으로 통합한다.
3. **독립성 유지**: 전혀 다른 주제의 이야기는 다른 정보로 분리한다.
4. **풍부한 정보**: 단순히 사실만 나열하지 말고, 당시의 분위기나 {target_persona}의 태도, 인과관계를 포함하여 '서사형'으로 작성한다.
5. 출력은 반드시 아래 <output format>인 JSON 형식을 엄격히 준수한다.

<persona>
다음은 {target_persona}의 페르소나이다. 
{persona}

<dialogue history>
{last_conversations}

<output format>
<think>(reasoning step)</think>
{{
    "extracted_info": [
        {{
            "1": (중요한 정보 1)
        }},
        {{
            "2": (중요한 정보 2)
        }}
    ]
}}

example)
1) 
input: 
"user": "뭐하냐"
"daughter": "침대에 누워있는데."
"user": "그래? 나 치킨 사왔는데 치킨 좀 먹을래?"
"daughter": "응."
"user": "뻥이야. 안 사왔어."
"daughter": "진짠 줄 알았네."
"user": "에이, 재미없어"
"daughter": "나는 재밌었는데."
"user": "에라이... 야, 오늘 밖에 비오니까 괜히 나가지 마라."
"daughter": "알겠어."

output:
[{{
        "1": "아빠가 치킨을 사왔다며 먹을지 물었다. Daughter는 그러겠다고 했지만, 그것은 거짓말이었다. Daughter는 무덤덤하게 답했고 그 반응에 아빠는 실망했다."
    }},
    {{
        "2": "밖에 비가 온다."
}}]
"""
    prompt = "output: "
    try:
        raw_response = api_manager.get_model_response_google(system_prompt, prompt, model_name="gemini-2.5-flash", temperature=0.2, json=True)
        
        print("==== raw response for conversation summary ====")
        print(raw_response)

        response = json.loads(raw_response).get("extracted_info", [])
    except Exception as e:
        print(f"Error getting extracted info: {e}")
        return

    print("==== conversation summary ====")
    print(response)
    
    info_list = []
    for _, item in enumerate(response):
        for i, info in item.items():
            print(f"==== processing extracted info {i} ====")
            print(info)
        try:
        # 요약내용 메모리에 저장
            new_dataset ={
                    "level": 1,
                    "type": "observation",
                    "content": info,
                    "scene_num": scene_num  
                }

            info_list.append(new_dataset)

        except Exception as e:
            print(f"Error saving conversation to memory: {e}")
            continue
    
    save_to_memory(info_list, target_persona)
    rag_manager.add_memory_to_db(collection_name, info_list, client, batch_size= 0)
    
    # 대화 로그 초기화
    log_manager.clear_conversation_log()

    return info_list

def reflect(collection_name, persona, client, scene_num):
    """
    # 걍 일단 대화내역을 나이브하게 쭉 다 저장해서, 프롬프트로 줘 버리자. 
    # 그리고 세션 종료 시 모델에게 오늘 대화에 대한 피드백을 요청.
    # 파이프라인
    # 1. 정보 추출 -> 이때 정보는 개수 제한을 두지 말고, 독립적으로 n개의 정보를 추출하도록 종용하여 리스트 json 형식으로 반환
    # 2. 추출된 각 정보들을 쿼리 검색 후 관련 기억 수집. 
    # 3. 수집된 기억들과 추출된 정보를 바탕으로 LLM 활용, 새로운 인사이트 도출. 
    # 4. 모든 정보에 대해 반복, 모두 메모리에 저장. 
    """

    # 1. 최근 대화 로그로부터 정보 추출
    last_conversations, conv_length= log_manager.get_last_conversations_list()
    # if conv_length < CONV_TURN_LIMIT:
    #     return
    target_persona = collection_name
    system_prompt = f"""
<Instruction>
1. 주어진 <dialogue history>에서 {target_persona}가 기억해야 할 핵심 정보를 추출한다.
2. **맥락적 그룹화**: 연관된 대화의 흐름은 절대 나누지 말고 하나의 완성된 문장으로 통합한다.
    - 예: A의 제안 -> B의 거절 -> A의 반응은 각각의 정보가 아니라 '하나의 에피소드'로 작성한다.
3. **독립성 유지**: 전혀 다른 주제의 이야기는 별도의 번호로 분리한다.
4. **풍부한 정보**: 단순히 사실만 나열하지 말고, 당시의 분위기나 {target_persona}의 태도, 인과관계를 포함하여 '서사형'으로 작성한다.
5. 출력은 반드시 아래 <output format>인 JSON 형식을 엄격히 준수한다.

<persona>
다음은 {target_persona}의 페르소나이다. 
{persona}

<dialogue history>
{last_conversations}

<output format>
{{
    "extracted_info": [
        {{
            "1": (중요한 정보 1)
        }},
        {{
            "2": (중요한 정보 2)
        }},
        ...
    ]
}}

example)
1) 
input: 
"user": "뭐하냐"
"daughter": "침대에 누워있는데."
"user": "그래? 나 치킨 사왔는데 치킨 좀 먹을래?"
"daughter": "응."
"user": "뻥이야. 안 사왔어."
"daughter": "진짠 줄 알았네."
"user": "에이, 재미없어"
"daughter": "나는 재밌었는데."
"user": "에라이... 야, 오늘 밖에 비오니까 괜히 나가지 마라."
"daughter": "알겠어."

output:
[{{
        "1": "아빠가 치킨을 사왔다며 먹을지 물었다. Daughter는 그러겠다고 했지만, 그것은 거짓말이었다. Daughter는 무덤덤하게 답했고 그 반응에 아빠는 실망했다."
    }},
    {{
        "2": "밖에 비가 온다."
}}]
"""
    prompt = "output: "
    raw_response = api_manager.get_model_response_google(system_prompt, prompt, model_name="gemini-2.5-flash", temperature=0.2, json=True)
    try:
        info_list = json.loads(raw_response).get("extracted_info", [])
    except Exception as e:
        print(f"Error parsing extracted info: {e}")
        return
    
    print("==== extracted info list ====")
    print(info_list)

    # 2. 추출된 정보를 바탕으로 관련 기억 검색 및 수집
    reflection_list = []
    for _, info_dict in enumerate(info_list):
        print("==== info dict ====")
        print(type(info_dict))
        print(info_dict)
        for i, info in info_dict.items():
            print(f"==== processing extracted info {i} ====")
            print(info)
            # model_name = model_manager.EMBEDDING_MODEL
            # client = rag_manager.database_check(collection_name = target_persona, embedding_model = model_name)
            retrieved_mem, context = rag_manager.search_memory(collection_name = target_persona,
                                                                client = client,
                                                                query = info)
            print("==== retrieved memory for reflection ====")
            print(context)

            # 3. 수집된 기억들과 추출된 정보를 바탕으로 새로운 인사이트 도출
            reflection_prompt = f"""
    너는 주어진 <memory>와 <current info>를 바탕으로 새로운 인사이트를 도출하는 LLM이다. 

    이것은 너의 페르소나이다.
    <persona>
    {persona}

    <Instruction>
    1. 당신의 페르소나를 바탕으로, <current info>와 각 <memory>의 관계를 제시하라.
    2. 제시된 관계 속에서 도출할 수 있는 새로운 인사이트가 있다면, 구체적으로 설명하라.
    3. 인사이트에서 비롯되는 너의 감정을 <memory> 및 <current info>로부터 도출하여 추가하라.
    4. 출력은 <output>의 json format을 반드시 따른다.

    <memory>
    {context}

    <current info>
    {info}

    <output>
    {{
        "insight": (도출된 인사이트),
        "related_memory": (관련 기억 내용),
        "current_info": (현재 정보 내용),
        "reflection_emotion": (인사이트로부터 도출된 감정)
    }}
    """
            
            prompt = f"output: "
            raw_response = api_manager.get_model_response_google(reflection_prompt, prompt, model_name="gemini-2.5-flash", temperature=0.3, json=True)
            # try:
            print("==== raw reflection response ====")
            print(raw_response)
            reflection = json.loads(raw_response)
            print("==== reflection result ====")
            print(reflection)

            # 4. 도출된 인사이트 메모리에 저장
            new_dataset ={
                    "level": 1,
                    "type": "reflection",
                    "content": f"{reflection['insight']}",
                    "scene_num": scene_num 
                }

            reflection_list.append(new_dataset)
            # except Exception as e:
            #     print(f"Error parsing reflection result: {e}")
            #     continue
        
    save_to_memory(reflection_list)  
    rag_manager.add_memory_to_db(collection_name, reflection_list, client, batch_size= 0)

    # 대화 로그 초기화
    log_manager.clear_conversation_log()

    return reflection_list



    

    
    