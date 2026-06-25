import streamlit as st
from services.persistence.exercise_repository import get_or_create_user

# persistence layer yaha hm call krk db me Query jo uska main used yaha hoga 
# yah ham login logic denge taki authorization kr ske

def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True
    
    st.title("🏋️‍♂️ AI Real-time GYM Trainer")
    st.markdown("### Welcome! Please enter a username to start.")

     # yaha hm Form me filed ka logic denge
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Name (unique)", placeholder="unique name e.g. princekhunt")
        submit_button = st.form_submit_button("Start Session", width="stretch")

# yaha hm validation dal denge
    if submit_button:
        if not username:
            st.error("Name cannot be empty.")
            return False
        # ye Db se layenge get_or_create_user ye persitent layer se aa raha hai
        user = get_or_create_user(username)
    
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False