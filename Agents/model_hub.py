# This is the hub of the model, 
# where everything about the model is managed.

# main task
# 1. 사용자 응답 preprocessing
# 2. 프롬프트 주입, response get
# 3. raw data postprocess

import Agents.api_manager as api_manager
import Agents.prompt_manager as prompt_manager
import Agents.log_manager as log_manager


def run_model(user_input: str):
    user_name = "재훈"
    user_id = "001"

    # 1. 사용자 응답 전처리
    prompt = prompt_manager.get_prompt(user_name = user_name, user_id = user_id, user_input = user_input)

    # 2. 프롬프트 주입 및 응답 받기
    persona = prompt_manager.get_persona()
    print(f"=== prompt to model ===\n{prompt}\n=====================")
    print(f"=== persona to model ===\n{persona}\n=====================")
    raw_response =api_manager.get_model_response_google(persona = persona,
                                                        prompt = prompt)
    # 3. 응답 후처리
    response = raw_response.strip()

    # 4. 응답 저장
    log_manager.add_last_conversation(user_name, user_input, response)
    
    # return response 
    return response