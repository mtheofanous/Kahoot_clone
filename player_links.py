import streamlit as st
import json
from urllib.parse import quote 
from players import *
from questions import *

def save_player_links():
    with open("player_links.json", "w") as f:
        json.dump(st.session_state.player_links, f, indent=4)
        
def load_player_links():
    if not st.session_state.player_links:
        try:
            with open("player_links.json", "r") as f:
                st.session_state.player_links = json.load(f)
        except FileNotFoundError:
            st.session_state.player_links = {}
            
def player_links():
    st.title("Player Links")
    base_url = "http://localhost:8501/"  # Change to your deployment URL
    for player in st.session_state.players.keys():
        player_url = base_url + "?player=" + quote(player)
        st.write(f"{player}: [Click here]({player_url})")
        
    if st.button("Save Player Links"):
        save_player_links()
        
    if st.button("Next"):
        st.session_state["current_page"] = "game"
        save_player_links()
        st.rerun()
        
if __name__ == "__main__":
    player_links()
        
 