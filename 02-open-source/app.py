import streamlit as st
import json
from elasticsearch import Elasticsearch
from openai import OpenAI

# loading doc
with open('documents.json', 'rt') as f:
    docs_raw= json.load(f)

documents = []

for course_dict in docs_raw:
    for doc in course_dict['documents']:
        doc['course'] = course_dict['course']
        documents.append(doc)

# build up model
client = OpenAI(
    base_url = 'http://localhost:11434/v1/',
    api_key = 'ollama',
)

# elasticsearch
es_client = Elasticsearch('http://localhost:9200')
index_setting = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} 
        }
    }
}
index_name = "course-questions"
#es_client.indices.create(index=index_name, body= index_setting)
for doc in documents:
    es_client.index(index=index_name, document=doc)


# build whole search def

def elastics_search(query):

    search_query ={
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": "data-engineering-zoomcamp"
                    }
                }
            }
        }
    }

    # search
    response = es_client.search(index= index_name, body= search_query)

    result_docs = []

    for hits in response['hits']['hits']:
        result_docs.append(hits['_source'])


    return result_docs

def build_prompt(query, result):

    prompt_temp = '''
    you're a course teaching assistant. Answer the QUESTION based on the CONTEXT.
    Use only the facts from the CONTEXT when answering the QUESTION.
    
    QUESTION: {question}
    
    CONTEXT:
    {context}
    '''.strip()
    
    context = ""

    for doc in result:
        context = context + f"section: {doc['section']}\nquestions: {doc['question']}\nanswer: {doc['text']}\n\n"

    prompt = prompt_temp.format(question = query, context = context).strip()

    return prompt

def llm(prompt):
    response = client.chat.completions.create(
        model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag_es(query, doc):

    search_result = elastics_search(query)
    prompt = build_prompt(query, search_result)
    answer = llm(prompt)

    return answer
    

# streamlit UI
def main():
    st.set_page_config(page_title = 'FAQ')
    st.title('Please ask me question.')

    user_input = st.text_input('Enter your question here:')

    if st.button('Ask'):
        with st.spinner('Processing...'):
            output = rag_es(user_input, doc)
            st.success('Completed!')
            st.write(output)

if __name__ == '__main__':
    main()


