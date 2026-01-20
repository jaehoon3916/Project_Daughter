from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import Agents.model_hub as model_hub
import Agents.model_manager as model_manager
import Agents.Memories.rag_manager as rag_manager

app = FastAPI()

# 2. CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 모든 곳에서의 접속을 허용합니다.
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST 등 모든 메소드를 허용합니다.
    allow_headers=["*"],      # 모든 헤더를 허용합니다.
)

# 유니티에서 보낼 데이터 형식을 정의 (C# 클래스와 매칭됨)
class ChatRequest(BaseModel):
    name: str
    scene_num: int
    target_persona: str
    affinity: int
    response: str



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
    target_persona = request.target_persona # str
    affinity = request.affinity
    response = request.response
    embedding_model = model_manager.EMBEDDING_MODEL
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)

    # --- AI 처리 구간 ---
    ai_response = model_hub.run_model(response, user_name, user_id, target_persona, affinity, scene_num, client)

    # ------------------------------------------
    return {
        "response": ai_response["response"],
        "affinity_change": ai_response["affinity_delta"],
        "emotion": ai_response["emotion"]
    }

@app.post("/open")
async def open_endpoint(request: ChatRequest):
    user_name = request.name
    user_id = '001'
    scene_num = request.scene_num
    target_persona = request.target_persona # str
    affinity = request.affinity
    response = request.response
    embedding_model = model_manager.EMBEDDING_MODEL
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)
    
    ai_response = model_hub.open_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    return {
        "response": ai_response["response"],
        "affinity_change": ai_response["affinity_delta"],
        "emotion": ai_response["emotion"]
    }

@app.post("/close")
async def close_endpoint(request: ChatRequest):
    user_name = request.name
    user_id = '001'
    scene_num = request.scene_num
    target_persona = request.target_persona # str
    affinity = request.affinity
    embedding_model = model_manager.EMBEDDING_MODEL
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)

    model_hub.close_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    return True
    # ------------------------------------------

if __name__ == "__main__":
    # host="0.0.0.0"으로 해야 외부(같은 공유기 내 다른 기기)에서도 접속 가능
    uvicorn.run(app, host="0.0.0.0", port=8000)