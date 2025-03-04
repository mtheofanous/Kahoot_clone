import streamlit as st
import pandas as pd
import random
import json
import os
import urllib.parse
import time 

st.set_page_config(
    page_title="Quiz",
    page_icon="🔵",
    layout="centered" 
)

# File for storing scores and questions
DATA_FILE = "game_scores.json"
QUESTIONS_FILE = "questions.json"
PLAYERS_FILE = "players.json"

TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
# display in the left corner
col1, col2 = st.columns([4, 2])
with col2:
    st.image(TELADOC_LOGO, width=400)


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
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0  # Track the current question number

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
    st.sidebar.title("Delete Question")
    question = st.sidebar.selectbox("Select a question to delete", st.session_state.questions)
    if st.sidebar.button("Delete Question"):
        st.session_state.questions.remove(question)
        save_questions(st.session_state.questions)
        st.success("Question deleted!")
        st.rerun()


# Ensure questions are loaded into session
if not st.session_state.questions:
    st.session_state.questions = load_questions()
    
# save players
def save_players(players):
    with open(PLAYERS_FILE, "w") as f:
        json.dump(st.session_state.players, f, indent=4)
        
# load players
def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r") as f:
            return json.load(f)
    return {}

# delete a player
def delete_player():
    st.title("Delete Player")
    player = st.selectbox("Select a player to delete", st.session_state.players)
    if st.button("Delete Player"):
        del st.session_state.players[player] 
        save_players(st.session_state.players)
        st.success("Player deleted!")
        st.rerun()

# Load scores
def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=4)
        
import streamlit as st

def reset_game():
    # Ensure all session state attributes are initialized
    if "scores" not in st.session_state:
        st.session_state.scores = {}  # Initialize scores if it doesn't exist
    
    st.session_state.questions = []
    st.session_state.players = {}
    st.session_state.responses = {}
    st.session_state.completed_players = set()
    st.session_state.show_podium = False
    st.session_state.current_player = None
    st.session_state.quiz_finished = False
    st.session_state.current_question_index = 0
    
    # Save state
    save_questions(st.session_state.questions)
    save_players(st.session_state.players)
    save_scores(st.session_state.scores)
    
    st.success("Game reset successfully!")
    st.rerun()


scores = load_scores()


# Detect URL parameters
query_params = st.query_params
player_name = query_params.get("player", [None])[0]
url_page = query_params.get("page", [None])[0]

# Ensure session state updates when a new player clicks a link
if player_name and st.session_state.current_player != player_name:
    st.session_state.current_player = player_name  # Update session state
    st.session_state.current_question_index = 0  # Reset question index for new player
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
    base_url = "https://kahootclone.streamlit.app/" #http://localhost:8501/   # Change to your deployment URL
    for player in st.session_state.players.keys():
        with st.container(border=True):
            player_url = base_url + "?page=Player_Quiz&player=" + urllib.parse.quote(player)
            st.write(f"{player}: [Click here]({player_url})")
            # show the player link
            st.write(f"Send Link: {player_url}")
 
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
    with st.expander("Click to preview questions"):
        # Splitting questions into two columns
        col1, col2 = st.columns(2)

        for i, question in enumerate(questions):
            # Alternate placement of questions in columns
            col = col1 if i % 2 == 0 else col2
            with col:
                with st.container(border=True):
                    st.markdown(f"<h3 style='color:#662D91;'>Question {i+1}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**{question['question']}**")
                    for opt in question["options"]:
                        if opt == question["correct"]:
                            st.markdown(f"✅ **{opt}**")
                        else:
                            st.markdown(f"🔹 {opt}")
    # delete a question
    delete_question()
    # Reset the game
    if st.sidebar.button("🔄 Reset Game"):
        reset_game()
    

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
        save_players(players)
        st.success("Players saved!")
    
    st.subheader("Current Players:")
    for player in st.session_state.players:
        with st.container(border=True):
            st.write(player)
    
    # delete a player
    delete_player()
    

# Page 3: Generate Player Links
elif page == "Player Links":
    player_links()
    
# Page 4: Player Quiz
elif page == "Player Quiz":
    st.title(f"Hello {player_name}! Your Quiz")
    
    questions = load_questions()
    total_questions = len(questions)
    current_question = st.session_state.current_question_index
    if current_question < total_questions:
        question = questions[current_question]
        st.markdown(f"<h3 style='color:#662D91;'>Question {current_question+1}/{total_questions}</h3>", unsafe_allow_html=True)
        st.markdown(f"**{question['question']}**")
        with st.container(border=True):
            st.session_state.responses[player_name] = st.radio("Select your answer:", question["options"], key=f"{player_name}_{current_question}")
        
        if st.button("✅ Submit Answer"):
  
            if st.session_state.responses.get(player_name) == question["correct"]:
                scores[player_name] = scores.get(player_name, 0) + 1
            st.session_state.current_question_index += 1
            save_scores(scores)
            st.rerun()
    else:
        st.title("🎉 Quiz Completed!"
                 f"Thank you for participating, {player_name}!")
        st.markdown("Your responses have been recorded.")
        st.session_state.quiz_finished = True
        st.rerun()
    

# Page 5: Quiz Finished
elif page == "Quiz Finished":
    st.title("🎉 Congratulations! 🎉")
    st.subheader("You have successfully completed the questionnaire!")
    st.markdown("Thank you for participating. Your responses have been recorded.")
    st.markdown("Click on **Results** in the sidebar to see the final scores!")

elif page == "Results":
    st.title("Quiz Results")
    
    st.subheader("Questions & Answers:")
    questions = load_questions()
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1} - {question['question']}"):
            for opt in question["options"]:
                if opt == question["correct"]:
                    st.markdown(f"✅ **{opt}**")
                else:
                    st.markdown(f"🔹 {opt}")
                    
    st.subheader("Final Scores:")
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    scores_df = pd.DataFrame([(p, s) for p, s in sorted_scores], columns=["Player", "Score"])

    # if len(sorted_scores) >= len(st.session_state.players):
    if st.button("📢 Show Winners"):
#         st.session_state.show_podium = True    
# if st.session_state.show_podium:
        st.balloons()
        c = st.columns([1, 1, 1, 4, 1, 1])
        c[3].markdown("<h2 style='color: #FFD700;'>Podium Winners</h2>", unsafe_allow_html=True)
        columna = st.columns(3)
        col = st.columns(4)
        if len(sorted_scores) > 0:
            with columna[1].container(border=True):
                st.markdown(f"<h4>🥇 {sorted_scores[0][0]}</h4>", unsafe_allow_html=True)
        if len(sorted_scores) > 1:
            with col[1].container(border=True):
                st.markdown(f"<h4>🥈 {sorted_scores[1][0]}</h4>", unsafe_allow_html=True)
        if len(sorted_scores) > 2:
            with col[2].container(border=True):
                st.markdown(f"<h4>🥉 {sorted_scores[2][0]}</h4>", unsafe_allow_html=True)
        # show all players ranking
        st.subheader("All Players Ranking:")
        for i, (player, score) in enumerate(sorted_scores):
            st.write(f"{i+1}. {player} - {score} points")
        # st.write(sorted_scores)
        st.write("🏁 Thank you for playing! 🏁")

        

if __name__ == "__main__":
    pass
