import json, uuid
# from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
# from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance,Filter, FieldCondition, Range
import google.generativeai as genai
import Agents.utils as utils
import Agents.model_manager as model_manager
import paths

# def set_embedding_model():
#     return SentenceTransformer("dragonkue/BGE-m3-ko")

def add_memory_to_db(collection_name, new_dataset, client, batch_size= 0):

    points_to_upsert = []

    # get content from 'memory.json'
    for idx, item in enumerate(new_dataset):
        content = item.get('content')

        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, content))
        
        # 1. get api key
        api_key = utils.get_model_api("google")
        genai.configure(api_key=api_key)

        # vector = embedding_model.encode(content).tolist()
        emb_response = genai.embed_content(
            model = model_manager.EMBEDDING_MODEL,
            content=content,
            task_type = 'retrieval_document' # 모델 임베딩에는 무조건 document type으로! (google 임베딩의 경우) (query와 answer doc으 ㄴ형식이 많이 다르니까)
        )

        vector = emb_response["embedding"]

        payload = {
            "level": int(item.get('level', 0)),
            "type": item.get('type'),
            "content": content,
            "scene_num": item.get('scene_num')
        }

        # set db row
        point = PointStruct(
            id = point_id,
            vector = vector,
            payload = payload,
        )
        points_to_upsert.append(point)

        if batch_size != 0 and len(points_to_upsert) >= batch_size:
            client.upsert(
                collection_name = collection_name,
                points = points_to_upsert,
                wait = True
            )
            print(f"Indexed {idx + 1}/{len(new_dataset)} items...")
            points_to_upsert = []

    if points_to_upsert:
        client.upsert(
            collection_name = collection_name,
            points = points_to_upsert,
            wait = True
        )
        print(f"index completed : {len(new_dataset)}")

    return client

def database_check(collection_name, embedding_model):
    client = QdrantClient(path = paths.DB_PATH)

    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    collection_name = str(collection_name)
    if collection_name in collection_names:
        print(f"existing collection '{collection_name}'")
    else:
        client.create_collection(
            collection_name = collection_name,
            vectors_config = VectorParams(size = 768, distance = Distance.COSINE)
        )
        print(f" new collection '{collection_name}'")
        data_path = paths.MEMORY_PATH0
        with open(data_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        client = add_memory_to_db(collection_name, dataset, client)
    
    return client

def clear_database(collection_name, client):
    client.delete_collection(collection_name = collection_name)
    return


def get_rag_response(collection_name, client, query, top_k = 5, level_threshold = -1)-> list:
    '''
    나중에 agent toolkit을 활용해서 agent보고 이 메소드의 level_threshold를 정하라고 할 수도 있을 듯.
    아니면 일단 다 뽑아보고 뽑은 것 중에 ai보고 상황에 맞게 따로 선별하라고 하던가. 
    중요한 건, 유저의 응답 정보 및 맥락, 메모리 상황에 따라 이 레벨 threshold가 다르게 책정되어야 한다는 것. 
    즉, 유저의 현재 정보 수준, 관계도 등 환경적 요소에 따라 ai가 제공하는 정보의 레벨이 달라진다는 것!
    Docstring for search_memory
    
    :param collection_name: Description
    :param client: Description
    :param emb_model: Description
    :param query: Description
    :param top_k: Description
    :param level_threshold: Description
    '''

    # if query.type == dict:
    #     query = query["content"]

    result = genai.embed_content(
        model = "models/text-embedding-004",
        content=query,
        task_type = 'retrieval_query'
    )

    # query_vector = emb_model.encode(query).tolist()
    query_vector = result["embedding"]

    # 검색 필터 지정. level threshold 이하 레벨의 정보만 검색해오도록.
    query_filter = None
    if level_threshold != -1:
        query_filter = Filter(
            must = [
                FieldCondition(
                    key = "level",
                    range = Range(
                        lte = level_threshold
                    )
                )
            ]
        )
    
    # **RAG 검색**
    search_response = client.query_points(
        collection_name = collection_name,
        query = query_vector,
        query_filter = query_filter,
        limit = top_k,
        with_payload = True
    )
    
    # payload 정리 및 result list로 후처리
    results = []
    for hit in search_response.points:
        results.append({
            "score": hit.score,
            "level": hit.payload.get('level', ''),
            "type": hit.payload.get("type", ''),
            "content": hit.payload.get("content", ''),
            "scene_num": hit.payload.get("scene_num", '')
        })
    return results


def search_memory(collection_name, client, query, top_k = 5, level_threshold = -1):
    """
    Docstring for search_memory
    
    :param collection_name: Description
    :param client: Description
    :param emb_model: Description
    :param query: Description
    :param top_k: Description
    :param level_threshold: Description

    return 
    retrieved_mem: json type retrieved memory
    context: text type retrieved memory
    """
    # 검색 결과 받아오기
    retrieved_mem = get_rag_response(collection_name, client, query, top_k, level_threshold)
    print("==== retrieved memeory ====")
    print(retrieved_mem)

    # 검색 결과 후처리 (string)
    context_parts = []
    for i, memory in enumerate(retrieved_mem, 1):
        context_parts.append(f"[기억 {i}]")
        context_parts.append(f"level: {memory['level']}")
        context_parts.append(f"type: {memory['type']}")
        context_parts.append(f"content: {memory['content']}")
        context_parts.append(f"scene_num: {memory['scene_num']}")
    
    context = "\n".join(context_parts)
    return retrieved_mem, context
