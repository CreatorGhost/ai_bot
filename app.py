import streamlit as st
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
from io import StringIO
import openai
from langchain.llms import OpenAI

# Load environment variables
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

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
        llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        return llm(input_text)

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
                full_response = ""
                for response in openai.ChatCompletion.create(
                    model="gpt-4-1106-preview",
                    messages=[{"role": m["role"], "content": m["content"]}
                              for m in st.session_state.messages], stream=True):
                    full_response += response.choices[0].delta.get("content", "")
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                with st.chat_message("assistant"):
                    st.markdown(full_response)

    elif option == 'Upload file':
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            response = generate_response(string_data)
            st.info(response)

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.session_state.logged_in = login()
else:
    main_page()
