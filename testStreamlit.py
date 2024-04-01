import streamlit as st
from streamlit_extras.stylable_container import stylable_container

# Create buttons with st.button
with stylable_container(
    "green",
    css_styles="""
    button {
        background-color: #00FF00;
        color: black;
    }""",
):
    button1_clicked = st.button("Button 1", key="button1")
with stylable_container(
    "red",
    css_styles="""
    button {
        background-color: #FF0000;

    }""",
):
    button2_clicked = st.button("Button 2", key="button2")

# Check button states and print messages
if st.button("Submit"):
    if button1_clicked:
        st.write("Button 1 pressed")
    elif button2_clicked:
        st.write("Button 2 pressed")