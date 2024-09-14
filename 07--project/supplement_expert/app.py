from flask import Flask, request, render_template, redirect, url_for
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
import json
from dotenv import load_dotenv
from db import save_conversation, save_feedback, get_answer_data

load_dotenv('../.env')

app = Flask(__name__)

# initalize elasticsearch and embedding model
ELASTIC_URL = os.getenv("ELASTIC_URL_LOCAL")
MODEL_NAME = os.getenv("MODEL_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

es_client = Elasticsearch(ELASTIC_URL)
model = SentenceTransformer(MODEL_NAME)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        question = request.form.get('question')
        is_vegan = request.form.get('vegan') == 'on'

        # ask question nand vegan (default is false)
        answer_data = ask_question(question, is_vegan)

        # save conversation
        save_conversation(
            conversation_id=answer_data['conversation_id'],
            question=question,
            answer_data=answer_data
        )

        # 重定向回首頁，並附帶 conversation_id 查詢參數
        return redirect(url_for('index', conversation_id=answer_data['conversation_id']))

    conversation_id = request.args.get('conversation_id')
    question = ""
    answer = ""
    if conversation_id:
        # 根據 conversation_id 從資料庫取得相關資訊
        answer_data = get_answer_data(conversation_id)
        question = answer_data['question']
        answer = answer_data['answer']

    return render_template('index.html', question=question, answer=answer, conversation_id=conversation_id)

@app.route('/feedback/<conversation_id>', methods=['POST'])
def feedback(conversation_id):
    feedback_value = int(request.form.get('feedback'))
    save_feedback(conversation_id, feedback_value)
    return redirect(url_for('index'))

def ask_question(question, is_vegan):
    # 這裡是模擬對問題進行處理的部分
    # 實際應用中，這部分應該連接到 Elasticsearch 和 LLM
    answer_data = {
        "conversation_id": "some_unique_id",  # 這裡需要生成唯一的 ID
        "answer": "This is a mock answer",
        "response_time": 0.5,
        "relevance": "high",
        "relevance_explanation": "Highly relevant",
        "prompt_tokens": 10,
        "completion_tokens": 15,
        "total_tokens": 25,
        "eval_prompt_tokens": 5,
        "eval_completion_tokens": 7,
        "eval_total_tokens": 12
    }
    return answer_data

if __name__ == '__main__':
    app.run(debug=True)
