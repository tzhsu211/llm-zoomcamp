import streamlit as st
import requests
from db import save_conversation, save_feedback, get_answer_data, get_recent_conversations, get_feedback_stats
from datetime import datetime
from ingestion import initialize_data
from dotenv import load_dotenv
from assistant import rag
import uuid

load_dotenv('../.env')

def print_log(message):
    print(message, flush=True)

def ask_question(question, is_vegan):
    answer_data = rag(question, is_vegan)
    conversation_id = st.session_state.conversation_id
    save_conversation(conversation_id, question, answer_data)
    return answer_data

def main():

    if "initialized" not in st.session_state:
        print_log("Starting initialize_data")
        initialize_data()
        st.session_state.initialized = True

    st.title("Supplement Expert")

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID-1: {st.session_state.conversation_id}")
    
    with st.form(key='question_form'):
        question = st.text_input("Question:")
        is_vegan = st.checkbox("I am a vegan!")
        submit_button = st.form_submit_button("Ask")

    if submit_button:
        with st.spinner("Processing..."):
            answer_data = ask_question(question, is_vegan)
            st.success("Completed!")

            # 调试信息，检查 answer_data
            st.write("Answer Data:", answer_data.answer)

    # if 'conversation_id' in st.session_state:
    #     st.subheader("Answer")
    #     st.write(st.session_state.answer)

    #     if not st.session_state.feedback_given:
    #         feedback = st.radio("Was the answer helpful?", (-1, 1), format_func=lambda x: "No" if x == -1 else "Yes")
    #         submit_feedback = st.button("Submit Feedback")

    #         if submit_feedback:
    #             if st.session_state.conversation_id:
    #                 save_feedback(st.session_state.conversation_id, feedback)
    #                 st.session_state.feedback_given = True
    #                 st.success("Feedback submitted!")
    #             else:
    #                 st.error("Error: No conversation ID found.")

    # st.subheader("Recent Conversations")
    # recent_conversations = get_recent_conversations(limit=5)
    # if recent_conversations:
    #     for convo in recent_conversations:
    #         st.write(f"**Question:** {convo['question']}")
    #         st.write(f"**Answer:** {convo['answer']}")
    #         st.write(f"**Feedback:** {convo['feedback']}")
    #         st.write("---")
    # else:
    #     st.write("No recent conversations found.")

    # st.subheader("Feedback Statistics")
    # feedback_stats = get_feedback_stats()
    # if feedback_stats:
    #     st.write(f"Thumbs Up: {feedback_stats['thumbs_up']}")
    #     st.write(f"Thumbs Down: {feedback_stats['thumbs_down']}")
    # else:
    #     st.write("No feedback data available.")

if __name__ == "__main__":
    main()
