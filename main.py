import streamlit as st
import requests
import json

if "config_complete" not in st.session_state:
    st.session_state.config_complete = False
if "config" not in st.session_state:
    st.session_state.config = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

class Message:
    def __init__(self, message, role='user'):
        self.message = {
            "role": role,
            "content": message
            }
    def add(self):
        st.session_state.messages.append(self.message)
    def remove(self):
        st.session_state.messages.remove(self.message)

class OpenAIRequest:
    def __init__(self, stream=True):
        self.data = {
            "model": st.session_state.config['model'],
            "messages": st.session_state.messages,
            "temperature": st.session_state.config['temperature'],
            "max_tokens": st.session_state.config['tokens'],
            "stop": ["user", "system"],  # Stop on these tokens, which limits the response to a single message
            "stream": stream
        }
    def send(self):
        return requests.post(st.session_state.config['url'], json=self.data, stream=True)


def config():
    st.title('Configuration')
    with st.form(key='config_form'):
        url = st.text_input('OpenAI API Compatible Completions Endpoint:', 'http://localhost:8080/v1/chat/completions')
        model = st.text_input('Model Name:', 'llama-2-7b.Q3_K_L.gguf')
        prompt = st.text_input('System Prompt:', 'You are a helpful assistant.')
        tokens = int(st.text_input('Maximum Response Tokens:', 50))
        temperature = st.slider('Temperature', 0.0, 1.0, 0.9, 0.01)
        submitted = st.form_submit_button()
        if submitted:
            st.session_state.config = {
                'url': url,
                'model': model,
                'prompt': prompt,
                'tokens': tokens,
                'temperature': temperature,
            }
            Message(st.session_state.config['prompt'], 'system').add()
            st.session_state.config_complete = True
            st.rerun()

def chat_history():
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.write(f"**User:** {message['content']}")
        elif message['role'] == 'model':
            st.write(f"**Bot:** {message['content']}")
        elif message['role'] == 'system':
            st.write(f"**System:** {message['content']}")

def send_message(user_input, output_placeholder):
    message = Message(user_input)
    message.add()
    try:
        with OpenAIRequest().send() as response:
            message_content = ''
            for line in response.iter_lines(decode_unicode=True):
                try:
                    line = line[6:]
                    if line and line != '[DONE]':
                        line_content = json.loads(line)['choices'][0]['delta']['content']
                        message_content += line_content
                        output_placeholder.markdown(f"**Bot:** {message_content}")
                except KeyError:
                    continue
            Message(message_content, 'model').add()
    except requests.exceptions.ConnectionError:
        output_placeholder.markdown('**Connection Error. Please check the configuration.**')
        message.remove()

def app():
    st.title('LLM Interface')
    chat_history()
    input = st.empty()
    output = st.empty()
    with st.form(key='user_input_form', border=False):
        user_input = st.text_input('user_input', label_visibility='hidden')
        send = st.form_submit_button('Send')
        if send and user_input:
            input.markdown(f"**User:** {user_input}")
            send_message(user_input, output)
            send = False

    
if not st.session_state.config_complete:
    config()
else:
    app()
