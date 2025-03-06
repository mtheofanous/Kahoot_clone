import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
import time
import datetime


st.set_page_config(
    page_title="🎉 Quiz Time!",
    page_icon="❓",
    layout="centered" 
)

# Inject CSS to customize fonts and sizes
st.markdown("""
    <style>
        /* Change the font for the entire app */
        html, body, [class*="st-"] {
            font-family: 'Poppins', sans-serif;
            font-size: 14px !important;
        }

        /* Sidebar customization */
        .sidebar-content {
            font-size: 14px !important;

        }

        /* Style for headings */
        h1 {
            font-size: 30px !important;
            font-weight: bold;
        }
        h2 {
            font-size: 28px !important;
        }
        h3 {
            font-size: 26px !important;
        }
    </style>
""", unsafe_allow_html=True)

# File for storing scores and questions
DATA_FILE = "game_scores.json"
QUESTIONS_FILE = "questions.json"
PLAYERS_FILE = "players.json"
ANSWERS_FILE = "answers.json"
# Directory for saved question sets
QUESTION_SETS_DIR = "question_sets"
if not os.path.exists(QUESTION_SETS_DIR):
    os.makedirs(QUESTION_SETS_DIR)  # Create directory if it doesn't exist

TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
# display in the left corner
col1, col2 = st.columns([4, 3])
with col2:
    st.image(TELADOC_LOGO, width=600)


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

# Function to save the current question set to a custom file
def save_question_set(filename):
    filepath = os.path.join(QUESTION_SETS_DIR, filename + ".json")
    with open(filepath, "w") as f:
        json.dump(st.session_state.questions, f, indent=4)
    st.success(f"Question set saved as '{filename}.json'")

# Function to load a question set from a custom file
# Function to load a question set from a custom file
def load_question_set(filename):
    filepath = os.path.join(QUESTION_SETS_DIR, filename)
    try:
        with open(filepath, "r") as f:
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
        with open(QUESTIONS_FILE, "r") as f:
            return json.load(f)
    return []


def save_questions(questions):

    with open(QUESTIONS_FILE, "w") as f:
        json.dump(questions, f, indent=4)
        
# delete a question
def delete_question():
    st.sidebar.title("Delete Question")
    question = st.sidebar.selectbox("Select a question to delete", st.session_state.questions, format_func=lambda x: x["question"])
    if st.sidebar.button("Delete Question"):
        try:
            st.session_state.questions.remove(question)
            save_questions(st.session_state.questions)
            st.success("Question deleted!")
            st.rerun()
        except ValueError:
            st.error("Question not found.")

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
        try:
            del st.session_state.players[player] 
            save_players(st.session_state.players)
            st.success("Player deleted!")
            st.rerun()
        except KeyError:
            st.error("Player not found.")

# Load scores
def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            scores = json.load(f)
    else:
        scores = {}

    # Ensure all players exist in scores with at least 0 points
    for player in st.session_state.players.keys():
        if player not in scores:
            scores[player] = 0

    return scores


def save_scores(scores):
    # Ensure every player exists in scores, even if they have 0 points
    for player in st.session_state.players.keys():
        if player not in scores:
            scores[player] = 0  # Assign a default score of 0

    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=4)
        
# Function to load answers
def load_answers():
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r") as f:
            return json.load(f)
    return {}

# Function to save answers
def save_answers(answers):
    with open(ANSWERS_FILE, "w") as f:
        json.dump(answers, f, indent=4)
        
answers = load_answers()

# Ensure answers are initialized in session state
if "answers" not in st.session_state:
    st.session_state.answers = answers

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
    st.rerun()

scores = load_scores()

# Detect URL parameters
query_params = st.query_params

player_name = query_params.get("player")

if player_name:
    if isinstance(player_name, list):
        player_name = player_name[0]  # Get the first value if it's a list
    player_name = urllib.parse.unquote(str(player_name))  # Ensure it's a string and decode
else:
    player_name = None

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
    page = st.sidebar.radio("***GAME***", ["📝 Create New Questions", "📂 Load Previous Questions", "⚙️ Preview and Manage Questions", "👥 Setup Players", "🔗 Player Links", "🔄 Reset Game", "📊 Results", "🏆 Winners"])

def player_links():
    st.title("Player Links")
    base_url =  "https://kahootclone.streamlit.app/"  # Change to your deployment URL "https://kahootclone.streamlit.app/" or "http://localhost:8501/"
    for player in st.session_state.players.keys():
        with st.container(border=True):
            player_url = f"{base_url}?page=Player_Quiz&player={urllib.parse.quote(player)}"
            st.write("Open the link below in a new tab to start the quiz:")

            st.write(f"{player}: [Click here]({player_url})")
            st.write(f"Or copy the link below and share it with {player} to start the quiz!")
                
                # Display hidden text input with the link
            link_box = st.text_input(f"Link for {player} (copy):", player_url, key=f"link_{player}", disabled=False)



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


# 
if page == "⚙️ Preview and Manage Questions":
    st.subheader("Preview & Reorder Questions")

    # Load questions from JSON
    questions = load_questions()
    st.session_state.questions = questions.copy()  # Prevent modifying original data accidentally

    with st.expander("Click to preview and reorder questions"):
        # Splitting questions into two columns
        col1, col2 = st.columns(2)

        new_order = []  # Store the new order

        for i, question in enumerate(st.session_state.questions):
            # Alternate placement of questions in columns
            col = col1 if i % 2 == 0 else col2
            with col:
                with st.container(border=True):
                    # Dropdown for reordering questions
                    new_index = st.selectbox(
                        f"Move Q{i+1} to:",
                        list(range(1, len(st.session_state.questions) + 1)),
                        index=i,
                        key=f"order_{i}"
                    )

                    # Store new positions
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
    filename = st.text_input("Enter a filename to save this question set (without extension)")
    if st.button("Save Question Set"):
        if filename:
            save_question_set(filename)
        else:
            st.error("Please enter a valid filename.")

    # delete a question
    delete_question()

elif page == "🔄 Reset Game":
    st.title("Reset Game")
    st.write("This will reset the game and clear all questions, players, and scores.")
    # Reset the game
    if st.button("🔄 Reset Game"):
        reset_game()
    
elif page == '📂 Load Previous Questions':
    st.subheader("Load a Saved Question Package")
    saved_filenames = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]

    selected_file = st.selectbox("Select a question set to load:", saved_filenames)
    if selected_file:
        if st.button("Load Question Set"):
                
            st.session_state.questions = load_question_set(selected_file)
            save_questions(st.session_state.questions)  # Save loaded questions to ensure persistence
            st.success(f"Question set '{selected_file}' loaded successfully!")
            time.sleep(1)
            st.rerun()
                
        

# Page 2: Setup Players
elif page == "👥 Setup Players":
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
elif page == "🔗 Player Links":
    player_links()
    
    
# Page 4: Player Quiz
elif page == "Player Quiz":
    st.title(f"Hello {player_name}! Your Quiz")
    
    questions = st.session_state.questions
    total_questions = len(questions)
    current_question = st.session_state.current_question_index
    if current_question < total_questions:
        question = questions[current_question]
        st.markdown(f"<h3 style='color:#662D91;'>Question {current_question+1}/{total_questions}</h3>", unsafe_allow_html=True)
        st.markdown(f"**{question['question']}**")
        with st.container(border=True):
            st.session_state.responses[player_name] = st.radio("Select your answer:", question["options"], key=f"{player_name}_{current_question}")
        
        if st.button("✅ Submit Answer"):
            if player_name not in scores:
                scores[player_name] = 0  # Ensure the player starts with 0
                
            if player_name not in st.session_state.answers:
                st.session_state.answers[player_name] = {}
                
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            
            time.sleep(0.5)
                
            st.session_state.answers[player_name][f"Q{current_question+1}"] = {
                "question": question["question"],
                "selected_answer": st.session_state.responses[player_name],
                "correct_answer": question["correct"],
                "timestamp": timestamp
            }

            if st.session_state.responses.get(player_name) == question["correct"]:
                scores[player_name] = scores.get(player_name, 0) + 1
            st.session_state.current_question_index += 1
            
            time.sleep(0.5)
            save_scores(scores)
            time.sleep(0.5)
            save_answers(st.session_state.answers)
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


elif page == "📊 Results":
    st.title("Quiz Results")
    
    # Load questions and answers
    questions = load_questions()
    answers = load_answers()
    
    st.write("Total Players:", len(st.session_state.players))
    st.write("Total Questions:", len(questions))
    # show which players finished the all the quiz
    st.write("Players who have completed the quiz:")
    for player, response in answers.items():
        if len(response) == len(questions):
            st.write(player)
            st.session_state.completed_players.add(player)

    st.subheader("Questions & Answers:")

    # Process answer statistics
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1} - {question['question']}"):
            # Count responses for each option
            response_counts = {opt: 0 for opt in question["options"]}
            total_responses = 0

            for player, responses in answers.items():
                if f"Q{i+1}" in responses:
                    selected_answer = responses[f"Q{i+1}"]["selected_answer"]
                    response_counts[selected_answer] += 1
                    total_responses += 1
            
            # Display answer choices with percentages
            for opt in question["options"]:
                count = response_counts[opt]
                percentage = (count / total_responses * 100) if total_responses > 0 else 0
                if opt == question["correct"]:
                    st.markdown(f"✅ **{opt}** - {count} responses ({percentage:.1f}%)")
                else:
                    st.markdown(f"🔹 {opt} - {count} responses ({percentage:.1f}%)")
            
            # Show total responses
            st.markdown(f"**Total Responses:** {total_responses}")

elif page == "🏆 Winners":
    st.title("🏆 Winners")                 
    scores = load_scores()
    answers = load_answers()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    # show me the timestamp of the last answer for each player
    for player, response in answers.items():
        last_answer = list(response.keys())[-1]
        timestamp = response[last_answer]["timestamp"]
    scores_df = pd.DataFrame([(p, s) for p, s in sorted_scores], columns=["Player", "Score"])
    # make a dataframe with columns player, score and last answer timestamp
    try:
        final_scores_df = pd.DataFrame([(p, s, list(answers[p].keys())[-1], answers[p][list(answers[p].keys())[-1]]["timestamp"]) for p, s in sorted_scores], columns=["Player", "Score", "Last Answer", "Timestamp"])
        # sort first by score and then by timestamp
        final_scores_df = final_scores_df.sort_values(by=["Score", "Timestamp"], ascending=[False, True])
 

        if st.button("📢 Show Winners"):

            st.balloons()
            c = st.columns([1, 1, 1, 4, 1, 1])
            c[3].markdown("<h2 style='color: #FFD700;'>Podium Winners</h2>", unsafe_allow_html=True)
            columna = st.columns(3)
            col = st.columns(4)
            if len(sorted_scores) > 0:
                with columna[1].container(border=True):
                    st.markdown(f"<h4>🥇 {final_scores_df.loc[0,'Player']}</h4>", unsafe_allow_html=True)
            if len(sorted_scores) > 1:
                with col[1].container(border=True):
                    st.markdown(f"<h4>🥈 {final_scores_df.loc[1,'Player']}</h4>", unsafe_allow_html=True)
            if len(sorted_scores) > 2:
                with col[2].container(border=True):
                    st.markdown(f"<h4>🥉 {final_scores_df.loc[2,'Player']}</h4>", unsafe_allow_html=True)
            # show all players ranking
            st.subheader("All Players Ranking:")
            # Display all players in order based on final_scores_df
            for i, (player, score, last_answer, timestamp) in enumerate(final_scores_df.itertuples(index=False)):
                st.markdown(f"<p style='font-size:24px; font-weight:bold;'>{i+1}. {player} - {score} points</p>", unsafe_allow_html=True)
                
        
            # st.write(sorted_scores)
            st.markdown("<p style='font-size:36px; font-weight:bold;'> Thank you for playing! </p>", unsafe_allow_html=True)

    except:
        st.write('Not all players have answered yet')
        # show who has not answered yet
        not_answered = set(st.session_state.players.keys()) - set(answers.keys())
        st.write("Players who have not answered yet:")
        for player in not_answered:
            st.write(player)
if __name__ == "__main__":
    pass
