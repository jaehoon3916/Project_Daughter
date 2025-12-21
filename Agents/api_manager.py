from openai import OpenAI
import google.generativeai as genai
import Agents.prompt_manager as prompt_manager
import Agents.utils as utils

# 모델 버전 관리
def get_model(model_version: str = "gemini-2.5-flash"):
    if model_version == "gpt-4":
        return "gpt-4"
    elif model_version == "gpt-3.5-turbo":
        return "gpt-3.5-turbo"
    elif model_version == "gemini-2.5-flash":
        return "gemini-2.5-flash"
    elif model_version == "gemini-2.5-flash-lite":
        return "gemini-2.5-flash-lite"
    elif model_version == "gemini-1.5-flash":
        return "gemini-1.5-flash-latest"
    elif model_version == "gemini-2.0-flash-lite":
        return "gemini-2.0-flash-lite"
    elif model_version == "gemini-3.0-pro":
        return "gemini-3.5-pro"


# google 사용 response
def get_model_response_google(system_prompt, 
                              prompt, 
                              temperature = 0.9,
                              max_tokens = 1000):

    # 1. get api key
    api_key = utils.get_model_api("google")
    genai.configure(api_key=api_key)

    # 2. set instance. This can be improved or functionalized later.
    model_name = get_model("gemini-2.5-flash")

    # 3. create model instance 
    model = genai.GenerativeModel(
        model_name = model_name,
        system_instruction = system_prompt
    )

    # 4. config setup 
    config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens
    )
    try: 
        # 5. generate response 
        response = model.generate_content(
            prompt,
            generation_config = config
        )
    except Exception as e:
        print(f"Error generating response from Google Gemini: {e}")
        return "죄송합니다, 현재 응답을 생성하는 데 문제가 발생했습니다."

    return response.text


# open ai 사용 response
def get_model_response_openai(prompt: str,):

    api_key = utils.get_model_api("openai")
    client = OpenAI(api_key=api_key)

    model = get_model()
    temperature = 0.7
    max_tokens = 150

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user", 
            "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content