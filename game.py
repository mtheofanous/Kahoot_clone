import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
import time
import datetime
import random
import string


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
    st.title("Delete Player")
    player = st.selectbox("Select a player to delete", st.session_state.players)
    if st.button("Delete Player"):
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
    st.title("Login")

    col1, col2 = st.columns(2)

    with col1:
        password = st.text_input("Enter the password", type="password", max_chars=20)

    with col2:
        game_id_input = st.text_input("Enter Game ID", max_chars=10).upper()

    if st.button("Log in"):
        if password == 'Teladoc':
            st.session_state.logged_in = 'admin'
            st.rerun()

        elif password == '111':  # player password
            if not game_id_input:
                st.error("Please enter a valid Game ID to proceed.")
            else:
                st.session_state.logged_in = 'player'
                st.session_state.game_id = game_id_input  # Track the game session
                st.session_state.current_question_index = 0
                st.rerun()

        else:
            st.error("Incorrect password. Try again.")
            
def player_page():
    st.title("Welcome to Teladoc Game")

    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    col1, col2 = st.columns([4, 3])
    with col2:
        st.image(TELADOC_LOGO, width=300)

    player = st.text_input("Enter your name: ", max_chars=40)
    
    if st.button("Start"):

        if player:
            st.session_state.current_player = player

            # Load existing players
            existing_players = {}
            if os.path.exists(PLAYERS_FILE):
                with open(PLAYERS_FILE, "r") as f:
                    existing_players = json.load(f)

            existing_players[player] = {}

            with open(PLAYERS_FILE, "w") as f:
                json.dump(existing_players, f, indent=4)
                
                    # Switch to countdown + game start
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
    
    # Load scores
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            all_scores = json.load(f)
    else:
        all_scores = {}

    if game_id not in all_scores:
        all_scores[game_id] = {}
    if player not in all_scores[game_id]:
        all_scores[game_id][player] = 0

    # Load answers
    all_answers = load_answers()
    if game_id not in all_answers:
        all_answers[game_id] = {}
    if player not in all_answers[game_id]:
        all_answers[game_id][player] = {}


    # Load questions
    questions = load_questions()
    total_questions = len(questions)
    current_index = st.session_state.get("current_question_index", 0)

    if current_index < total_questions:
        question = questions[current_index]

        st.markdown(f"##### Question {current_index + 1} of {total_questions}")
        st.markdown(f"#### {question['question']}")

        # Build a 2-column layout
        col1, col2 = st.columns(2)
        columns = [col1, col2]

        # CSS button style
        button_css = """
        <style>
        .big-button {
            display: block;
            width: 100%;
            padding: 20px;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            background-color: #f5f5f5;
            border: 2px solid #ccc;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
        }
        .big-button:hover {
            background-color: #e0e0e0;
        }
        </style>
        """

        st.markdown(button_css, unsafe_allow_html=True)

        # Use form so only one button triggers a response
        for idx, option in enumerate(question["options"]):
            with columns[idx % 2]:
                # Unique form per button
                with st.form(key=f"form_{current_index}_{idx}"):
                    submitted = st.form_submit_button(
                        label=f"**{option}**", 
                        help=option
                    )

                    if submitted:
                        selected = option
                        correct = question["correct"]
                        timestamp = datetime.datetime.now().isoformat()

                        all_answers[game_id][player][f"Q{current_index + 1}"] = {
                            "selected_answer": selected,
                            "correct_answer": correct,
                            "timestamp": timestamp,
                            "is_correct": selected == correct
                        }

                        if selected == correct:
                            all_scores[game_id][player] += 1

                        with open(ANSWERS_FILE, "w") as f:
                            json.dump(all_answers, f, indent=4)
                        with open(DATA_FILE, "w") as f:
                            json.dump(all_scores, f, indent=4)

                        st.session_state.current_question_index = current_index + 1
                        st.rerun()

    else:
        final_score = all_scores[game_id][player]

        save_game_history(
            game_id=game_id,
            questions=questions,
            answers=all_answers,
            scores=all_scores
        )

        st.success("🎉 Quiz completed!")
        st.markdown(f"Your final score: **{final_score}**")





def logged_in_page():
    st.title("Welcome to Teladoc Game Manager")

    # Display the logo
    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    col1, col2 = st.columns([4, 3])
    with col2:
        st.image(TELADOC_LOGO, width=300)

    menu = st.sidebar.selectbox("***GAME***", ["New Game", "My Games"])
    
    if menu == "New Game":
        page = st.sidebar.radio('', ["📝 Create New Questions", "⚙️ Preview and Manage Questions", "🔗 Game Link"])
        
        if page == "📝 Create New Questions":
            st.title("Create Questions")
            st.write("Add questions, answer options, and select the correct answer.")

            # Initialize session state for questions
            if "questions" not in st.session_state:
                st.session_state.questions = []

            # Unique session state key counter for input fields
            if "input_key_counter" not in st.session_state:
                st.session_state.input_key_counter = 0

            # Generate unique keys to force input refresh
            question_key = f"question_{st.session_state.input_key_counter}"
            option_keys = [f"option_{st.session_state.input_key_counter}_{i}" for i in range(4)]
            correct_answer_key = f"correct_{st.session_state.input_key_counter}"

            # Input fields
            question = st.text_input("Enter the question:", key=question_key, max_chars=500)

            options = [
                st.text_input(f"Option {i+1}", key=option_keys[i]) for i in range(4)
            ]

            correct_answer = st.selectbox("Select the correct answer:", options, key=correct_answer_key)

            # Add Question Button
            if st.button("Add Question"):
                if not question.strip() or any(opt.strip() == "" for opt in options):
                    st.error("Please fill in all fields before adding the question.")
                else:
                    new_question = {
                        "question": question,
                        "options": options,
                        "correct": correct_answer
                    }
                    st.session_state.questions.append(new_question)
                    save_questions(st.session_state.questions)  # Save questions to file
                    st.success("Question added!")

                    # Increase key counter to reset input fields
                    st.session_state.input_key_counter += 1

                    # Wait for UI feedback
                    time.sleep(1.5)

                    # Force UI refresh
                    st.rerun()
                    
            st.write("Preview and manage questions in the 'Preview Questions' section.")
            st.write("You can also save the question set for later use.")
        
        if page == "⚙️ Preview and Manage Questions":
            st.subheader("Preview & Reorder Questions")

            # Load questions from JSON
            questions = load_questions()
            if "questions" not in st.session_state:
                st.session_state.questions = questions.copy() # Prevent modifying original data accidentally
            
            if not questions:
                st.warning("No questions found. Please create questions first.")

            with st.expander("Click to preview and reorder questions"):
                # Splitting questions into two columns
                col1, col2 = st.columns(2)

                new_order = []  # Store the new order

                for i, question in enumerate(st.session_state.questions):
                    # Alternate placement of questions in columns
                    col = col1 if i % 2 == 0 else col2
                    with col:
                        with st.container(border=True):
                                                        # 🗑 Delete button (placed at top with unique key)
                            _ , delete_col = st.columns([5, 1])
                            with delete_col:
                                if st.button("**🗑**", key=f"delete_{i}"):
                                    try:
                                        st.session_state.questions.remove(question)
                                        save_questions(st.session_state.questions)
                                        st.success("Question deleted!")
                                        st.rerun()
                                    except ValueError:
                                        st.error("Question not found.")
                                        
                            # Dropdown for reordering questions
                            new_index = st.selectbox(
                                f"Move Q{i+1} to:",
                                list(range(1, len(st.session_state.questions) + 1)),
                                index=i,
                                key=f"order_{i}"
                            )

                            # Store new positions for sorting and don't let questions have the same order
                            if new_index in [pos for pos, _ in new_order]:
                                st.error("Each question must have a unique position. Please adjust the order.")
                                st.stop()
                            
                                
                            new_order.append((new_index, question))

                            # Display question
                            st.markdown(f"<h3 style='color:#662D91;'>Question {i+1}</h3>", unsafe_allow_html=True)
                            st.markdown(f"**{question['question']}**")

                            # Show options
                            for opt in question["options"]:
                                if opt == question["correct"]:
                                    st.markdown(f"✅ **{opt}**")
                                else:
                                    st.markdown(f"🔹 {opt}")

                # Sort questions based on new order
                new_order.sort(key=lambda x: x[0])
                st.session_state.questions = [q for _, q in new_order]

                # Save reordered questions to JSON
                if st.button("Save Order"):
                    with open("questions.json", "w") as f:
                        json.dump(st.session_state.questions, f, indent=4)
                    st.success("Question order saved successfully!")
                    st.rerun()
                    
            # Save question set with a custom name
            st.subheader("Save Questions Package")
            st.markdown("Save the current set of questions to a custom file for later use.")
            filename = st.text_input("Enter a filename to save this question set (without extension)")
            # if filename exists, warn the user
            if os.path.exists(os.path.join(QUESTION_SETS_DIR, filename + ".json")):
                st.warning("A file with this name already exists. Saving will overwrite the existing file.")
            # Save
            if st.button("Save Question Set"):
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
        elif page == "🔗 Game Link":
            st.title("🔗 Game Link Generator")

            if st.button("🎲 Click to Generate Game ID"):
                st.session_state.game_id = generate_game_id()

                # Save it to a file
                with open(GAMES_FILE, "w") as f:
                    json.dump({"game_id": st.session_state.game_id}, f, indent=4)

                st.success(f"Game ID generated: **{st.session_state.game_id}**")
            # Show the link only if the Game ID has been generated
            # if "game_id" in st.session_state:
            #     base_url = "http://localhost:8501/"  # # Change to your deployment URL "https://kahootclone.streamlit.app/" or "http://localhost:8501/"
            #     st.markdown(f"🔗 Share this link with players: [Copy Link]({st.session_state.game_id})")
        
    
    if menu == "My Games":
    # Add any additional features here for the logged-in user
        page = st.sidebar.radio("***GAME***", ["📂 Load Previous Questions", "📝 Create New Questions", "⚙️ Preview and Manage Questions", "🔗 Game Link", "📊 Results", "🏆 Winners"])
        
        if page == "📝 Create New Questions":
            st.title("Create Questions")
            st.write("Add questions, answer options, and select the correct answer.")

            # Initialize session state for questions
            if "questions" not in st.session_state:
                st.session_state.questions = []

            # Unique session state key counter for input fields
            if "input_key_counter" not in st.session_state:
                st.session_state.input_key_counter = 0

            # Generate unique keys to force input refresh
            question_key = f"question_{st.session_state.input_key_counter}"
            option_keys = [f"option_{st.session_state.input_key_counter}_{i}" for i in range(4)]
            correct_answer_key = f"correct_{st.session_state.input_key_counter}"

            # Input fields
            question = st.text_input("Enter the question:", key=question_key, max_chars=500)

            options = [
                st.text_input(f"Option {i+1}", key=option_keys[i]) for i in range(4)
            ]

            correct_answer = st.selectbox("Select the correct answer:", options, key=correct_answer_key)

            # Add Question Button
            if st.button("Add Question"):
                if not question.strip() or any(opt.strip() == "" for opt in options):
                    st.error("Please fill in all fields before adding the question.")
                else:
                    new_question = {
                        "question": question,
                        "options": options,
                        "correct": correct_answer
                    }
                    st.session_state.questions.append(new_question)
                    save_questions(st.session_state.questions)  # Save questions to file
                    st.success("Question added!")

                    # Increase key counter to reset input fields
                    st.session_state.input_key_counter += 1

                    # Wait for UI feedback
                    time.sleep(1.5)

                    # Force UI refresh
                    st.rerun()
                    
            st.write("Preview and manage questions in the 'Preview Questions' section.")
            st.write("You can also save the question set for later use.")
        
        if page == "⚙️ Preview and Manage Questions":
            st.subheader("Preview & Reorder Questions")

            # Load questions from JSON
            questions = load_questions()
            if "questions" not in st.session_state:
                st.session_state.questions = questions.copy() # Prevent modifying original data accidentally
            
            if not questions:
                st.warning("No questions found. Please create questions first.")

            with st.expander("Click to preview and reorder questions"):
                # Splitting questions into two columns
                col1, col2 = st.columns(2)

                new_order = []  # Store the new order

                for i, question in enumerate(st.session_state.questions):
                    # Alternate placement of questions in columns
                    col = col1 if i % 2 == 0 else col2
                    with col:
                        with st.container(border=True):
                            
                            # 🗑 Delete button (placed at top with unique key)
                            delete_col, _ = st.columns([1, 5])
                            with delete_col:
                                if st.button("🗑", key=f"delete_{i}"):
                                    try:
                                        st.session_state.questions.remove(question)
                                        save_questions(st.session_state.questions)
                                        st.success("Question deleted!")
                                        st.rerun()
                                    except ValueError:
                                        st.error("Question not found.")
                            
                            # Dropdown for reordering questions
                            new_index = st.selectbox(
                                f"Move Q{i+1} to:",
                                list(range(1, len(st.session_state.questions) + 1)),
                                index=i,
                                key=f"order_{i}"
                            )

                            # Store new positions for sorting and don't let questions have the same order
                            if new_index in [pos for pos, _ in new_order]:
                                st.error("Each question must have a unique position. Please adjust the order.")
                                st.stop()
                            
                                
                            new_order.append((new_index, question))

                            # Display question
                            st.markdown(f"<h3 style='color:#662D91;'>Question {i+1}</h3>", unsafe_allow_html=True)
                            st.markdown(f"**{question['question']}**")

                            # Show options
                            for opt in question["options"]:
                                if opt == question["correct"]:
                                    st.markdown(f"✅ **{opt}**")
                                else:
                                    st.markdown(f"🔹 {opt}")

                # Sort questions based on new order
                new_order.sort(key=lambda x: x[0])
                st.session_state.questions = [q for _, q in new_order]

                # Save reordered questions to JSON
                if st.button("Save Order"):
                    with open("questions.json", "w") as f:
                        json.dump(st.session_state.questions, f, indent=4)
                    st.success("Question order saved successfully!")
                    st.rerun()
                    
            # Save question set with a custom name
            st.subheader("Save Questions Package")
            st.markdown("Save the current set of questions to a custom file for later use.")
            filename = st.text_input("Enter a filename to save this question set (without extension)")
            # if filename exists, warn the user
            if os.path.exists(os.path.join(QUESTION_SETS_DIR, filename + ".json")):
                st.warning("A file with this name already exists. Saving will overwrite the existing file.")
            # Save
            if st.button("Save Question Set"):
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

            
        elif page == '📂 Load Previous Questions':
            st.subheader("Load a Saved Question Package")
            saved_filenames = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]

            selected_file = st.selectbox("Select a question set to manage:", saved_filenames)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Load Question Set"):
                    st.session_state.questions = load_question_set(selected_file)
                    save_questions(st.session_state.questions)
                    st.success(f"Question set '{selected_file}' loaded successfully!")
                    time.sleep(1)
                    st.rerun()

            with col2:
                confirm_delete = st.checkbox("⚠️ I’m sure I want to delete this set", key="confirm_delete")

                if st.button("🗑️ Delete Question Set"):
                    if confirm_delete:
                        delete_question_set(selected_file)
                    else:
                        st.warning("Please confirm deletion by checking the box.")

                    
        elif page == "🔗 Game Link":
            st.title("🔗 Game Link Generator")

            if st.button("🎲 Click to Generate Game ID"):
                st.session_state.game_id = generate_game_id()

                # Save it to a file
                with open(GAMES_FILE, "w") as f:
                    json.dump({"game_id": st.session_state.game_id}, f, indent=4)

                st.success(f"Game ID generated: **{st.session_state.game_id}**")
            # Show the link only if the Game ID has been generated
            # if "game_id" in st.session_state:
            #     base_url = "http://localhost:8501/"  # # Change to your deployment URL "https://kahootclone.streamlit.app/" or "http://localhost:8501/"
            #     st.markdown(f"🔗 Share this link with players: [Copy Link]({st.session_state.game_id})")
        
            
        elif page == "📊 Results":
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




        elif page == "🏆 Winners":
            st.title("🏆 Winners")
            
            use_history = st.checkbox("📁 Use archived game history")
            if use_history:
                history = load_game_history()
                available_game_ids = list(history.keys())
            else:
                all_answers = load_answers()
                def load_all_scores():
                    if os.path.exists(DATA_FILE):
                        with open(DATA_FILE, "r") as f:
                            return json.load(f)
                    return {}

                all_scores = load_all_scores()  # Load all game scores, not just the current one

                # Get all available game IDs
                available_game_ids = list(all_answers.keys())

            if not available_game_ids:
                st.warning("No game sessions found yet.")
            else:
                selected_game_id = st.selectbox("Select Game ID", available_game_ids, key="selectbox_winners")
                game_id = selected_game_id
                st.session_state.game_id = game_id  # ensure consistency for loading

                if use_history:
                    selected_data = history.get(game_id, {})
                    game_answers = selected_data.get("answers", {})
                    game_scores = selected_data.get("scores", {})
                else:
                    if game_id not in all_answers or not all_answers[game_id]:
                        st.warning("No answers submitted for this game.")
                        return
                    game_answers = all_answers[game_id]
                    game_scores = all_scores.get(game_id, {})

                data = []
                for player, response in game_answers.items():
                    if response:
                        last_q = list(response.keys())[-1]
                        timestamp_str = response[last_q].get("timestamp", "9999-12-31T23:59:59")
                        try:
                            timestamp = datetime.datetime.fromisoformat(timestamp_str)
                        except:
                            timestamp = datetime.datetime.max
                        score = game_scores.get(player, 0)  # ✅ get score for player in this game
                        data.append((player, score, timestamp))

                if not data:
                    st.warning("No valid answer data found.")
                else:
                    # Sort: score DESC, then timestamp ASC
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

                        st.subheader("🏅 All Players Ranking:")
                        for i, (player, score, timestamp) in enumerate(sorted_data):
                            st.markdown(f"<p style='font-size:20px;'>{i+1}. <strong>{player}</strong> — {score} pts</p>", unsafe_allow_html=True)

                        st.markdown("<p style='font-size:24px; font-weight:bold;'>🎉 Thank you for playing! 🎉</p>", unsafe_allow_html=True)


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