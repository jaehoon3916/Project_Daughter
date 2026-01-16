from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import Agents.model_hub as model_hub
import Agents.model_manager as model_manager
import Agents.Memories.rag_manager as rag_manager

app = FastAPI()

# 유니티에서 보낼 데이터 형식을 정의 (C# 클래스와 매칭됨)
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"유니티에서 온 메시지: {request.response}")
    # response, affinity
    
    
    # user_name = "재훈"
    # user_id = "001"
    # scene_num = 4
    # target_persona = "Daughter"
    user_name = request.name
    user_id = '001'
    scene_num = request.scene_num
    target_persona = str(request.target_persona)
    affinity = request.affinity
    response = request.response
    session = request.session
    embedding_model = model_manager.EMBEDDING_MODEL
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)

    if session == 0:
        # 세션이 0이면 새로운 세션 시작
        model_hub.open_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    elif session == 1:
        # --- AI 처리 구간 ---
        ai_response = model_hub.run_model(response, user_name, user_id, target_persona, affinity, scene_num, client)
    else:
        model_hub.close_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    # ------------------------------------------
    return {
        "response": ai_response["response"],
        "affinity_change": ai_response["affinity_delta"],
        "emotion": ai_response["emotion"]
    }

if __name__ == "__main__":
    # host="0.0.0.0"으로 해야 외부(같은 공유기 내 다른 기기)에서도 접속 가능
    uvicorn.run(app, host="127.0.0.1", port=5000)