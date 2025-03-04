import streamlit as st
import pandas as pd
import json
import os
import urllib.parse

# Set Teladoc Health theme
st.set_page_config(
    page_title="Teladoc Health Quiz",
    page_icon="🔵",
    layout="centered",
)

# Load Teladoc Health logo
TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"

# Display logo and title
st.image(TELADOC_LOGO, width=200)
st.markdown("<h1 style='color:#0057B8; text-align:center;'>Teladoc Health Quiz</h1>", unsafe_allow_html=True)

# File storage
QUESTIONS_FILE = "questions.json"

# Load questions
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    return []

# Save questions
def save_questions(questions):
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f, indent=4)

# Page: Add Questions
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Add Questions", "Preview Questions"])

if page == "Add Questions":
    st.title("Add Questions")
    question = st.text_input("Enter the question:")
    options = [st.text_input(f"Option {i+1}") for i in range(4)]
    correct_answer = st.selectbox("Select the correct answer:", options)

    if st.button("Add Question"):
        new_question = {
            "question": question,
            "options": options,
            "correct": correct_answer
        }
        questions = load_questions()
        questions.append(new_question)
        save_questions(questions)
        st.success("Question added!")

# Page: Preview Questions
elif page == "Preview Questions":
    st.title("Preview Questions")
    questions = load_questions()
    
    if not questions:
        st.warning("No questions available.")
    else:
        col1, col2 = st.columns(2)
        
        for i, question in enumerate(questions):
            col = col1 if i % 2 == 0 else col2
            with col:
                with st.container():
                    st.markdown(f"<h3 style='color:#662D91;'>Question {i+1}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**{question['question']}**")
                    for opt in question["options"]:
                        if opt == question["correct"]:
                            st.markdown(f"✅ **{opt}**")
                        else:
                            st.markdown(f"🔹 {opt}")
