import streamlit as st
from dotenv import load_dotenv
import os
import openai



from openai import OpenAI


# Load environment variables
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key
client = OpenAI(api_key=openai_api_key)

def login():
    col1, col2, col3 = st.columns([2,6,2])

    with col2:
        st.image("login.png", width=300,use_column_width=True)
        with st.form(key='login_form'):
            st.markdown("<h2 style='text-align: center; color: black;'>Login</h2>", unsafe_allow_html=True)
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')
            submit_button = st.form_submit_button('Login')
        
        if submit_button:
            valid_username = os.getenv("USER1_USERNAME")
            valid_password = os.getenv("USER1_PASSWORD")
            if username == valid_username and password == valid_password:
                return True
            else:
                st.error('Invalid username or password')

def main_page():
    st.title('🦜🔗 Ai Helper App')

    def generate_response(input_text):
        response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": input_text
            }
        ]
    )
        # The assistant's reply can be found in the last message in the response

        answer = response.choices[0].message.content
        return answer

    option = st.selectbox('Choose an option', ('Chat', 'Upload file'))
    if option == 'Chat':
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": "Welcome to the chat! You can start by typing a message in the box below."}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("What is up?")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner('Waiting for reply...'):
                full_response = generate_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(full_response)



if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.session_state.logged_in = login()
else:
    main_page()
