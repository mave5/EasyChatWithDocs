import streamlit as st
import os
import tempfile
import git
import rags
from streamlit import session_state

def clone_repo(repo_url, local_dir="./data"):
    repo_name = os.path.basename(repo_url).split('.git')[0]
    repo_path = os.path.join(local_dir, repo_name)
    if not os.path.exists(repo_path):
        git.Repo.clone_from(repo_url, repo_path)
    else:
        print(f"{repo_path} exists!")
    return repo_path


# Streamlit app
st.title("Chat with your Documents")
if st.button("Reset Session"):
    st.session_state.clear()
    st.write("Session state reset!")

# Source selection
source_type = st.radio("Select source type:", ["File", "Directory", "GitHub Repository"])
file_types = st.text_input("Enter file types, example .py,.txt:", value="all")
if file_types.strip() in ("all", ""):
    file_types = None
else:
    file_types = file_types.strip().strip(",")
    file_types = file_types.split(",")
    file_types = [ft.strip() for ft in file_types]
    file_types = list(set(file_types))
if source_type == "File":
    uploaded_file = st.file_uploader("Choose files",
                                     accept_multiple_files=False,
                                     type=file_types)
    if uploaded_file and "ollama_chat" not in session_state:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name
        session_state.ollama_chat = rags.ChatWithDoc(temp_file_path)
        print(f"{uploaded_file.name} was indexed!")
elif source_type == "Directory":
    dir_path = st.text_input("Enter directory path:")
    if dir_path and os.path.isdir(dir_path) and "ollama_chat" not in session_state:
        session_state.ollama_chat = rags.ChatWithDoc(dir_path, file_types=file_types)
        print(f"{dir_path} was indexed!")
else:
    repo_url = st.text_input("Enter GitHub repository URL:")
    if repo_url and "ollama_chat" not in session_state:
        repo_path = clone_repo(repo_url)
        session_state.ollama_chat = rags.ChatWithDoc(repo_path)
        print(f"{repo_path} was indexed!")

if "history" not in session_state:
    session_state.history = []



if "ollama_chat" in session_state:
    st.markdown("## Chat with Documents")
    llm_model = st.selectbox('LLM Model', ('llama3', 'llama2', 'mistral'), index=0)
    user_input = st.chat_input("Say something")
    if user_input:
        chat_output = session_state.ollama_chat.query(user_input)
        print("-" * 30)
        print(chat_output)
        print("-" * 30)
        session_state.history.append((user_input, chat_output))

for message, response in session_state.history:
    st.markdown(f"**You**: **{message}**")
    st.markdown(f"Bot: {response}")
    st.markdown("-"*30)  # Empty line for spacing



