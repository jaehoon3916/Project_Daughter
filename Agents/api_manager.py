import torch
from openai import OpenAI
import google.generativeai as genai
import Agents.prompt_manager as prompt_manager
import Agents.utils as utils

MODEL = "gpt-3.5-turbo"

def get_model(model_version: str = "gpt-3.5-turbo"):
    if model_version == "gpt-4":
        return "gpt-4"
    elif model_version == "gpt-3.5-turbo":
        return "gpt-3.5-turbo"
    elif model_version == "gemini-2.5-flash":
        return "gemini-2.5-flash"
    elif model_version == "gemini-1.5-flash":
        return "gemini-1.5-flash"

# google 사용 response
def get_model_response_google(
                              persona, 
                              prompt, 
                              temperature = 0.7,
                              max_tokens = 150):

    # 1. get api key
    api_key = utils.get_model_api("google")
    genai.configure(api_key)

    # 2. set instance. This can be improved or functionalized later.
    model_name = get_model("gemini-1.5-flash")

    # 3. create model instance 
    model = genai.GenerativeModel(
        model_name = model_name,
        system_instruction = persona
    )

    # 4. config setup 
    config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens
    )

    # create full context history?

    # 5. generate response 
    response = model.generate_content(
        prompt,
        generation_config = config
    )

    return response.text


# open ai 사용 response
def get_model_response_openai(prompt: str,):

    api_key = utils.get_model_api("openai")
    print(api_key)
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