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

translations = {
    "en": {
        "Welcome to the Teladoc Quiz!": "Welcome to the Teladoc Quiz!",
        "Think you know it all? Let's find out!": "Think you know it all? Let's find out!",
        "🔑 Enter Game ID": "🔑 Enter Game ID",
        "🚀 Join Game": "🚀 Join Game",
        "❌ No game found with this Game ID.": "❌ No game found with this Game ID.",
        "Please enter a valid Game ID to proceed.": "Please enter a valid Game ID to proceed.",
        "Welcome to Teladoc Game": "Welcome to Teladoc Game",
        "Your Name": "Your Name",
        "🎮 Start Quiz": "🎮 Start Quiz",
        "Please enter a name.": "Please enter a name.",
        "Game ID not found. Please join through a valid game link.": "Game ID not found. Please join through a valid game link.",
        "This name is already taken for this game. Please choose another one.": "This name is already taken for this game. Please choose another one.",
        "❓ Question": "❓ Question",
        "of": "of",
        "Please enter a valid filename.": "Please enter a valid filename.",
        "Question set saved as": "Question set saved as",
        "Question set '": "Question set '",
        "loaded successfully!": "loaded successfully!",
        "Enter the question:": "Enter the question:",
        "Select the correct answer:": "Select the correct answer:",
        "Option": "Option",
        "How many answer options?": "How many answer options?",
        "➕ Add Question": "➕ Add Question",
        "✅ Question added!": "✅ Question added!",
        "The question cannot be empty.": "The question cannot be empty.",
        "All options must be filled in and not empty.": "All options must be filled in and not empty.",
        "Options must be unique — duplicates are not allowed.": "Options must be unique — duplicates are not allowed.",
        "Save Question Set": "Save Question Set",
        "💾 Save Set": "💾 Save Set",
        "📥 Load Question Set": "📥 Load Question Set",
        "🧹 Clear All Questions": "🧹 Clear All Questions",
        "⚠️ I’m sure I want to clear all questions": "⚠️ I’m sure I want to clear all questions",
        "🔄 Reorder Questions": "🔄 Reorder Questions",
        "📊 Quiz Results": "📊 Quiz Results",
        "📊 Results": "📊 Results",
        "🏆 Winners": "🏆 Winners",
        "Select Game ID to View Results": "Select Game ID to View Results",
        "Total Players:": "Total Players:",
        "Total Questions:": "Total Questions:",
        "Players who completed all questions:": "Players who completed all questions:",
        "📋 Questions & Answers": "📋 Questions & Answers",
        "✅": "✅",
        "🔹": "🔹",
        "Total Responses:": "Total Responses:",
        "Select Game ID": "Select Game ID",
        "📢 Show Winners": "📢 Show Winners",
        "Podium Winners": "Podium Winners",
        "🥇 First Place": "🥇 First Place",
        "🥈 Second Place": "🥈 Second Place",
        "🥉 Third Place": "🥉 Third Place",
        "🏅 All Players Ranking:": "🏅 All Players Ranking:",
        "🧠 Create Quiz": "🧠 Create Quiz",
        "🚀 Launch Game": "🚀 Launch Game",
        "📊 Game Stats": "📊 Game Stats",
        "🛠 Manage Games": "🛠 Manage Games",
        "🔒 Log out": "🔒 Log out",
        "Generate & Save Game": "Generate & Save Game",
        "Send this Game ID to players to join:": "Send this Game ID to players to join:",
        "No game sessions found yet.": "No game sessions found yet.",
        "No valid answer data found.": "No valid answer data found.",
        "🧰 Manage Question Sets & Games": "🧰 Manage Question Sets & Games",
        "🗃 Question Sets": "🗃 Question Sets",
        "🎮 Active Games": "🎮 Active Games",
        "⚠️ Confirm deletion": "⚠️ Confirm deletion",
        "🗑": "🗑",
        "Congratulations": "Congratulations",
        "You have completed the Teladoc Health quiz.": "You have completed the Teladoc Health quiz.",
        "Your final score:": "Your final score:",
        "points": "points",
        "If this were a medical consult... you'd be the chief doctor!": "If this were a medical consult... you'd be the chief doctor!",
        "Your Teladoc knowledge is stronger than a double shot of coffee ☕": "Your Teladoc knowledge is stronger than a double shot of coffee ☕",
        "Share your result with the team and challenge your coworkers.": "Share your result with the team and challenge your coworkers.",
    },
    "es": {
        "Welcome to the Teladoc Quiz!": "¡Bienvenido al Quiz de Teladoc!",
        "Think you know it all? Let's find out!": "¿Crees que lo sabes todo? ¡Descubrámoslo!",
        "🔑 Enter Game ID": "🔑 Introduce el ID del juego",
        "🚀 Join Game": "🚀 Unirse al Juego",
        "❌ No game found with this Game ID.": "❌ No se encontró ningún juego con este ID.",
        "Please enter a valid Game ID to proceed.": "Por favor, introduce un ID de juego válido para continuar.",
        "Welcome to Teladoc Game": "Bienvenido al Juego de Teladoc",
        "Your Name": "Tu Nombre",
        "🎮 Start Quiz": "🎮 Comenzar Quiz",
        "Please enter a name.": "Por favor, introduce un nombre.",
        "Game ID not found. Please join through a valid game link.": "ID de juego no encontrado. Únete mediante un enlace válido.",
        "This name is already taken for this game. Please choose another one.": "Este nombre ya está en uso para este juego. Por favor, elige otro.",
        "❓ Question": "❓ Pregunta",
        "of": "de",
        "Please enter a valid filename.": "Por favor, introduce un nombre de archivo válido.",
        "Question set saved as": "Conjunto de preguntas guardado como",
        "Question set '": "Conjunto de preguntas '",
        "loaded successfully!": "cargado correctamente!",
        "Enter the question:": "Introduce la pregunta:",
        "Select the correct answer:": "Selecciona la respuesta correcta:",
        "Option": "Opción",
        "How many answer options?": "¿Cuántas opciones de respuesta?",
        "➕ Add Question": "➕ Añadir Pregunta",
        "✅ Question added!": "✅ ¡Pregunta añadida!",
        "The question cannot be empty.": "La pregunta no puede estar vacía.",
        "All options must be filled in and not empty.": "Todas las opciones deben estar completas y no vacías.",
        "Options must be unique — duplicates are not allowed.": "Las opciones deben ser únicas. No se permiten duplicados.",
        "Save Question Set": "Guardar Conjunto de Preguntas",
        "💾 Save Set": "💾 Guardar Conjunto",
        "📥 Load Question Set": "📥 Cargar Conjunto de Preguntas",
        "🧹 Clear All Questions": "🧹 Borrar Todas las Preguntas",
        "⚠️ I’m sure I want to clear all questions": "⚠️ Estoy seguro de que quiero borrar todas las preguntas",
        "🔄 Reorder Questions": "🔄 Reordenar Preguntas",
        "📊 Quiz Results": "📊 Resultados del Quiz",
        "📊 Results": "📊 Resultados",
        "**📊 Results**": "**📊 Resultados**",
        "🏆 Winners": "🏆 Ganadores",
        "**🏆 Winners**": "**🏆 Ganadores**",
        "Select Game ID to View Results": "Selecciona el ID del Juego para ver los Resultados",
        "Total Players:": "Total de Jugadores:",
        "Total Questions:": "Total de Preguntas:",
        "Players who completed all questions:": "Jugadores que completaron todas las preguntas:",
        "📋 Questions & Answers": "📋 Preguntas y Respuestas",
        "✅": "✅",
        "🔹": "🔹",
        "Total Responses:": "Respuestas Totales:",
        "Select Game ID": "Seleccionar ID del Juego",
        "📢 Show Winners": "📢 Mostrar Ganadores",
        "Podium Winners": "Ganadores del Podio",
        "🥇 First Place": "🥇 Primer Lugar",
        "🥈 Second Place": "🥈 Segundo Lugar",
        "🥉 Third Place": "🥉 Tercer Lugar",
        "🏅 All Players Ranking:": "🏅 Clasificación de Todos los Jugadores:",
        "🧠 Create Quiz": "🧠 Crear Quiz",
        "🚀 Launch Game": "🚀 Lanzar Juego",
        "📊 Game Stats": "📊 Estadísticas",
        "🛠 Manage Games": "🛠 Gestionar",
        "🔒 Log out": "🔒 Salir",
        "Generate & Save Game": "Generar y Guardar Juego",
        "Send this Game ID to players to join:": "Envía este ID de juego a los jugadores para unirse:",
        "No game sessions found yet.": "No se encontraron sesiones de juego todavía.",
        "No valid answer data found.": "No se encontraron datos de respuestas válidas.",
        "🧰 Manage Question Sets & Games": "🧰 Gestionar Conjuntos de Preguntas y Juegos",
        "🗃 Question Sets": "🗃 Conjuntos de Preguntas",
        "🎮 Active Games": "🎮 Juegos Activos",
        "⚠️ Confirm deletion": "⚠️ Confirmar eliminación",
        "🗑": "🗑",
        "Congratulations": "¡Felicidades",
        "You have completed the Teladoc Health quiz.": "Has completado el quiz de Teladoc Health.",
        "Your final score:": "Tu puntuación final:",
        "points": "puntos",
        "If this were a medical consult... you'd be the chief doctor!": "Si esto fuera una consulta médica... ¡serías el/la doctor/a en jefe!",
        "Your Teladoc knowledge is stronger than a double shot of coffee ☕": "Tu conocimiento Teladoc está más fuerte que una taza doble de café ☕",
        "Share your result with the team and challenge your coworkers.": "Comparte tu resultado con el equipo y reta a tus compañeros.",
        "Hi team,": "Hola equipo,",
        "Join our quiz game by clicking the link below and entering the following Game ID:": "Únete a nuestro quiz haciendo clic en el siguiente enlace e introduciendo este ID de juego:",
        "Have fun and good luck!": "¡Diviértanse y mucha suerte!",
        "You can copy and paste this message into an email or Teams chat.": "Puedes copiar y pegar este mensaje en un correo o en Teams.",
        "Load a Saved Question Package": "Cargar un paquete de preguntas guardado",
        "Select a question set to manage:": "Selecciona un conjunto de preguntas para gestionar:",
        "📥 Load Question Set": "📥 Cargar Conjunto de Preguntas",
        "Question set": "Conjunto de preguntas",
        "loaded successfully!": "cargado correctamente!",
        "🧠 Create & Edit Questions": "🧠 Crear y Editar Preguntas",
        "Add questions, choose number of options, and set the correct one(s).": "Añade preguntas, elige el número de opciones y selecciona la(s) correcta(s).",
        "How many answer options?": "¿Cuántas opciones de respuesta?",
        "Enter the question:": "Introduce la pregunta:",
        "Option": "Opción",
        "Select the correct answer:": "Selecciona la respuesta correcta:",
        "➕ Add Question": "➕ Añadir Pregunta",
        "The question cannot be empty.": "La pregunta no puede estar vacía.",
        "All options must be filled in and not empty.": "Todas las opciones deben estar completas y no vacías.",
        "Options must be unique — duplicates are not allowed.": "Las opciones deben ser únicas. No se permiten duplicados.",
        "✅ Question added!": "✅ ¡Pregunta añadida!",
        "Welcome to the Quiz Game Manager!": "¡Bienvenido al Gestor de Quiz!",
        "✏️ Edit Mode": "✏️ Modo Edición",
        "Edit question text": "Editar texto de la pregunta",
        "Number of options": "Número de opciones",
        "Select correct answer": "Seleccionar respuesta correcta",
        "💾 Save Changes": "💾 Guardar Cambios",
        "✅ Question updated successfully.": "✅ Pregunta actualizada correctamente.",
        "— Select new position —": "— Selecciona nueva posición —",
        "Position": "Posición",
        "Move": "Mover",
        "to:": "a:",
        "Choose a unique new position for this question": "Elige una nueva posición única para esta pregunta",
        "🚀 Generate Game Link": "🚀 Generar Enlace del Juego",
        "🧩 Preview & Manage Questions": "🧩 Previsualizar y Gestionar Preguntas",


    }
}


def t(key):
    lang = st.session_state.get("lang", "en")
    return translations.get(lang, {}).get(key, key)

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

    # Extract player names from answers for easy access
    players_with_names = {}
    game_answers = answers.get(game_id, {})
    for pid, responses in game_answers.items():
        for q in responses.values():
            name = q.get("player_name")
            if name:
                players_with_names[pid] = name
            break

    history[game_id] = {
        "questions": questions,
        "answers": game_answers,
        "scores": scores.get(game_id, {}),
        "players": players_with_names
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
    if "lang" not in st.session_state:
        st.session_state.lang = "en"  # default language
        
    _ , lang = st.columns([10,1.5])

    with lang:
        lang_choice = st.selectbox(
        "🌐",
        options=["en", "es"],
        index=0 if st.session_state.lang == "en" else 1,
        format_func=lambda x: "Eng" if x == "en" else "Esp"
        )

    st.session_state.lang = lang_choice
    
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
        
        st.image(TELADOC_LOGO, width=350)

        st.markdown(f'<div class="login-header">{t("Welcome to the Teladoc Quiz!")}</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="login-sub">{t("Think you know it all? Let's find out!")}</div>""", unsafe_allow_html=True)

        game_id_input = st.text_input(t("🔑 Enter Game ID"), max_chars=10).upper().strip()

        if st.button(t("🚀 Join Game")):
            if game_id_input == 'TELADOC':
                st.session_state.logged_in = 'admin'
                st.rerun()
            elif game_id_input:
                if os.path.exists(GAMES_FILE):
                    try:
                        with open(GAMES_FILE, "r") as f:
                            games_data = json.load(f)
                    except json.JSONDecodeError:
                        st.error(t("Error loading games data."))
                        return
                else:
                    st.error(t("No games found."))
                    return

                if game_id_input in games_data:
                    #new changes
                    st.session_state.player_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                    st.session_state.logged_in = 'player'
                    st.session_state.game_id = game_id_input
                    st.session_state.current_question_index = 0
                    st.session_state.questions = games_data[game_id_input].get("questions", [])
                    st.rerun()
                else:
                    st.error(t("❌ No game found with this Game ID."))
            else:
                st.error(t("Please enter a valid Game ID to proceed."))



def player_page():

    st.title(t("Welcome to Teladoc Game"))

    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    col1, col2 = st.columns([4, 3])
    with col2:
        st.image(TELADOC_LOGO, width=300)

    player = st.text_input(t("Your Name"), max_chars=40)

    if st.button(t("🎮 Start Quiz")):
        if not player:
            st.error(t("Please enter a name."))
            return

        if "game_id" not in st.session_state:
            st.error(t("Game ID not found. Please join through a valid game link."))
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
            st.error(t("This name is already taken for this game. Please choose another one."))
        else:
            existing_players[game_id][player] = {"player_id": st.session_state.player_id}

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
            countdown_placeholder.markdown(
                f"<h1 style='text-align:center; font-size:80px;'>{i}</h1>", unsafe_allow_html=True
            )
            time.sleep(1)
        countdown_placeholder.markdown(
            f"<h1 style='text-align:center; font-size:80px;'>{t('Go!')}</h1>", unsafe_allow_html=True
        )
        time.sleep(1)
        st.session_state.countdown_done = True
        st.rerun()
    else:
        question_page()

        

def question_page():
    player_name = st.session_state.current_player
    player_id = st.session_state.get("player_id", player_name)
    game_id = st.session_state.get("game_id", "default")

    questions = st.session_state.get("questions", [])
    total_questions = len(questions)
    current_index = st.session_state.get("current_question_index", 0)

    if current_index >= total_questions:
        final_score = load_scores().get(game_id, {}).get(player_id, 0)
        all_answers = st.session_state.answers
        all_scores = load_scores()

        save_game_history(
            game_id=game_id,
            questions=questions,
            answers=all_answers,
            scores=all_scores
        )

        st.balloons()
        st.markdown(f"""
            <div style="background-color:#E9E4F6; padding:30px; border-radius:20px; text-align:center; margin-top:50px;">
                <h2 style="color:#4B2991;">🎉 {t("Congratulations")}, {player_name}! 🎉</h2>
                <p style="font-size:20px;">{t("You have completed the Teladoc Health quiz.")}</p>
                <p style="font-size:22px;"><strong>{t("Your final score:")}</strong> <span style="color:#00B1E1;">{final_score} {t("points")}</span></p>
                <hr style="margin: 20px 0;">
                <p style="font-size:18px;">🧠 {t("Your Teladoc knowledge is stronger than a double shot of coffee ☕")}</p>
                <p style="font-size:16px; color:#555;">{t("Share your result with the team and challenge your coworkers.")}</p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Load time limit from game config
    if os.path.exists(GAMES_FILE):
        with open(GAMES_FILE, "r") as f:
            games_data = json.load(f)
        time_limit = games_data.get(game_id, {}).get("time_limit", 30)
    else:
        time_limit = 30

    question = questions[current_index]
    correct = question["correct"]
    options = question["options"]

    # Setup timer per question
    question_timer_key = f"question_timer_{current_index}"
    timer_flag_key = f"timer_started_{question_timer_key}"

    if timer_flag_key not in st.session_state:
        st.session_state[question_timer_key] = time.time()
        st.session_state[timer_flag_key] = True

    elapsed = time.time() - st.session_state[question_timer_key]
    remaining_time = max(0, int(time_limit - elapsed))

    # Countdown display
    countdown_placeholder = st.empty()
    countdown_placeholder.markdown(
        f"<h2 style='color:red;'>⏱ {remaining_time} seconds left</h2>",
        unsafe_allow_html=True
    )

    # Progress bar
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

    st.markdown(f"#### ❓ {t('Question')} {current_index + 1} {t('of')} {total_questions}")
    st.markdown(f"<div class='question-card'><h3>{question['question']}</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    columns = [col1, col2]

    for idx, option in enumerate(options):
        with columns[idx % 2]:
            with st.form(key=f"form_{current_index}_{idx}"):
                submitted = st.form_submit_button(label=f"**{option}**", use_container_width=True)
                if submitted:
                    is_correct = option in correct if isinstance(correct, list) else option == correct

                    answers = load_answers()
                    if game_id not in answers:
                        answers[game_id] = {}
                    if player_id not in answers[game_id]:
                        answers[game_id][player_id] = {}

                    answers[game_id][player_id][f"Q{current_index + 1}"] = {
                        "selected_answer": option,
                        "correct_answer": correct,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "is_correct": is_correct,
                        "player_name": player_name
                    }

                    st.session_state.answers = answers
                    save_answers(answers)

                    scores = load_scores()
                    if game_id not in scores:
                        scores[game_id] = {}
                    if player_id not in scores[game_id]:
                        scores[game_id][player_id] = 0
                    if is_correct:
                        scores[game_id][player_id] += 1
                    save_scores(scores)

                    # Reset timer for next question
                    st.session_state.pop(question_timer_key, None)
                    st.session_state.pop(timer_flag_key, None)

                    st.session_state.current_question_index += 1
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Handle timeout after full page renders
    if remaining_time == 0:
        answers = load_answers()
        if game_id not in answers:
            answers[game_id] = {}
        if player_id not in answers[game_id]:
            answers[game_id][player_id] = {}

        answers[game_id][player_id][f"Q{current_index + 1}"] = {
            "selected_answer": "No Answer",
            "correct_answer": correct,
            "timestamp": datetime.datetime.now().isoformat(),
            "is_correct": False,
            "player_name": player_name
        }

        st.session_state.answers = answers
        save_answers(answers)

        scores = load_scores()
        if game_id not in scores:
            scores[game_id] = {}
        if player_id not in scores[game_id]:
            scores[game_id][player_id] = 0
        save_scores(scores)

        # Reset timer for next question
        st.session_state.pop(question_timer_key, None)
        st.session_state.pop(timer_flag_key, None)

        st.session_state.current_question_index += 1
        st.rerun()

    # Rerun every second if time is still ticking
    if remaining_time > 0:
        time.sleep(1)
        st.rerun()




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

    home, _, logout = st.columns([1, 4, 1])
    with home:
        if st.button(t("About")):
            clear_all_views()
            st.session_state.about = True

    with logout:
        if st.button(t("🔒 Log out")):
            st.session_state.logged_in = False
            st.session_state.game = False
            for key in list(st.session_state.keys()):
                if key not in ["logged_in"]:
                    del st.session_state[key]
            st.rerun()

    st.markdown(f"## 👋 {t('Welcome to the Quiz Game Manager!')}")

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

        st.success(t("✅ Question order updated successfully!"))
        st.rerun()

    # Display the logo
    TELADOC_LOGO = "https://images.ctfassets.net/l3v9j0ltz3yi/3o4PsPxE76WmyGqcsucKAI/adb5c6086ecb3a0a74876010c21f0c03/Teladoc_Health_Logo_PNG.png"
    st.sidebar.image(TELADOC_LOGO, width=300)

    with st.container(border=True):
        menu1, menu2, menu3, menu4 = st.columns([1.5, 1.5, 1.5, 1.5])

        with menu1:
            if st.button(f"**{t('🧠 Create Quiz')}**"):
                clear_all_views()
                st.session_state.new_game_active = True

        with menu2:
            if st.button(f"**{t('🚀 Launch Game')}**"):
                clear_all_views()
                st.session_state.game_link_active = True

        with menu3:
            if st.button(f"**{t('📊 Game Stats')}**"):
                clear_all_views()
                st.session_state.dashboard_active = True

        with menu4:
            if st.button(f"**{t('🛠 Manage Games')}**"):
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
            st.subheader(t("Load a Saved Question Package"))
            saved_filenames = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]
            selected_file = st.selectbox(t("Select a question set to manage:"), saved_filenames)

            if st.button(t("📥 Load Question Set")):
                st.session_state.questions = load_question_set(selected_file)
                save_questions(st.session_state.questions)
                st.success(f"{t('Question set')} '{selected_file}' {t('loaded successfully!')}")
                time.sleep(1)
                st.rerun()

            st.title(t("🧠 Create & Edit Questions"))
            st.write(t("Add questions, choose number of options, and set the correct one(s)."))

            # Initialize session state for questions
            if "questions" not in st.session_state:
                st.session_state.questions = []

            # Unique session state key counter for input fields
            if "input_key_counter" not in st.session_state:
                st.session_state.input_key_counter = 0

            # 🔢 Select number of options
            num_options = st.number_input(
                t("How many answer options?"),
                min_value=2, max_value=6, value=4, step=1, key="num_options_selector"
            )

            # Generate input keys
            question_key = f"question_{st.session_state.input_key_counter}"
            option_keys = [f"option_{st.session_state.input_key_counter}_{i}" for i in range(num_options)]
            correct_answer_key = f"correct_{st.session_state.input_key_counter}"

            # Question input
            question = st.text_input(t("Enter the question:"), key=question_key, max_chars=500)

            # Option inputs
            options = [st.text_input(f"{t('Option')} {i+1}", key=option_keys[i]) for i in range(num_options)]

            # Correct answer selection
            non_empty_options = [opt for opt in options if opt.strip()]
            correct_answer = st.selectbox(t("Select the correct answer:"), non_empty_options, key=correct_answer_key)

            # ➕ Add Question
            if st.button(t("➕ Add Question")):
                if not question.strip():
                    st.error(t("The question cannot be empty."))
                elif any(opt.strip() == "" for opt in options):
                    st.error(t("All options must be filled in and not empty."))
                elif len(set(opt.strip() for opt in options)) < len(options):
                    st.error(t("Options must be unique — duplicates are not allowed."))
                else:
                    new_question = {
                        "question": question.strip(),
                        "options": [opt.strip() for opt in options],
                        "correct": correct_answer.strip()
                    }
                    st.session_state.questions.append(new_question)
                    save_questions(st.session_state.questions)
                    st.success(t("✅ Question added!"))
                    st.session_state.input_key_counter += 1
                    time.sleep(0.5)
                    st.rerun()

            
        with st.container():
            st.subheader(t("🧩 Preview & Manage Questions"))

            if "questions" not in st.session_state:
                st.session_state.questions = load_questions()

            if not st.session_state.questions:
                st.warning(t("No questions found. Please create questions first."))
                st.stop()

            col1, col2 = st.columns(2)
            selected_positions = set()

            for i, question in enumerate(st.session_state.questions):
                col = col1 if i % 2 == 0 else col2
                with col:
                    with st.container(border=True):
                        action_col, _, delete_col = st.columns([1, 4, 1])

                        with action_col:
                            if st.button("✏️", key=f"edit_{i}"):
                                st.session_state.editing_index = i

                        with delete_col:
                            if st.button(f"**{t('🗑')}**", key=f"delete_{i}"):
                                st.session_state.questions.remove(question)
                                save_questions(st.session_state.questions)
                                st.success(t("Question deleted!"))
                                st.rerun()

                        if st.session_state.get("editing_index") == i:
                            st.markdown(f"**{t('✏️ Edit Mode')}**")

                            new_question = st.text_input(t("Edit question text"), value=question["question"], key=f"edit_q_{i}")

                            current_option_count = len(question["options"])
                            num_edit_options = st.number_input(
                                t("Number of options"),
                                min_value=2, max_value=6, value=current_option_count, step=1, key=f"edit_q_{i}_option_count"
                            )

                            new_options = []
                            for opt_idx in range(num_edit_options):
                                default_val = question["options"][opt_idx] if opt_idx < len(question["options"]) else ""
                                new_opt = st.text_input(f"{t('Option')} {opt_idx+1}", value=default_val, key=f"edit_q_{i}_opt_{opt_idx}")
                                new_options.append(new_opt)

                            valid_for_dropdown = [opt for opt in new_options if opt.strip()]
                            try:
                                index_of_correct = valid_for_dropdown.index(question["correct"]) if question["correct"] in valid_for_dropdown else 0
                            except ValueError:
                                index_of_correct = 0

                            new_correct = st.selectbox(
                                t("Select correct answer"),
                                valid_for_dropdown,
                                index=index_of_correct,
                                key=f"edit_q_{i}_correct"
                            )

                            if st.button(t("💾 Save Changes"), key=f"save_edit_{i}"):
                                if not new_question.strip():
                                    st.error(t("The question cannot be empty."))
                                elif any(opt.strip() == "" for opt in new_options):
                                    st.error(t("All options must be filled in and not empty."))
                                elif len(set(opt.strip() for opt in new_options)) < len(new_options):
                                    st.error(t("Options must be unique — duplicates are not allowed."))
                                else:
                                    st.session_state.questions[i] = {
                                        "question": new_question.strip(),
                                        "options": [opt.strip() for opt in new_options],
                                        "correct": new_correct.strip()
                                    }
                                    save_questions(st.session_state.questions)
                                    st.success(t("✅ Question updated successfully."))
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

                        display_options = [t("— Select new position —")] + [f"Position {p}" for p in available_positions]
                        previous_value = st.session_state.get(f"order_{i}", t("— Select new position —"))

                        selected = st.selectbox(
                            f"{t('Move')} Q{i+1} {t('to:')}",
                            display_options,
                            index=display_options.index(previous_value) if previous_value in display_options else 0,
                            key=f"order_{i}",
                            help=t("Choose a unique new position for this question"), label_visibility="collapsed"
                        )

                        if selected.startswith("Position"):
                            selected_pos_number = int(selected.replace("Position ", ""))
                            selected_positions.add(selected_pos_number)

            if st.button(t("🔄 Reorder Questions")):
                reorder_questions()

            st.subheader(t("Save Question Set"))
            st.markdown(t("Save the current set of questions to a custom file for later use."))
            filename = st.text_input(t("Enter a filename to save this question set (without extension)"))

            if os.path.exists(os.path.join(QUESTION_SETS_DIR, filename + ".json")):
                st.warning(t("A file with this name already exists. Saving will overwrite the existing file."))

            if st.button(t("💾 Save Set")):
                if filename:
                    save_question_set(filename)
                else:
                    st.error(t("Please enter a valid filename."))

            confirm_clear = st.checkbox(t("⚠️ I’m sure I want to clear all questions"), key="confirm_clear")

            if st.button(t("🧹 Clear All Questions")):
                if confirm_clear:
                    reset_questions_only()
                else:
                    st.warning(t("Please confirm clearing by checking the box."))

            if not st.session_state.questions:
                st.warning(t("No questions found. Please create questions first."))


    # --- START GAME SECTION ---
    if st.session_state.game_link_active:
        st.title(t("🚀 Generate Game Link"))
        question_files = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]

        if not question_files:
            st.warning(t("No question sets found. Please create and save a question set first."))
        else:
            selected_file = st.selectbox(t("Select a question set:"), question_files, label_visibility="collapsed")
            time_limit = st.number_input("⏱ Time limit per question (in seconds)", min_value=5, max_value=300, value=30)


            if st.button(t("Generate & Save Game")):
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
                    "questions": selected_questions,
                    "time_limit": time_limit
                }

                with open(GAMES_FILE, "w") as f:
                    json.dump(games_data, f, indent=4)

                st.success(f"{t('Game ID')} {game_id} {t('created and saved!')}")
                st.markdown(f"{t('Send this Game ID to players to join:')} {game_id}")
                share_message = (
                    f"{t('Hi team,')}\n\n"
                    f"{t('Join our quiz game by clicking the link below and entering the following Game ID:')}\n\n"
                    f"🌐 https://kahootclone.streamlit.app/\n"
                    f"🆔 {t('Game ID')}: {game_id}\n\n"
                    f"{t('Have fun and good luck!')}"
                )

                st.code(share_message, language="markdown")
                st.markdown(t("You can copy and paste this message into an email or Teams chat."))


    # --- DASHBOARD SECTION ---
    # --- DASHBOARD SECTION ---
    if st.session_state.dashboard_active:
        page = st.sidebar.radio('', [t("**📊 Results**"), t("**🏆 Winners**")], label_visibility="collapsed")

        history = load_game_history()
        available_game_ids = list(history.keys())

        if not available_game_ids:
            st.warning(t("No game sessions found yet."))
            return

        if page == t("**📊 Results**"):
            st.title(t("📊 Quiz Results"))
            selected_game_id = st.selectbox(t("Select Game ID to View Results"), available_game_ids, key="selectbox_results")
            game_id = selected_game_id
            st.session_state.game_id = game_id

            selected_data = history.get(game_id, {})
            game_answers = selected_data.get("answers", {})
            questions = selected_data.get("questions", [])
            player_names = selected_data.get("players", {})

            st.write(f"{t('Total Players:')} {len(game_answers)}")
            st.write(f"{t('Total Questions:')} {len(questions)}")

            st.write(t("Players who completed all questions:"))
            for player_id, response in game_answers.items():
                name = player_names.get(player_id, player_id)
                if len(response) == len(questions):
                    st.write(f"✅ {name}")
                    st.session_state.completed_players.add(player_id)

            st.subheader(t("📋 Questions & Answers"))

            for i, question in enumerate(questions):
                with st.expander(f"{t('Question')} {i+1}: {question['question']}"):
                    response_counts = {opt: 0 for opt in question["options"]}
                    total_responses = 0

                    for player_id, responses in game_answers.items():
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
                            st.markdown(f"✅ **{opt}** — {count} {t('responses')} ({percentage:.1f}%)")
                        else:
                            st.markdown(f"🔹 {opt} — {count} {t('responses')} ({percentage:.1f}%)")

                    st.markdown(f"**{t('Total Responses:')}** {total_responses}")

        elif page == t("**🏆 Winners**"):
            st.title(t("🏆 Winners"))
            selected_game_id = st.selectbox(t("Select Game ID"), available_game_ids, key="selectbox_winners")
            game_id = selected_game_id
            st.session_state.game_id = game_id

            selected_data = history.get(game_id, {})
            game_answers = selected_data.get("answers", {})
            game_scores = selected_data.get("scores", {})
            player_names = selected_data.get("players", {})

            data = []
            for player_id, response in game_answers.items():
                if response:
                    last_q = list(response.keys())[-1]
                    timestamp_str = response[last_q].get("timestamp", "9999-12-31T23:59:59")
                    try:
                        timestamp = datetime.datetime.fromisoformat(timestamp_str)
                    except:
                        timestamp = datetime.datetime.max
                    score = game_scores.get(player_id, 0)
                    name = player_names.get(player_id, player_id)
                    data.append((name, score, timestamp))

            if not data:
                st.warning(t("No valid answer data found."))
            else:
                sorted_data = sorted(data, key=lambda x: (-x[1], x[2]))

                if st.button(t("📢 Show Winners")):
                    st.balloons()
                    st.markdown(f"<h2 style='color: #FFD700;'>{t('Podium Winners')}</h2>", unsafe_allow_html=True)

                    col_podium = st.columns(3)
                    if len(sorted_data) > 0:
                        with col_podium[1].container(border=True):
                            st.markdown(f"<h4>{t('🥇 First Place')}: {sorted_data[0][0]} - {sorted_data[0][1]} pts</h4>", unsafe_allow_html=True)
                    if len(sorted_data) > 1:
                        with col_podium[0].container(border=True):
                            st.markdown(f"<h4>{t('🥈 Second Place')}: {sorted_data[1][0]} - {sorted_data[1][1]} pts</h4>", unsafe_allow_html=True)
                    if len(sorted_data) > 2:
                        with col_podium[2].container(border=True):
                            st.markdown(f"<h4>{t('🥉 Third Place')}: {sorted_data[2][0]} - {sorted_data[2][1]} pts</h4>", unsafe_allow_html=True)

                    with st.sidebar.container():
                        st.markdown(f"## {t('🏅 All Players Ranking:')}")
                        for i, (name, score, timestamp) in enumerate(sorted_data):
                            st.markdown(f"<p style='font-size:18px;'>{i+1}. <strong>{name}</strong> — {score} pts</p>", unsafe_allow_html=True)

    # --- MANAGE SETS & GAMES SECTION ---
    if st.session_state.get("manage_sets_games_active", False):
        st.header(t("🧰 Manage Question Sets & Games"))

        # --- Manage Question Sets ---
        st.subheader(t("🗃 Question Sets"))
        sets = [f for f in os.listdir(QUESTION_SETS_DIR) if f.endswith(".json")]
        if not sets:
            st.info(t("No question sets found."))
        else:
            for qfile in sets:
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(qfile)
                with col3:
                    confirm_key = f"confirm_qset_{qfile}"
                    st.checkbox(t("⚠️ Confirm deletion"), key=confirm_key)
                with col2:
                    if st.button(f"**{t('🗑')}**", key=f"delete_qset_{qfile}"):
                        if st.session_state.get(confirm_key, False):
                            delete_question_set(qfile)
                        else:
                            st.warning(t("Please confirm deletion first."))

        # --- Manage Active Games ---
        st.subheader(t("🎮 Active Games"))
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE, "r") as f:
                try:
                    games = json.load(f)
                except json.JSONDecodeError:
                    games = {}
        else:
            games = {}

        if not games:
            st.info(t("No active games found."))
        else:
            for game_id in list(games.keys()):
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(f"{t('Game ID')}: {game_id} — {t('Set')}: {games[game_id]['question_file']}")
                with col3:
                    confirm_key = f"confirm_game_{game_id}"
                    st.checkbox(t("⚠️ Confirm deletion"), key=confirm_key)
                with col2:
                    if st.button(f"**{t('🗑')}**", key=f"delete_game_{game_id}"):
                        if st.session_state.get(confirm_key, False):
                            del games[game_id]
                            with open(GAMES_FILE, "w") as f:
                                json.dump(games, f, indent=4)
                            st.success(f"{t('Game')} {game_id} {t('deleted.')}")
                            st.rerun()
                        else:
                            st.warning(t("Please confirm deletion first."))

           
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