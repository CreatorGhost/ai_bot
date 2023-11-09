import os
import streamlit as st
import time
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
import PyPDF2
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")


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
                st.session_state.logged_in = True  # Set logged_in in session_state to True
            else:
                st.error('Invalid username or password')

def run_chatbot(chat_history_key):
    # Load OpenAI API key
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Initialize the OpenAI model
    llm = ChatOpenAI(model="gpt-4-1106-preview", openai_api_key=openai_api_key)

    # Initialize the agent with tools
    tools = load_tools(["ddg-search"])
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True,k=7)

    # Load chat history into memory
    if chat_history_key in st.session_state:
        chat_history = st.session_state[chat_history_key]
        for message in chat_history:
            memory.save_context({'input':message['human']},{'output':message['AI']})

    agent = initialize_agent(
        tools, llm, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory
    )

    # Initialize the Streamlit callback handler
    st_callback = StreamlitCallbackHandler(st.container())

    # Display chat messages from history on app rerun
    for message in chat_history:
        with st.chat_message(message["human"]):
            st.markdown(message["AI"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        with st.expander(label="Chat History",expanded=False):
            st.write(chat_history)
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the agent
        response = agent.run(prompt, callbacks=[st_callback])
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(response)
        # Add assistant response to chat history
        st.session_state[chat_history_key].append({"human": prompt, "AI": response})
        
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    login()
else:
    mode = st.selectbox("Choose a mode", ["Chat", "Upload PDF and chat"])
    if mode == "Chat":
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        run_chatbot('chat_messages')
    elif mode == "Upload PDF and chat":
        if 'pdf_chat_messages' not in st.session_state:
            st.session_state.pdf_chat_messages = []
        pdf_file = st.file_uploader("Upload a PDF file", type=['pdf'])
        if pdf_file is not None:
            pdf_reader = PdfReader(pdf_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
            st.session_state.pdf_chat_messages.append({"human": pdf_text +  "Neded answers from the above file", "AI": ""})
            run_chatbot('pdf_chat_messages')