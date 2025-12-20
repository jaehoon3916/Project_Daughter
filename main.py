import Agents.model_hub as model_hub
import sys

def main():
    # model name, user inpt -> model -> get the response 
    model_name = "gpt-3.5-turbo"
    
    # user input 
    # use rinput에 담길 정보는 다음과 같다. 
    # 1. 유저 이름
    # 2. 유저와 모델의 관게 정보
    # 3. 실제 유저 input
    # 4. 기타 스탯 정보

    # user_input = "안녕?"
    user_input = sys.argv[1]


    response = model_hub.run_model(user_input)
    print(f"response: {response}")

if __name__ == "__main__":
    
    main()

