import streamlit as st
import json

def save_questions():
    with open("questions.json", "w") as f:
        json.dump(st.session_state.questions, f, indent=4)
        
def load_questions():
    if not st.session_state.questions:
        try:
            with open("questions.json", "r") as f:
                st.session_state.questions = json.load(f)
        except FileNotFoundError:
            st.session_state.questions = []
            
def save_scores():
    with open("game_scores.json", "w") as f:
        json.dump(st.session_state.scores, f, indent=4)
        
def load_scores():
    if not st.session_state.scores:
        try:
            with open("game_scores.json", "r") as f:
                st.session_state.scores = json.load(f)
        except FileNotFoundError:
            st.session_state.scores = {}

# create questions, 4 options, and correct answer
def create_questions():
    st.title("Create Questions")
    question = st.text_input("Enter the question:")
    options = [st.text_input(f"Option {i+1}") for i in range(4)]
    correct_answer = st.selectbox("Select the correct answer:", options)
    
    if st.button("Add Question"):
        st.session_state.questions.append({
            "question": question,
            "options": options,
            "correct": correct_answer
        })
        st.success("Question added!")
    
    st.subheader("Current Questions:")
    for idx, q in enumerate(st.session_state.questions):
        st.write(f"{idx+1}. {q['question']}")
        for opt in q["options"]:
            st.write(f" - {opt}")
    
    if st.button("Save Questions"):
        save_questions()
        st.success("Questions saved!")
        
    if st.button("Next"):
        st.session_state["current_page"] = "add_players"
        save_questions()
        st.rerun()
        
if __name__ == "__main__":
    create_questions()
# Page 4: Results
# elif page == "Results":