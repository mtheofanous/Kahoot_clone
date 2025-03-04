import streamlit as st
import json

def save_players():
    with open("players.json", "w") as f:
        json.dump(st.session_state.players, f, indent=4)
        
def load_players():
    if not st.session_state.players:
        try:
            with open("players.json", "r") as f:
                st.session_state.players = json.load(f)
        except FileNotFoundError:
            st.session_state.players = []
        

def add_players():
    st.title("Add Players")
    player = st.text_input("Enter the player:")
    if st.button("Add Player"):
        if "players" not in st.session_state:
            st.session_state.players = {}
        st.session_state.players[player
        ] = 0
        
        st.success("Player added!")
        
        
    if st.button("Save Players"):
        save_players()
        st.success("Players saved!")
        
    if st.button("Next"):
        st.session_state["current_page"] = "player_links"
        save_players()
        st.rerun()
        


if __name__ == "__main__":
    add_players()