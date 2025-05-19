import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
import time
import datetime
import random
import string
import requests

# Custom Teladoc CSS styles
st.markdown("""
    <style>
    .big-button {
        display: block;
        width: 100%;
        padding: 20px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        background-color: #E9E4F6;  /* Teladoc light purple */
        border: 2px solid #662D91;  /* Teladoc purple */
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
        color: #4B2991;
    }
    .big-button:hover {
        background-color: #d1c7ea;
    }
    </style>
""", unsafe_allow_html=True)


# File paths
DATA_FILE = "game_scores.json"
QUESTIONS_FILE = "questions.json"
PLAYERS_FILE = "players.json"
ANSWERS_FILE = "answers.json"
QUESTION_SETS_DIR = "question_sets"
GAMES_FILE = "games.json"
HISTORY_FILE = "game_history.json"



if not os.path.exists(QUESTION_SETS_DIR):
    os.makedirs(QUESTION_SETS_DIR)

    
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


def generate_game_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def save_game_history(game_id, questions, answers, scores):
    history = {}

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}

    history[game_id] = {
        "questions": questions,
        "answers": answers.get(game_id, {}),
        "scores": scores.get(game_id, {})
    }

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


# Function to save the current question set to a custom file
def save_question_set(filename):
    filepath = os.path.join(QUESTION_SETS_DIR, filename + ".json")
    with open(filepath, "w") as f:
        json.dump(st.session_state.questions, f, indent=4)
    st.success(f"Question set saved as '{filename}.json'")

# Function to load a question set from a custom file
def load_question_set(filename):
    filepath = os.path.join(QUESTION_SETS_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File '{filename}' not found.")
        return []
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from '{filename}'. Ensure the file is correctly formatted.")
        return []

# Load questions from file if session is empty
def load_questions():
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_game_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


def save_questions(questions):

    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f, indent=4)
        
    
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
    st.title("🗑 Remove Player")
    player = st.selectbox("Select a player to delete", st.session_state.players, label_visibility="collapsed")
    if st.button("🗑 Remove Player"):
        try:
            del st.session_state.players[player] 
            save_players(st.session_state.players)
            st.success("Player deleted!")
            st.rerun()
        except KeyError:
            st.error("Player not found.")
            
def delete_question_set(filename):
    filepath = os.path.join(QUESTION_SETS_DIR, filename)
    try:
        os.remove(filepath)
        st.success(f"'{filename}' deleted successfully!")
        time.sleep(1)
        st.rerun()
    except FileNotFoundError:
        st.error("File not found.")
    except Exception as e:
        st.error(f"Error deleting file: {str(e)}")


# Load scores
def load_scores():
    all_scores = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            all_scores = json.load(f)

    game_id = st.session_state.get("game_id", "default")
    return all_scores.get(game_id, {})


def save_scores(scores):
    all_scores = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            all_scores = json.load(f)

    game_id = st.session_state.get("game_id", "default")
    all_scores[game_id] = scores  # Save scores under this game

    with open(DATA_FILE, "w") as f:
        json.dump(all_scores, f, indent=4)
        
# Function to load answers
def load_answers():
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r") as f:
            data = json.load(f)
            # Ensure timestamp exists
            for game_id in data:
                for player in data[game_id]:
                    for q in data[game_id][player]:
                        if "timestamp" not in data[game_id][player][q]:
                            data[game_id][player][q]["timestamp"] = "9999-12-31T23:59:59"
            return data
    return {}

# Function to save answers
def save_answers(answers):
    with open(ANSWERS_FILE, "w") as f:
        json.dump(answers, f, indent=4)
        
answers = load_answers()

# Ensure answers are initialized in session state
if "answers" not in st.session_state:
    st.session_state.answers = answers
    
def reset_questions_only():
    st.session_state.questions = []
    save_questions([])  # Overwrite the saved file
    st.success("Questions reset successfully!")
    time.sleep(1)
    st.rerun()
    

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
    st.session_state.answers = {}
    st.session_state.scores = {}
    
    # Save state
    save_questions(st.session_state.questions)
    save_players(st.session_state.players)
    save_scores(st.session_state.scores)
    save_answers(st.session_state.answers)
    
    st.success("Game reset successfully!")
    time.sleep(1.5)
    st.rerun()

scores = load_scores()


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
if 'game' not in st.session_state:
    st.session_state.game = False
    

def login_page():
    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"

    st.markdown("""
        <style>
        .login-header {
            font-size: 36px;
            color: #4B2991;
            font-weight: bold;
            margin-top: 20px;
        }
        .login-sub {
            font-size: 18px;
            color: #555;
            margin-bottom: 30px;
        }
        .stTextInput>div>div>input {
            font-size: 18px;
            padding: 10px;
        }
        .stButton>button {
            background-color: #662D91;
            color: white;
            font-size: 18px;
            padding: 10px 20px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background-color: #4B2991;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([0.5, 3, 0.5])
    with col2:

        st.image(TELADOC_LOGO, width=250)

        st.markdown('<div class="login-header">Welcome to the Teladoc Quiz!</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Think you know it all? Let\'s find out!</div>', unsafe_allow_html=True)

        game_id_input = st.text_input("🔑 Enter Game ID", max_chars=10).upper()

        if st.button("🚀 Join Game"):
            if game_id_input == 'TELADOC':
                st.session_state.logged_in = 'admin'
                st.rerun()
            elif game_id_input:
                if os.path.exists(GAMES_FILE):
                    try:
                        with open(GAMES_FILE, "r") as f:
                            games_data = json.load(f)
                    except json.JSONDecodeError:
                        st.error("Error loading games data.")  # << this line was missing
                        return
                else:
                    st.error("No games found.")
                    return

                if game_id_input in games_data:
                    st.session_state.logged_in = 'player'
                    st.session_state.game_id = game_id_input
                    st.session_state.current_question_index = 0
                    st.session_state.questions = games_data[game_id_input].get("questions", [])
                    st.rerun()
                else:
                    st.error("❌ No game found with this Game ID.")
            else:
                st.error("Please enter a valid Game ID to proceed.")


def player_page():
    st.title("Welcome to Teladoc Game")

    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    col1, col2 = st.columns([4, 3])
    with col2:
        st.image(TELADOC_LOGO, width=300)

    player = st.text_input("Your Name", max_chars=40)

    if st.button("🎮 Start Quiz"):
        if not player:
            st.error("Please enter a name.")
            return

        if "game_id" not in st.session_state:
            st.error("Game ID not found. Please join through a valid game link.")
            return

        game_id = st.session_state.game_id

        # Load existing players
        existing_players = {}
        if os.path.exists(PLAYERS_FILE):
            with open(PLAYERS_FILE, "r") as f:
                existing_players = json.load(f)

        if game_id not in existing_players:
            existing_players[game_id] = {}

        if player in existing_players[game_id]:
            st.error("This name is already taken for this game. Please choose another one.")
        else:
            existing_players[game_id][player] = {}

            with open(PLAYERS_FILE, "w") as f:
                json.dump(existing_players, f, indent=4)

            st.session_state.current_player = player
            st.session_state.game = 'start_game'
            st.rerun()

 
def start_game():
    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    col1, col2 = st.columns([4, 3])
    with col2:
        st.image(TELADOC_LOGO, width=300)
    countdown_placeholder = st.empty()

    if "countdown_done" not in st.session_state:
        for i in range(5, 0, -1):
            countdown_placeholder.markdown(f"<h1 style='text-align:center; font-size:80px;'>{i}</h1>", unsafe_allow_html=True)
            time.sleep(1)
        countdown_placeholder.markdown("<h1 style='text-align:center; font-size:80px;'>Go!</h1>", unsafe_allow_html=True)
        time.sleep(1)
        st.session_state.countdown_done = True
        st.rerun()
    else:
        question_page()
        

def question_page():
    player = st.session_state.current_player
    game_id = st.session_state.get("game_id", "default")

    questions = st.session_state.get("questions", [])
    total_questions = len(questions)
    current_index = st.session_state.get("current_question_index", 0)

    if current_index >= total_questions:
        final_score = load_scores().get(game_id, {}).get(player, 0)
        all_answers = st.session_state.answers
        all_scores = load_scores()
        questions = st.session_state.questions

        # Save history so it shows in the dashboard
        save_game_history(
            game_id=game_id,
            questions=questions,
            answers=all_answers,
            scores=all_scores
        )

        st.balloons()
        st.markdown(f"""
            <div style="background-color:#E9E4F6; padding:30px; border-radius:20px; text-align:center; margin-top:50px;">
                <h2 style="color:#4B2991;">🎉 ¡Felicidades, {player}! 🎉</h2>
                <p style="font-size:20px;">Has completado el quiz de Teladoc Health.</p>
                <p style="font-size:22px;"><strong>Tu puntuación final:</strong> <span style="color:#00B1E1;">{final_score} puntos</span></p>
                <hr style="margin: 20px 0;">
                <p style="font-size:18px;">🏅 Si esto fuera una consulta médica... ¡serías el/la doctor/a en jefe!</p>
                <p style="font-size:18px;">🧠 Tu conocimiento Teladoc está más fuerte que una taza doble de café ☕</p>
                <p style="font-size:16px; color:#555;">Comparte tu resultado con el equipo y reta a tus compañeros.</p>
            </div>
        """, unsafe_allow_html=True)
        return


    question = questions[current_index]
    st.markdown(f"""
        <style>
        .question-card {{
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            margin-top: 40px;
        }}
        .progress-bar {{
            height: 20px;
            border-radius: 10px;
            background-color: #E9E4F6;
            overflow: hidden;
            margin-top: 20px;
            margin-bottom: 20px;
        }}
        .progress-bar-fill {{
            height: 100%;
            width: {100 * (current_index + 1) // total_questions}%;
            background-color: #662D91;
        }}
        </style>
        <div class="progress-bar"><div class="progress-bar-fill"></div></div>
    """, unsafe_allow_html=True)

    st.markdown(f"#### ❓ Question {current_index + 1} of {total_questions}")
    st.markdown(f"<div class='question-card'><h3>{question['question']}</h3>", unsafe_allow_html=True)

    correct = question["correct"]
    options = question["options"]

    col1, col2 = st.columns(2)
    columns = [col1, col2]

    for idx, option in enumerate(options):
        with columns[idx % 2]:
            with st.form(key=f"form_{current_index}_{idx}"):
                submitted = st.form_submit_button(
                    label=f"**{option}**",
                    use_container_width=True
                )
                if submitted:
                    is_correct = option in correct if isinstance(correct, list) else option == correct

                    # Record
                    answers = st.session_state.get("answers", {})
                    if game_id not in answers:
                        answers[game_id] = {}
                    if player not in answers[game_id]:
                        answers[game_id][player] = {}

                    answers[game_id][player][f"Q{current_index + 1}"] = {
                        "selected_answer": option,
                        "correct_answer": correct,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "is_correct": is_correct
                    }

                    st.session_state.answers = answers
                    save_answers(answers)

                    scores = load_scores()
                    if game_id not in scores:
                        scores[game_id] = {}
                    if player not in scores[game_id]:
                        scores[game_id][player] = 0
                    if is_correct:
                        scores[game_id][player] += 1
                    save_scores(scores)

                    st.session_state.current_question_index += 1
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def logged_in_page():
    
    # Initialize toggle states
    if "new_game_active" not in st.session_state:
        st.session_state.new_game_active = False
    if "game_link_active" not in st.session_state:
        st.session_state.game_link_active = False
    if "dashboard_active" not in st.session_state:
        st.session_state.dashboard_active = False
    if "manage_sets_games_active" not in st.session_state:
        st.session_state.manage_sets_games_active = False
    if "about" not in st.session_state:
        st.session_state.about = False
        
    def clear_all_views():
        st.session_state.new_game_active = False
        st.session_state.game_link_active = False
        st.session_state.dashboard_active = False
        st.session_state.manage_sets_games_active = False
        st.session_state.about = False
    
    home, _ ,logout = st.columns([1,4,1])
    with home:
        if st.button("About"):
            clear_all_views()
            st.session_state.about = True
            
    with logout:
        if st.button("🔒 Log out"):
            st.session_state.logged_in = False
            st.session_state.game = False
            for key in list(st.session_state.keys()):
                if key not in ["logged_in"]:  # Keep "logged_in" to allow redirect to login page
                    del st.session_state[key]
            st.rerun()
            
    st.markdown("## 👋 Welcome to the Quiz Game Manager!")
    
    def reorder_questions():
        move_plan = []

        for i in range(len(st.session_state.questions)):
            raw = st.session_state.get(f"order_{i}", "")
            if raw.startswith("Position"):
                target = int(raw.replace("Position ", "")) - 1
                move_plan.append((target, i))

        questions_copy = st.session_state.questions.copy()
        final_order = questions_copy.copy()

        for insert_pos, original_index in sorted(move_plan):
            q = questions_copy[original_index]
            if q in final_order:
                final_order.remove(q)
            final_order.insert(insert_pos, q)

        st.session_state.questions = final_order
        save_questions(st.session_state.questions)

        for i in range(len(st.session_state.questions)):
            st.session_state.pop(f"order_{i}", None)

        st.success("✅ Question order updated successfully!")
        st.rerun()

    # Display the logo
    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    st.sidebar.image(TELADOC_LOGO, width=300)


    with st.container(border=True):
        menu1, menu2, menu3, menu4 = st.columns([1.5,1.5,1.5,1.5])
        # Sidebar toggle buttons (no highlight)
        
        with menu1:
            if st.button("**🧠 Create Quiz**"):
                clear_all_views()
                st.session_state.new_game_active = True
                
        with menu2:
            if st.button("**🚀 Launch Game**"):
                clear_all_views()
                st.session_state.game_link_active = True
                
        with menu3:
            if st.button("**📊 Game Stats**"):
                clear_all_views()
                st.session_state.dashboard_active = True
                
        with menu4:
            if st.button("**🛠 Manage Games**"):
                clear_all_views()
                st.session_state.manage_sets_games_active = True
                
      
   
    # --- Show game presentation ---
    if st.session_state.get("about", False):

        st.markdown("""
        ### 🎮 What is this?
        This is an internal Teladoc game-based quiz platform to engage your team using questions and multiple-choice answers.

        ---
        ### 🧭 Admin Workflow Overview

        #### 1️⃣ **Create Game**
        - Add custom quiz questions manually or load an existing set from file.
        - Each question has four answer options, and one must be marked as correct.
        - **Validation checks** ensure no empty or duplicate options.
        - After adding, preview questions with:
            - Question number
            - Correct answer indication (✅)
            - Options to **edit**, **delete**, or **reorder** questions.

        #### 2️⃣ **Preview & Reorder Questions**
        - Questions appear in two-column layout.
        - Use dropdowns to select a new position for each question.
        - Click "🔄 Reorder Questions" to save the new order.

        #### 3️⃣ **Start Game**
        - Select a question set and click "Generate & Save Game".
        - A unique **Game ID** is created.
        - Share the Game ID with players — they’ll use it to log in.

        #### 4️⃣ **Dashboard**
        - View detailed stats and question-level responses.
        - See who answered what, which options were chosen, and how many players completed the game.

        #### 5️⃣ **Manage Sets & Games**
        - Delete unused question sets and game IDs.
        - Confirm deletions with a checkbox to avoid mistakes.

        ---
        ### 🏆 How Does a Player Win?

        - Each correct answer gives **1 point**.
        - At the end of the game, players are **ranked** based on:
            1. **Total score** (most correct answers)
            2. **Speed** (tie-breaker: earliest answer timestamp)

        - The **Top 3 players** appear on a podium:
            - 🥇 First Place
            - 🥈 Second Place
            - 🥉 Third Place

        ---
        ### 🧑‍💼 Admin vs Player View
        - **Admin:** Manages questions, games, dashboard, and data.
        - **Player:** Sees only the game login screen and question flow.

        ---
        👉 Use the buttons above to get started.
        """)

    # --- CREATE GAME SECTION ---
    if st.session_state.new_game_active:
        with st.sidebar.container():
            st.subheader("Load a Saved Question Package")
            saved_filenames = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]
            selected_file = st.selectbox("Select a question set to manage:", saved_filenames)

            if st.button("📥 Load Question Set"):
                st.session_state.questions = load_question_set(selected_file)
                save_questions(st.session_state.questions)
                st.success(f"Question set '{selected_file}' loaded successfully!")
                time.sleep(1)
                st.rerun()

            st.title("🧠 Create & Edit Questions")
            st.write("Add questions, choose number of options, and set the correct one(s).")

            # Initialize session state for questions
            if "questions" not in st.session_state:
                st.session_state.questions = []

            # Unique session state key counter for input fields
            if "input_key_counter" not in st.session_state:
                st.session_state.input_key_counter = 0

            # 🔢 Select number of options
            num_options = st.number_input(
                "How many answer options?", min_value=2, max_value=6, value=4, step=1, key="num_options_selector"
            )

            # Generate input keys
            question_key = f"question_{st.session_state.input_key_counter}"
            option_keys = [f"option_{st.session_state.input_key_counter}_{i}" for i in range(num_options)]
            correct_answer_key = f"correct_{st.session_state.input_key_counter}"

            # Question input
            question = st.text_input("Enter the question:", key=question_key, max_chars=500)

            # Option inputs
            options = [st.text_input(f"Option {i+1}", key=option_keys[i]) for i in range(num_options)]

            # Correct answer selection
            non_empty_options = [opt for opt in options if opt.strip()]
            correct_answer = st.selectbox("Select the correct answer:", non_empty_options, key=correct_answer_key)

            # ➕ Add Question
            if st.button("➕ Add Question"):
                if not question.strip():
                    st.error("The question cannot be empty.")
                elif any(opt.strip() == "" for opt in options):
                    st.error("All options must be filled in and not empty.")
                elif len(set(opt.strip() for opt in options)) < len(options):
                    st.error("Options must be unique — duplicates are not allowed.")
                else:
                    new_question = {
                        "question": question.strip(),
                        "options": [opt.strip() for opt in options],
                        "correct": correct_answer.strip()
                    }
                    st.session_state.questions.append(new_question)
                    save_questions(st.session_state.questions)
                    st.success("✅ Question added!")
                    st.session_state.input_key_counter += 1
                    time.sleep(0.5)
                    st.rerun()


            
        with st.container():
            st.subheader("🧩 Preview & Manage Questions")

            if "questions" not in st.session_state:
                st.session_state.questions = load_questions()

            if not st.session_state.questions:
                st.warning("No questions found. Please create questions first.")
                st.stop()

            col1, col2 = st.columns(2)
            selected_positions = set()

            for i, question in enumerate(st.session_state.questions):
                col = col1 if i % 2 == 0 else col2
                with col:
                    with st.container(border=True):
                        action_col, _ ,delete_col = st.columns([1, 4 ,1])

                        # ✏️ Edit Button
                        with action_col:
                            if st.button("✏️", key=f"edit_{i}"):
                                st.session_state.editing_index = i

                        # 🗑 Delete Button
                        with delete_col:
                            if st.button("**🗑**", key=f"delete_{i}"):
                                st.session_state.questions.remove(question)
                                save_questions(st.session_state.questions)
                                st.success("Question deleted!")
                                st.rerun()
                                
                        # Show editable fields if this question is selected for editing
                        if st.session_state.get("editing_index") == i:
                            st.markdown("**✏️ Edit Mode**")
                            
                            # Edit question text
                            new_question = st.text_input("Edit question text", value=question["question"], key=f"edit_q_{i}")

                            # Editable number of options (default to current)
                            current_option_count = len(question["options"])
                            num_edit_options = st.number_input(
                                "Number of options", min_value=2, max_value=6, value=current_option_count, step=1, key=f"edit_q_{i}_option_count"
                            )

                            # Option fields
                            new_options = []
                            for opt_idx in range(num_edit_options):
                                default_val = question["options"][opt_idx] if opt_idx < len(question["options"]) else ""
                                new_opt = st.text_input(f"Option {opt_idx+1}", value=default_val, key=f"edit_q_{i}_opt_{opt_idx}")
                                new_options.append(new_opt)

                            # Filter non-empty to prevent dropdown errors
                            valid_for_dropdown = [opt for opt in new_options if opt.strip()]
                            try:
                                index_of_correct = valid_for_dropdown.index(question["correct"]) if question["correct"] in valid_for_dropdown else 0
                            except ValueError:
                                index_of_correct = 0

                            new_correct = st.selectbox(
                                "Select correct answer",
                                valid_for_dropdown,
                                index=index_of_correct,
                                key=f"edit_q_{i}_correct"
                            )

                            if st.button("💾 Save Changes", key=f"save_edit_{i}"):
                                if not new_question.strip():
                                    st.error("The question cannot be empty.")
                                elif any(opt.strip() == "" for opt in new_options):
                                    st.error("All options must be filled in and not empty.")
                                elif len(set(opt.strip() for opt in new_options)) < len(new_options):
                                    st.error("Options must be unique — duplicates are not allowed.")
                                else:
                                    st.session_state.questions[i] = {
                                        "question": new_question.strip(),
                                        "options": [opt.strip() for opt in new_options],
                                        "correct": new_correct.strip()
                                    }
                                    save_questions(st.session_state.questions)
                                    st.success("✅ Question updated successfully.")
                                    st.session_state.editing_index = None
                                    st.rerun()


                        st.markdown(f"<h3 style='color:#662D91;'>Q{i+1}</h3>", unsafe_allow_html=True)
                        st.markdown(f"**{question['question']}**")

                        for opt in question["options"]:
                            if opt == question["correct"]:
                                st.markdown(f"✅ **{opt}**")
                            else:
                                st.markdown(f"🔹 {opt}")

                        total_qs = len(st.session_state.questions)
                        current_pos = i + 1

                        available_positions = [
                            pos for pos in range(1, total_qs + 1)
                            if pos != current_pos and pos not in selected_positions
                        ]

                        display_options = ["— Select new position —"] + [f"Position {p}" for p in available_positions]

                        previous_value = st.session_state.get(f"order_{i}", "— Select new position —")

                        selected = st.selectbox(
                            f"Move Q{i+1} to:",
                            display_options,
                            index=display_options.index(previous_value) if previous_value in display_options else 0,
                            key=f"order_{i}",
                            help="Choose a unique new position for this question", label_visibility="collapsed"
                        )

                        if selected.startswith("Position"):
                            selected_pos_number = int(selected.replace("Position ", ""))
                            selected_positions.add(selected_pos_number)

            if st.button("🔄 Reorder Questions"):
                reorder_questions()

            # Save question set with a custom name
            st.subheader("Save Question Set")
            st.markdown("Save the current set of questions to a custom file for later use.")
            filename = st.text_input("Enter a filename to save this question set (without extension)")
            # if filename exists, warn the user
            if os.path.exists(os.path.join(QUESTION_SETS_DIR, filename + ".json")):
                st.warning("A file with this name already exists. Saving will overwrite the existing file.")
            # Save
            if st.button("💾 Save Set"):
                if filename:
                    save_question_set(filename)
                else:
                    st.error("Please enter a valid filename.")
        
            # Button to reset only the question preview/management
            confirm_clear = st.checkbox("⚠️ I’m sure I want to clear all questions", key="confirm_clear")

            if st.button("🧹 Clear All Questions"):
                if confirm_clear:
                    reset_questions_only()
                else:
                    st.warning("Please confirm clearing by checking the box.")
            
            if not st.session_state.questions:
                st.warning("No questions found. Please create questions first.")

    # --- START GAME SECTION ---
    if st.session_state.game_link_active:
        st.title("🚀 Generate Game Link")
        question_files = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]

        if not question_files:
            st.warning("No question sets found. Please create and save a question set first.")
        else:
            selected_file = st.selectbox("Select a question set:", question_files, label_visibility="collapsed")

            if st.button("Generate & Save Game"):
                selected_questions = load_question_set(selected_file)
                game_id = generate_game_id()
                st.session_state.game_id = game_id

                games_data = {}
                if os.path.exists(GAMES_FILE):
                    with open(GAMES_FILE, "r") as f:
                        try:
                            games_data = json.load(f)
                        except json.JSONDecodeError:
                            games_data = {}

                games_data[game_id] = {
                    "question_file": selected_file,
                    "questions": selected_questions
                }

                with open(GAMES_FILE, "w") as f:
                    json.dump(games_data, f, indent=4)

                st.success(f"Game ID {game_id} created and saved!")
                st.markdown(f"Send this Game ID to players to join: {game_id}")

    # --- DASHBOARD SECTION ---
    if st.session_state.dashboard_active:
        page = st.sidebar.radio('', ["**📊 Results**","**🏆 Winners**"], label_visibility="collapsed")

        if page == "**📊 Results**":
            st.title("📊 Quiz Results")

            if "completed_players" not in st.session_state:
                st.session_state.completed_players = set()

            # Always use history
            history = load_game_history()
            available_game_ids = list(history.keys())

            if not available_game_ids:
                st.warning("No game sessions found yet.")
                return

            selected_game_id = st.selectbox("Select Game ID to View Results", available_game_ids, key="selectbox_results")
            game_id = selected_game_id
            st.session_state.game_id = game_id

            selected_data = history.get(game_id, {})
            game_answers = selected_data.get("answers", {})
            questions = selected_data.get("questions", [])

            st.write("Total Players:", len(game_answers))
            st.write("Total Questions:", len(questions))

            st.write("Players who completed all questions:")
            for player, response in game_answers.items():
                if len(response) == len(questions):
                    st.write(f"✅ {player}")
                    st.session_state.completed_players.add(player)

            st.subheader("📋 Questions & Answers")

            for i, question in enumerate(questions):
                with st.expander(f"Question {i+1}: {question['question']}"):
                    response_counts = {opt: 0 for opt in question["options"]}
                    total_responses = 0

                    for player, responses in game_answers.items():
                        q_key = f"Q{i+1}"
                        if q_key in responses:
                            selected_answer = responses[q_key]["selected_answer"]
                            if selected_answer in response_counts:
                                response_counts[selected_answer] += 1
                            total_responses += 1

                    for opt in question["options"]:
                        count = response_counts[opt]
                        percentage = (count / total_responses * 100) if total_responses > 0 else 0
                        if opt == question["correct"]:
                            st.markdown(f"✅ **{opt}** — {count} responses ({percentage:.1f}%)")
                        else:
                            st.markdown(f"🔹 {opt} — {count} responses ({percentage:.1f}%)")

                    st.markdown(f"**Total Responses:** {total_responses}")


        elif page == "**🏆 Winners**":
            st.title("🏆 Winners")

            # Always use game history
            history = load_game_history()
            available_game_ids = list(history.keys())

            if not available_game_ids:
                st.warning("No game sessions found yet.")
            else:
                selected_game_id = st.selectbox("Select Game ID", available_game_ids, key="selectbox_winners")
                game_id = selected_game_id
                st.session_state.game_id = game_id

                selected_data = history.get(game_id, {})
                game_answers = selected_data.get("answers", {})
                game_scores = selected_data.get("scores", {})

                data = []
                for player, response in game_answers.items():
                    if response:
                        last_q = list(response.keys())[-1]
                        timestamp_str = response[last_q].get("timestamp", "9999-12-31T23:59:59")
                        try:
                            timestamp = datetime.datetime.fromisoformat(timestamp_str)
                        except:
                            timestamp = datetime.datetime.max
                        score = game_scores.get(player, 0)
                        data.append((player, score, timestamp))

                if not data:
                    st.warning("No valid answer data found.")
                else:
                    sorted_data = sorted(data, key=lambda x: (-x[1], x[2]))

                    if st.button("📢 Show Winners"):
                        st.balloons()
                        st.markdown("<h2 style='color: #FFD700;'>Podium Winners</h2>", unsafe_allow_html=True)

                        col_podium = st.columns(3)
                        if len(sorted_data) > 0:
                            with col_podium[1].container(border=True):
                                st.markdown(f"<h4>🥇 {sorted_data[0][0]} - {sorted_data[0][1]} pts</h4>", unsafe_allow_html=True)
                        if len(sorted_data) > 1:
                            with col_podium[0].container(border=True):
                                st.markdown(f"<h4>🥈 {sorted_data[1][0]} - {sorted_data[1][1]} pts</h4>", unsafe_allow_html=True)
                        if len(sorted_data) > 2:
                            with col_podium[2].container(border=True):
                                st.markdown(f"<h4>🥉 {sorted_data[2][0]} - {sorted_data[2][1]} pts</h4>", unsafe_allow_html=True)

                        with st.sidebar.container():
                            st.markdown("## 🏅 All Players Ranking:")
                            for i, (player, score, timestamp) in enumerate(sorted_data):
                                st.markdown(f"<p style='font-size:18px;'>{i+1}. <strong>{player}</strong> — {score} pts</p>", unsafe_allow_html=True)


    # --- MANAGE SETS & GAMES SECTION ---
    if st.session_state.get("manage_sets_games_active", False):
        st.header("🧰 Manage Question Sets & Games")

        # --- Manage Question Sets ---
        st.subheader("🗃 Question Sets")
        sets = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]
        if not sets:
            st.info("No question sets found.")
        else:
            for qfile in sets:
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(qfile)
                with col3:
                    confirm_key = f"confirm_qset_{qfile}"
                    st.checkbox("⚠️ Confirm deletion", key=confirm_key)
                with col2:
                    if st.button("**🗑**", key=f"delete_qset_{qfile}"):
                        if st.session_state.get(confirm_key, False):
                            delete_question_set(qfile)
                        else:
                            st.warning("Please confirm deletion first.")

        # --- Manage Active Games ---
        st.subheader("🎮 Active Games")
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE, "r") as f:
                try:
                    games = json.load(f)
                except json.JSONDecodeError:
                    games = {}
        else:
            games = {}

        if not games:
            st.info("No active games found.")
        else:
            for game_id in list(games.keys()):
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(f"Game ID: {game_id} — Set: {games[game_id]['question_file']}")
                with col3:
                    confirm_key = f"confirm_game_{game_id}"
                    st.checkbox("⚠️ Confirm deletion", key=confirm_key)
                with col2:
                    if st.button("**🗑**", key=f"delete_game_{game_id}"):
                        if st.session_state.get(confirm_key, False):
                            del games[game_id]
                            with open(GAMES_FILE, "w") as f:
                                json.dump(games, f, indent=4)
                            st.success(f"Game {game_id} deleted.")
                            st.rerun()
                        else:
                            st.warning("Please confirm deletion first.")


           
def main():
    if st.session_state.logged_in == 'admin':
        logged_in_page()
    elif st.session_state.logged_in == 'player' and st.session_state.game != 'start_game':
        player_page()
    elif st.session_state.game == 'start_game':
        start_game()
    else:
        login_page()

if __name__ == '__main__':
    main()