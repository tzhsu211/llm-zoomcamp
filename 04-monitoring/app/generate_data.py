import time
import random
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from db import save_conversation, save_feedback, get_db_connection

# Set the timezone to CET (Europe/Berlin)
tz = ZoneInfo("Europe/Berlin")

# List of sample questions and answers
SAMPLE_QUESTIONS = [
    "What is machine learning?",
    "How does linear regression work?",
    "Explain the concept of overfitting.",
    "What is the difference between supervised and unsupervised learning?",
    "How does cross-validation help in model evaluation?",
]

SAMPLE_ANSWERS = [
    "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience.",
    "Linear regression is a statistical method used to model the relationship between a dependent variable and one or more independent variables by fitting a linear equation to observed data.",
    "Overfitting occurs when a machine learning model learns the training data too well, including its noise and fluctuations, resulting in poor generalization to new, unseen data.",
    "Supervised learning involves training models on labeled data, while unsupervised learning deals with finding patterns in unlabeled data without predefined outputs.",
    "Cross-validation is a technique used to assess how well a model will generalize to an independent dataset. It involves partitioning the data into subsets, training the model on a subset, and validating it on the remaining data.",
]

COURSES = ["machine-learning-zoomcamp", "data-engineering-zoomcamp", "mlops-zoomcamp"]
MODELS = ["ollama-insert"]
RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]

def generate_synthetic_data(start_time, end_time):
    current_time = start_time
    conversation_count = 0
    print(f"Starting historical data generation from {start_time} to {end_time}")
    while current_time < end_time:
        conversation_id = str(uuid.uuid4())
        question = random.choice(SAMPLE_QUESTIONS)
        answer = random.choice(SAMPLE_ANSWERS)
        course = random.choice(COURSES)
        model = random.choice(MODELS)
        relevance = random.choice(RELEVANCE)

        openai_cost = 0

        answer_data = {
            "answer": answer,
            "response_time": random.uniform(0.5, 5.0),
            "relevance": relevance,
            "relevance_explanation": f"This answer is {relevance.lower()} to the question.",
            "model_used": model,
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(50, 300),
            "total_tokens": random.randint(100, 500),
            "eval_prompt_tokens": random.randint(50, 150),
            "eval_completion_tokens": random.randint(20, 100),
            "eval_total_tokens": random.randint(70, 250),
            "openai_cost": openai_cost
        }

        save_conversation(
            conversation_id = conversation_id,
            timestamp=current_time,
            question=question,
            answer_data=answer_data,
            course=course,
            model=model
        )

        current_time += timedelta(minutes=random.randint(5, 15))
        conversation_count += 1

    print(f"Generated {conversation_count} conversations.")

def generate_feedback_data(start_time, end_time):
    current_time = start_time
    feedback_count = 0
    print(f"Starting feedback data generation from {start_time} to {end_time}")
    while current_time < end_time:
        feedback_id = str(uuid.uuid4())
        conversation_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        feedback = random.choice(RELEVANCE)
        timestamp = current_time

        save_feedback(
            feedback_id,
            conversation_id,
            user_id,
            feedback,
            timestamp
        )

        current_time += timedelta(minutes=random.randint(5, 15))
        feedback_count += 1

    print(f"Generated {feedback_count} feedback entries.")

if __name__ == "__main__":
    start_time = datetime.now(tz) - timedelta(days=30)
    end_time = datetime.now(tz)
    generate_synthetic_data(start_time, end_time)
    generate_feedback_data(start_time, end_time)
