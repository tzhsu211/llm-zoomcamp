import google.generationai as genai
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('../.env')

ELASTIC_URL = os.getenv("ELASTIC_URL")
GOOGLE_API = os.getenv("GOOGLE_API_KEY")

es_client = Elasticsearch(ELASTIC_URL)
ollama_client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
gemini = genai.GenerativeModel('gemini-pro', api_key = GOOGLE_API)

def hybrid_search(query: str, field: str, vegan: bool = False, boost: float = 0.7) -> List:

    query_v = model.encode(query)
    vector_field = field+'v'
    
    knn_search_hybird = {
        'field': vector_field,
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
                    'fields': field,
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
        '_source':['name', 'purpose', 'who_should_not_use', 'common_side_effects', 'vegan_friendly']       
    }

    response = es_client.search(index = es_index, body= search_query)

    result = []
    for hits in response['hits']['hits']:
        result.append(hits['_source'])
    return result


def build_prompt(query, search_results):
    prompt_template = """
You're a health supplement expert. Answer the QUESTION based on the CONTEXT from our health supplement database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    entry_template = """
name: {name}
purpose: {purpose}
who_should_not_use: {who_should_not_use}
common_side_effects: {common_side_effects}
recommended_dosage: {recommended_dosage}
source: {source}
vegan_friendly: {vegan_friendly}
""".strip()
    return prompt_template.format(question=query, context=context).strip()