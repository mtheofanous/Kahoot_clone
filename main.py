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

# Function to save players
def save_players(players):
    with open("players.json", "w") as f:
        json.dump(players, f, indent=4)

# Function to load players
def load_players():
    if os.path.exists("players.json"):
        with open("players.json", "r") as f:
            return json.load(f)
    return {}

# Ensure players are loaded into session
if not st.session_state.players:
    st.session_state.players = load_players()

# Function to delete a player
def delete_player():
    st.title("Delete Player")
    if st.session_state.players:
        player = st.selectbox("Select a player to delete", list(st.session_state.players.keys()))
        if st.button("Delete Player"):
            del st.session_state.players[player]
            save_players(st.session_state.players)
            st.success(f"Player {player} deleted!")
            st.rerun()
    else:
        st.warning("No players to delete.")

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

# Page 6: Results
if page == "Results":
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