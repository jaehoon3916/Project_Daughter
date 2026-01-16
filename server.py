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
    print(f"유니티에서 온 메시지: {request.message}")
    
    user_name = "재훈"
    user_id = "001"
    embedding_model = model_manager.EMBEDDING_MODEL
    scene_num = 4
    target_persona = "Daughter"
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)

    # --- AI 처리 구간 ---
    ai_response = model_hub.run_model(request.message, user_name, user_id, target_persona, scene_num, client)
    # ------------------------------------------
    
    return {
        "feeling": ai_response["feeling"],
        "reply": ai_response["response"]
    }

if __name__ == "__main__":
    # host="0.0.0.0"으로 해야 외부(같은 공유기 내 다른 기기)에서도 접속 가능
    uvicorn.run(app, host="127.0.0.1", port=5000)