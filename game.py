import streamlit as st
import json
from urllib.parse import quote
from players import *
from questions import *
from player_links import *

def save_scores():
    with open("scores.json", "w") as f:
        json.dump(st.session_state.scores, f, indent=4)
        
def load_scores():
    if not st.session_state.scores:
        try:
            with open("scores.json", "r") as f:
                st.session_state.scores = json.load(f)
        except FileNotFoundError:
            st.session_state.scores = {}
            
# every link is seeing the questions and options and selecting one answer
def game():
    st.title("Game")
    if st.session_state.player is None:
        st.session_state.player = st.session_state.players[0]
        st.session_state.player_questions = {player: 0 for player in st.session_state.players}
        
    player = st.session_state.player
    st.write(f"Player: {player}")
    
    if player not in st.session_state.completed_players:
        question_idx = st.session_state.player_questions[player]
        question = st.session_state.questions[question_idx]
        st.write(question["question"])
        for opt in question["options"]:
            st.write(opt)
        
        answer = st.selectbox("Select your answer:", question["options"])
        st.session_state.responses[player] = answer
        st.session_state.completed_players.add(player)
        
    if st.button("Next"):
        st.session_state.player = None
        st.rerun()
        
    if len(st.session_state.completed_players) == len(st.session_state.players):
        st.session_state.show_podium = True
        st.session_state["current_page"] = "results"
        save_scores()
        st.rerun()
    