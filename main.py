import Agents.model_hub as model_hub
import Agents.Memories.rag_manager as rag_manager
import Agents.model_manager as model_manager
import sys

def main():
    # model name, user input -> model -> get the response 
    model_name = "gpt-3.5-turbo"
    
    # user input 
    # use rinput에 담길 정보는 다음과 같다. 
    # 1. 유저 이름
    # 2. 유저와 모델의 관게 정보
    # 3. 실제 유저 input
    # 4. 기타 스탯 정보

    # user_input = "안녕?"
    user_name = "연돌이"
    user_id = "001"
    embedding_model = model_manager.EMBEDDING_MODEL
    scene_num = 5
    target_persona = "은솔"
    affinity = 100
    on_session = True
    
    # 0. check database 
    client = rag_manager.database_check(collection_name = target_persona, embedding_model = embedding_model)

    greeting = "일어났어? 꽤나 푹 자고 있었네."
    # greeting = model_hub.open_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    print(f"은솔: {greeting}")
    while on_session:
        user_input = input("나: ")
        if(user_input.lower() in ["exit", "quit"]):
            break

        response = model_hub.run_model(user_input, user_name, user_id, target_persona, affinity, scene_num, client)
        print(f"response: {response}")
    
    model_hub.close_session(user_name = user_name, user_id = user_id, target_persona = target_persona, affinity = affinity, scene_num = scene_num, client = client)
    print("대화를 종료합니다.")
    sys .exit(0)
    
if __name__ == "__main__":
    
    main()

