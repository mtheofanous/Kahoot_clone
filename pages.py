import streamlit as st

from questions import create_questions
from players import add_players
from player_links import player_links
from game import game

# Global page configuration
st.set_page_config(
    page_title="Kahoot Clone",
    page_icon="🏠",
    layout="centered",  # Use "wide" as the base layout
)

def main():
    
    with st.container(border=False):

        # Initialize session state
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "create_questions"
        if "questions" not in st.session_state:
            st.session_state.questions = []
            
        # Page routing
        if st.session_state["current_page"] == "create_questions":
            create_questions()
            
        elif st.session_state["current_page"] == "add_players":
            add_players()
            
        elif st.session_state["current_page"] == "player_links":
            player_links()
        elif st.session_state["current_page"] == "game":
            game()
        # elif st.session_state["current_page"] == "results":
        #     results()
        # elif st.session_state["current_page"] == "answer_questions":
        #     answer_questions()


if __name__ == "__main__":
    main()
    
    