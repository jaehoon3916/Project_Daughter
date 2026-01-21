# This is the hub of the model, 
# where everything about the model is managed.

# main task
# 1. 사용자 응답 preprocessing
# 2. 프롬프트 주입, response get
# 3. raw data postprocess

import Agents.api_manager as api_manager
import Agents.prompt_manager as prompt_manager
import Agents.log_manager as log_manager
import Agents.Memories.rag_manager as rag_manager
import Agents.model_manager as model_manager
import Agents.Memories.memory_manager as memory_mangager
import json

CONV_TURN_LIMIT = 50

def run_model(user_input: str, user_name: str, user_id: str, target_persona: str, affinity: int, scene_num: int, client: str):
    user_name = user_name
    user_id = user_id
    client = client
    scene_num = scene_num
    target_persona = target_persona

    # 1. 사용자 응답 전처리 - 사용자의 말로부터 observation 정보 도출.
    # 감정 추출, ()에 입력된 유저의 행동 분석? << 이건 걍 메인 응답 프롬프트에 통합할 수도? 
    # 아니면 generative agents처럼 대화창이 열리고 닫힐 때 환경 인식으로 갈 수도 있지. 
    # 다시 말해, scene 인식, 현재 시나리오 위치를 여기서 인지하게 하는 거임. 
    
    try:
        # 2. 프롬프트 주입 및 응답 받기
        prompt = prompt_manager.get_prompt(user_name = user_name, 
                                        user_id = user_id, 
                                        user_input = user_input,
                                        target_persona = target_persona)
        system_prompt = prompt_manager.get_system_instruction(user_name, user_input, target_persona, affinity, scene_num, client)
        print(f"=== persona to model ===\n{system_prompt}\n=====================")
        print(f"=== prompt to model ===\n{prompt}\n=====================")

        model_name= api_manager.get_model("gemini-3-flash-preview")

        raw_response =api_manager.get_model_response_google(system_prompt = system_prompt,
                                                            prompt = prompt,
                                                            model_name = model_name,
                                                            max_tokens = 2000,
                                                            temperature = 0.7)
        # 3. 응답 후처리
        print("===== raw response =====")
        print(raw_response)    
        response = log_manager.postprocess(raw_response)

        # 4. 응답 저장
        log_manager.add_last_conversation(user_name, user_input, response)

        # return response 
        return response

    except:
        response = "미, 미안. 못 들었어. 다시 한 번만 말해줄래?"
        if affinity > 80:
            response = "미안 못들었어 다시 말하라@고"
        elif affinity >60:
            response = "미안 못들었어 한 번만 다시 말해줄래?"
        elif affinity > 40:
            response = "미안, 못 들었어... 다시 한 번만 말해줄래?"
        elif affinity > 20: 
            response = "미안, 못 들었어! 다시 한 번만 말해줄래?"

        return {
            "emotion": "neutral", 
            'affinity_delta': 0, 
            "response": response
            }

def open_session(user_name: str, user_id: str, target_persona: str, affinity: int, scene_num: int, client: str):

    persona = prompt_manager.get_persona(target_persona, affinity)
    user_input = "안녕?"

    # 2. 프롬프트 주입 및 응답 받기
    prompt = prompt_manager.get_prompt(user_name = user_name, 
                                       user_id = user_id, 
                                       user_input = user_input,
                                       target_persona = target_persona)
    
    system_prompt = prompt_manager.get_system_instruction(user_name, user_input, target_persona, affinity, scene_num, client)
    print(f"=== persona to model ===\n{system_prompt}\n=====================")
    print(f"=== prompt to model ===\n{prompt}\n=====================")
    model_name= api_manager.get_model("gemini-3-flash-preview")
    raw_response =api_manager.get_model_response_google(system_prompt = system_prompt,
                                                        prompt = prompt,
                                                        model_name = model_name,
                                                        max_tokens = 2000,
                                                        temperature = 0.9)
    # 3. 응답 후처리
    print("===== raw response =====")
    print(raw_response)    
    response = log_manager.postprocess(raw_response)

    # 4. 응답 저장
    log_manager.add_last_conversation(user_name, user_input, response)

    return response

def close_session(user_name: str, user_id, target_persona: str, affinity: int, scene_num: int, client: str):
    
    log_manager.clear_conversation_log()

    # persona = prompt_manager.get_persona(target_persona, affinity)

    # # 0. 세션 종료 시 대화 내용 메모리에 저장

    # # option1: summary memory
    # memory_mangager.save_conversation_to_memory(collection_name = target_persona, 
    #                                             persona = persona,
    #                                             client = client,
    #                                             scene_num = scene_num)


    # option2: reflective memory
    # memory_mangager.reflect(collection_name = target_persona, 
    #                         persona = persona,
    #                         client = client, 
    #                         scene_num = scene_num)
    

    
                                            



