import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv('../.env')

def get_db_connection():
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    print("Loaded environment variables:")
    print(f"POSTGRES_HOST: {POSTGRES_HOST}")
    print(f"POSTGRES_DB: {POSTGRES_DB}")
    print(f"POSTGRES_USER: {POSTGRES_USER}")
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def init_db():    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 先删除 feedback 表
            cur.execute("DROP TABLE IF EXISTS feedback;")
            # 然后删除 conversations 表
            cur.execute("DROP TABLE IF EXISTS conversations;")

            # 创建 conversations 表
            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    prompt_token_count INTEGER NOT NULL,
                    candidates_token_count INTEGER NOT NULL,
                    total_token_count INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)

            # 创建 feedback 表
            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)

        conn.commit()
    finally:
        conn.close()



def save_conversation(conversation_id, question, answer_data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations 
                    (id, question, answer, response_time,  
                    prompt_token_count, candidates_token_count, total_token_count, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    conversation_id,
                    question,
                    answer_data["answer"],
                    answer_data["response_time"],
                    answer_data["prompt_token_count"],
                    answer_data["candidates_token_count"],
                    answer_data["total_token_count"],
                    timestamp
                )
            )
            conn.commit()
    finally:
        conn.close()



def save_feedback(conversation_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (conversation_id, feedback, timestamp) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))",
                (conversation_id, feedback, timestamp),
            )
        conn.commit()
    finally:
        conn.close()


def get_recent_conversations(limit=5, relevance=None):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """

            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()

def get_answer_data(conversation_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM conversations
                WHERE id = %s
            """, (conversation_id,))
            result = cur.fetchone()
            if result:
                return dict(result)
            else:
                return None
    finally:
        conn.close()
