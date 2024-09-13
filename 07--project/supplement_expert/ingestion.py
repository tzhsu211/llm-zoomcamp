import os
import requests
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import json

from db import init_db

load_dotenv('../.env')

ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

def load_model():
    print(f"Loading model: {MODEL_NAME}")
    return SentenceTransformer(MODEL_NAME)

def fetch_documents():
    print("Fetching documents...")
    try:
        relative_url = "https://raw.githubusercontent.com/tzhsu211/llm-zoomcamp/main/07--project/data/supplement.json"
        docs_response = requests.get(relative_url)

        # Check the status code
        if docs_response.status_code == 200:
            try:
                documents = docs_response.json()  
                print(f"Fetched {len(documents)} documents")
            except ValueError as e:
                # Handle JSON decoding error
                print(f"Error decoding JSON: {e}")
                documents = []
        else:
            print(f"Failed to fetch documents: HTTP {docs_response.status_code}")
            documents = []
    
    except Exception as e:
        print(f"Error fetching documents: {e}")
        documents = []

    return documents



def fetch_ground_truth():
    print("Fetching ground truth data...")
    try:
        ground_truth_url = "https://raw.githubusercontent.com/tzhsu211/llm-zoomcamp/main/07--project/data/supplement_extended_question_gpt.json"
        ground_truth_js = requests.get(ground_truth_url)
        ground_truth = ground_truth_js.json()  
        print(f"Fetched {len(ground_truth)} documents")

    except Exception as e:
        print(f"Error fetching documents: {e}")
        ground_truth = []    

    return ground_truth



def setup_elasticsearch():
    print("Setting up Elasticsearch...")
    es_client = Elasticsearch(ELASTIC_URL)

    index_settings = {
        'settings':{
            'number_of_shards':1,
            'number_of_replicas':0
        },
        'mappings':{
            'properties':{
                'name':{'type':'keyword'},
                'purpose':{'type':'text'},
                'who_should_not_use':{'type':'text'},
                'common_side_effects':{'type':'text'},
                'recommended_dosage':{'type':'text'},
                'source':{'type':'keyword'},
                'vegan_friendly':{'type':'boolean'},
                'combine':{'type':'text'},
                'purposev':{'type':'dense_vector',
                            'dims':384,
                            'index': True,
                            'similarity': 'cosine'
                            },
                'who_should_not_usev':{'type':'dense_vector',
                            'dims':384,
                            'index': True,
                            'similarity': 'cosine'
                            },
                'common_side_effectsv':{'type':'dense_vector',
                            'dims':384,
                            'index': True,
                            'similarity': 'cosine'
                            },
                'combinev':{'type':'dense_vector',
                            'dims':384,
                            'index': True,
                            'similarity': 'cosine'
                            }
                
            }
        }
    }

    es_client.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    es_client.indices.create(index=INDEX_NAME, body=index_settings)
    print(f"Elasticsearch index '{INDEX_NAME}' created")
    return es_client


def index_documents(es_client, documents, model):
    print("Indexing documents...")
    combine = "purpose: {purpose}, who should not use: {who_should_not_use}, common side effect: {common_side_effects}"
    for doc in documents:
        doc['combine'] = combine.format(**doc)
        doc['combinev'] = model.encode(doc['combine'])
        doc['purposev'] = model.encode(doc['purpose'])
        doc['who_should_not_usev'] = model.encode(doc['who_should_not_use'])
        doc['common_side_effectsv'] = model.encode(doc['common_side_effects'])
        es_client.index(index=INDEX_NAME, document=doc)
    print(f"Indexed {len(documents)} documents")


def main():
    # you may consider to comment <start>
    # if you just want to init the db or didn't want to re-index
    print("Starting the indexing process...")

    documents = fetch_documents()
    ground_truth = fetch_ground_truth()
    model = load_model()
    es_client = setup_elasticsearch()
    index_documents(es_client, documents, model)
    # you may consider to comment <end>

    print("Initializing database...")
    init_db()

    print("Indexing process completed successfully!")


if __name__ == "__main__":
    main()