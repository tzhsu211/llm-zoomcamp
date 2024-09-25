import google.generativeai as genai
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict
from time import time

load_dotenv('../.env')

ELASTIC_URL = os.getenv("ELASTIC_URL")
GOOGLE_API = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

es_client = Elasticsearch(ELASTIC_URL)

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
genai.configure(api_key= GOOGLE_API)
gemini = genai.GenerativeModel('gemini-pro')

prompt_template = """
You're a health supplement expert. Answer the QUESTION based on the CONTEXT from our health supplement database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

context_template = """
name: {name}
purpose: {purpose}
who_should_not_use: {who_should_not_use}
common_side_effects: {common_side_effects}
recommended_dosage: {recommended_dosage}
source: {source}
vegan_friendly: {vegan_friendly}
""".strip()

def hybrid_search(query: str, vegan: bool = False, boost: float = 0.7) -> List:

    query_v = model.encode(query)
    
    knn_search_hybird = {
        'field': 'combinev',
        'query_vector' :query_v,
        'k':5,
        'num_candidates': 10000,
        'boost': boost,
    }

    keyword_search_hybrid = {
        'bool':{
            'must':{
                'multi_match':{
                    'query': query,
                    'fields': 'combine',
                    'type':'best_fields',
                    'boost': 1-boost
                }
            }
        }
    }

    if vegan:
        knn_search_hybird['filter'] = {
            'term':{
                'vegan_friendly': True
            }
        }

        keyword_search_hybrid['bool']['filter'] ={
            'term':{
                'vegan_friendly': True
            }
        }
    

    search_query = {
        'knn': knn_search_hybird,
        'query':keyword_search_hybrid,
        'size':5,
        '_source':['name', 'purpose', 'who_should_not_use', 'common_side_effects', 'recommended_dosage', 'source', 'vegan_friendly']       
    }

    response = es_client.search(index = INDEX_NAME, body= search_query)

    result = []
    for hits in response['hits']['hits']:
        result.append(hits['_source'])
    return result


def build_prompt(query, search_result):

    context = ""

    for doc in search_result:
        context += context_template.format(**doc) + "\n\n"

    print('ZZZZZZZZZ',GOOGLE_API)
    return prompt_template.format(question = query, context = context).strip()

def llm(prompt):
    response = gemini.generate_content(prompt)
    return response


def rag(query, vegan):

    t0 = time()

    search_result = hybrid_search(query, vegan)
    prompt = build_prompt(query, search_result)
    response = llm(prompt)

    t1 = time()

    time_spent = t1 - t0

    answer_data = {
        'answer':response.text,
        'response_time': time_spent,
        'prompt_token_count': response.usage_metadata.prompt_token_count,
        'candidates_token_count': response.usage_metadata.candidates_token_count,
        'total_token_count': response.usage_metadata.total_token_count
    }

    return answer_data