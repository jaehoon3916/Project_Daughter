import os
import json
import re
import paths as paths

def get_last_conversations_list(n = -1):
    # ==== 최근 대화 불러오기 =====
    # This function can be expanded to retrieve the last n conversations.
    if os .path.exists(paths.CONVERSATION_LOG_PATH):
        try:
            with open(paths.CONVERSATION_LOG_PATH, "r", encoding="utf-8") as f:
                    conv_history = json.load(f)
        except Exception as e:
            print(f"Error reading conversation log: {e}")
            conv_history = []
    else: 
        conv_history = []
    
    if(n != -1):
        return conv_history[-n:] if len(conv_history) >= n else conv_history
    else:
        return conv_history, len(conv_history)

def get_last_conversations_formatted(user_name, target_persona, n=-1):
    # ==== 최근 n 대화 불러오기 =====
    conv_history, _ = get_last_conversations_list()
    last_convs = conv_history[-n:] if n != -1 else conv_history
    formatted_convs = f"<dialogue history>\n"
    for log in last_convs: 
        # 안전장치: 짝이 안 맞을 수도 있으니 체크
        role = log.get("role", "unknown")
        text = log["parts"][0]["text"]

        if role == "user":
            formatted_convs += f"{user_name}: {text}\n"
        elif role == "model":
            formatted_convs += f"{target_persona}: {text}\n"
    
    return formatted_convs, len(last_convs)

def add_last_conversation(user_name, user_input, response):
    # ==== 대화 로그 추가 =====
    # This function adds a new conversation log.
    if os .path.exists(paths.CONVERSATION_LOG_PATH):
        with open(paths.CONVERSATION_LOG_PATH, "r", encoding="utf-8") as f:
            conv_history = json.load(f)
    else: 
        conv_history = []
    
    new_log = [{
        "role": "user",
        "parts": [
            {
                "text": user_input,
            }
        ]
    }, {
        "role": "model",
        "parts": [
            {
                "text": response["response"], # 감정 정보를 넣을지 말지는 고민 중
            }
        ]
    }]
    conv_history.extend(new_log)

    with open(paths.CONVERSATION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(conv_history, f, ensure_ascii=False, indent=4)
    
def postprocess(raw_response:str) -> json:
    clean_response = re.sub(r'<think>.*?</think>', '', raw_response, flags = re.DOTALL)

    start_idx = clean_response.find('{')
    end_idx = clean_response.rfind('}')

    if start_idx != -1 and end_idx != -1:
        json_str = clean_response[start_idx : end_idx +1]
    
        try:
            # 3. 문자열을 파이썬 딕셔너리로 변환
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 에러: {e}")
            # 에러 시 기본값 반환하거나 예외 처리
            return {"feeling": "neutral", "response": "오류가 발생했습니다.", "action": ""}
    else:
        print("JSON 형식을 찾을 수 없습니다.")
        return {"feeling": "neutral", "response": "응답 형식이 잘못되었습니다.", "action": ""}

def clear_conversation_log():
    # ==== 대화 로그 초기화 =====
    log_backup()
    with open(paths.CONVERSATION_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

def log_backup():
    # ==== 대화 로그 백업 =====
    if os .path.exists(paths.CONVERSATION_LOG_PATH):
        with open(paths.CONVERSATION_LOG_PATH, "r", encoding="utf-8") as f:
            conv_history = json.load(f)
        
        backup_path = paths.CONVERSATION_LOG_PATH.replace(".json", "_backup.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(conv_history, f, ensure_ascii=False, indent=4)