import streamlit as st
import pandas as pd
import random
import json
import os
import urllib.parse

# File for storing scores and questions
DATA_FILE = "game_scores.json"
QUESTIONS_FILE = "questions.json"

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = []
if "players" not in st.session_state:
    st.session_state.players = {}
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "completed_players" not in st.session_state:
    st.session_state.completed_players = set()
if "show_podium" not in st.session_state:
    st.session_state.show_podium = False
if "current_player" not in st.session_state:
    st.session_state.current_player = None  # Track current player
if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False  # Track if quiz is completed

# Load questions from file if session is empty
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    return []

# Save questions to file
def save_questions(questions):
    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f, indent=4)
        
# delete a question
def delete_question():
    st.title("Delete Question")
    question = st.selectbox("Select a question to delete", st.session_state.questions)
    if st.button("Delete Question"):
        st.session_state.questions.remove(question)
        save_questions(st.session_state.questions)
        st.success("Question deleted!")
        st.rerun()


# Ensure questions are loaded into session
if not st.session_state.questions:
    st.session_state.questions = load_questions()

# Load scores
def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=4)

scores = load_scores()

# Detect URL parameters
query_params = st.query_params
player_name = query_params.get("player", [None])[0]
url_page = query_params.get("page", [None])[0]

# Ensure session state updates when a new player clicks a link
if player_name and st.session_state.current_player != player_name:
    st.session_state.current_player = player_name  # Update session state
    st.rerun()  # Reload to ensure correct session

# Override navigation if player is accessing their quiz link
if player_name and not st.session_state.quiz_finished:
    page = "Player Quiz"
elif st.session_state.quiz_finished:
    page = "Quiz Finished"
else:
    page = st.sidebar.radio("Select Page", ["Add Questions", "Setup Players", "Player Links", "Results"])

def player_links():
    st.title("Player Links")
    base_url = "https://kahootclone.streamlit.app/"  # Change to your deployment URL
    for player in st.session_state.players.keys():
        player_url = base_url + "?page=Player_Quiz&player=" + urllib.parse.quote(player)
        st.write(f"{player}: [Click here]({player_url})")

# Page 1: Add Questions
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
        st.session_state.questions.append(new_question)
        save_questions(st.session_state.questions)  # Save questions to file
        st.success("Question added!")
    
    # preview the questions
    st.subheader("Preview Questions:")
    questions = load_questions()
    for i, question in enumerate(questions):
        with st.container():
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**{question['question']}**")
            for opt in question["options"]:
                if opt == question["correct"]:
                    st.markdown(f"✅ **{opt}**")
                else:
                    st.markdown(f"🔹 {opt}")
    # delete a question
    delete_question()
    

# Page 2: Setup Players
elif page == "Setup Players":
    st.title("Setup Players")
    num_players = st.number_input("Enter number of players:", min_value=1, value=2)
    
    players = {}
    for i in range(num_players):
        name = st.text_input(f"Enter name for Player {i+1}")
        if name:
            players[name] = 0  # Initialize score
    
    if st.button("Save Players"):
        st.session_state.players = players
        st.success("Players saved!")
    
    st.subheader("Current Players:")
    st.write(st.session_state.players)

# Page 3: Generate Player Links
elif page == "Player Links":
    player_links()
    
# Page 4: Player Quiz
elif page == "Player Quiz":
    st.title(f"Hello {player_name}! Your Quiz")
    
    questions = load_questions()
    for i, question in enumerate(questions):
        with st.container():
            st.markdown(f"### 🎯 Question {i+1}")
            st.markdown(f"**{question['question']}**")
            st.session_state.responses[player_name] = st.radio("Select your answer:", question["options"], key=f"{player_name}_{i}")
    
    if st.button("✅ Submit Answers"):
        score = 0
        for i, question in enumerate(questions):
            if st.session_state.responses.get(player_name) == question["correct"]:
                score += 1
        scores[player_name] = {"score": score, "current_question": len(questions)}
        save_scores(scores)
        st.session_state.quiz_finished = True
        st.rerun()

# Page 5: Quiz Finished
elif page == "Quiz Finished":
    st.title("🎉 Congratulations! 🎉")
    st.subheader("You have successfully completed the questionnaire!")
    st.markdown("Thank you for participating. Your responses have been recorded.")
    st.markdown("Click on **Results** in the sidebar to see the final scores!")

# Page 6: Results
elif page == "Results":
    st.title("Quiz Results")
    
    st.subheader("Questions & Answers:")
    questions = load_questions()
    for i, question in enumerate(questions):
        with st.container():
            st.markdown(f"### Question {i+1}")
            st.markdown(f"**{question['question']}**")
            for opt in question["options"]:
                if opt == question["correct"]:
                    st.markdown(f"✅ **{opt}**")
                else:
                    st.markdown(f"🔹 {opt}")
    
    st.subheader("Final Scores:")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    scores_df = pd.DataFrame([(p, s["score"]) for p, s in sorted_scores], columns=["Player", "Score"])
    st.dataframe(scores_df)
    
    if len(sorted_scores) >= len(st.session_state.players) and all(s["current_question"] >= len(st.session_state.questions) for _, s in sorted_scores):
        if st.button("📢 Show Winners"):
            st.session_state.show_podium = True
    
    if st.session_state.show_podium:
        st.balloons()
        st.markdown("<h2 style='color: #FFD700;'>🥇 Podium Winners 🥈🥉</h2>", unsafe_allow_html=True)
        if len(sorted_scores) > 0:
            st.markdown(f"🥇 **{sorted_scores[0][0]}** - {sorted_scores[0][1]['score']} points")
        if len(sorted_scores) > 1:
            st.markdown(f"🥈 **{sorted_scores[1][0]}** - {sorted_scores[1][1]['score']} points")
        if len(sorted_scores) > 2:
            st.markdown(f"🥉 **{sorted_scores[2][0]}** - {sorted_scores[2][1]['score']} points")
