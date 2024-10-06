import streamlit as st
import requests
from db import save_conversation, save_feedback, get_recent_conversations, get_feedback_stats
from datetime import datetime
from ingestion import initialize_data
from dotenv import load_dotenv
from typing import List, Dict
from assistant import rag
import uuid

load_dotenv('../.env')

def print_log(message: str):
    print(message, flush=True)

def ask_question(llm_model:str, question: str, api, is_vegan: bool = False):
    # Generate and save question to db
    try:
        print_log(f"rag func: llm model: {llm_model}, query: {question}, is vegan: {is_vegan}, api: {api}")
        answer_data = rag(llm_model, question, is_vegan, api) 
        print_log(answer_data)
        conversation_id = st.session_state.conversation_id
        save_conversation(conversation_id, question, answer_data, llm_model)
    
        return answer_data
    
    except Exception as e:
        st.error("An error occurred while fetching the answer.")
        print_log(f"Error: {e}")
    
        return None

def send_feedback(conversation_id: str, feedback: bool):
    # save feedback to db. for each question, feedback can only be sent once and st.sesion_state will change.
    if feedback:
       save_feedback(conversation_id, 1)
       st.session_state.feedback_given = True
    else:
        save_feedback(conversation_id, -1)
        st.session_state.feedback_given = True


def main():

    if "initialized" not in st.session_state:
        print_log("Starting initialize_data")
        initialize_data()
        st.session_state.initialized = True 
        
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(f"New conversation started with ID: {st.session_state.conversation_id}")

    if "answer_data" not in st.session_state:
        st.session_state.answer_data = None
        print_log("answer_data is set to None.")

    st.title("Supplement Expert💊")
    
    # set up the outline of streamlit form
    with st.form(key='question_form'):
        st.subheader("How may I assist you today?")
        # question text box
        question = st.text_input("Question:")
        # is_vegan checkbox
        is_vegan = st.checkbox("I am a vegan!")
        # model selection
        llm_model = st.selectbox(
            "LLM model:",
            [ "Ollama phi3", "Google Gemini pro"]
        )
        api = st.text_input("Please input LLM API:",key="chatbot_api_key", type="password")
        submit_button = st.form_submit_button("🔍")


    if submit_button:

        if not question:
            st.warning("Please enter a question before submitting.")

        elif llm_model != "Ollama phi3" and not api:
            st.warning("Please provide LLM api.")

        else:

            with st.spinner("Processing..."):
                print_log(f"model selected: {llm_model}, api: {api}, ")

                st.session_state.conversation_id = str(uuid.uuid4())
                answer_data = ask_question(llm_model, question, api, is_vegan)
                st.session_state.answer_data = answer_data
                st.success("Completed!")
            
                # write info
                st.write("Answer:", answer_data['answer'])
                st.write("Conversation id:", st.session_state.conversation_id)
                st.write("Response time:", answer_data['response_time'])
                st.write("Prompt token count::", answer_data['prompt_token_count'])
                st.write("Candidates token count:", answer_data['candidates_token_count'])
                st.write("Total token count:", answer_data['total_token_count'])

                # init feedback state when ask button triggered
                st.session_state.feedback_given = False 

    # feedback buttons
    if st.session_state.conversation_id and st.session_state.answer_data:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍") and not st.session_state.feedback_given:
                send_feedback(st.session_state.conversation_id, True)

        with col2:
            if st.button("👎") and not st.session_state.feedback_given:
                send_feedback(st.session_state.conversation_id, False)
        
        if st.session_state.feedback_given:
            st.write("Feedback is sent. Thank you.")

    
    st.subheader("Recent Conversations")
    recent_conversations = get_recent_conversations()

    if recent_conversations:

        for convo in recent_conversations:

            st.write(f"**Question:** {convo['question']}")
            st.write(f"**Answer:** {convo['answer']}")

            if convo['feedback'] ==1:
                st.write("**Feedback:** 👍")
            elif convo['feedback'] ==-1:
                st.write("**Feedback:** 👎")

            st.write(f"**Model:** {convo['model']}")
            st.write(f"**Time Stamp:** {convo['timestamp']}")
            st.write("---")
    else:
        st.write("No recent conversations found.")

    st.subheader(" User Feedback Statistics")
    feedback_stats = get_feedback_stats()

    if feedback_stats:
        st.write(f"👍: {feedback_stats['thumbs_up']}")
        st.write(f"👎: {feedback_stats['thumbs_down']}")
    else:
        st.write("No feedback data available.")

if __name__ == "__main__":
    main()
