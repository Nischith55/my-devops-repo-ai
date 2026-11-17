from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

st.set_page_config(page_title='GenAI Chat UI', page_icon='💬', layout='centered')
st.title('💬 GenAI Chat (Streamlit → FastAPI → vLLM)')
st.caption('Beginner demo project with clear architecture and deployment path.')

with st.expander('Current endpoint configuration'):
    st.write({'API_BASE_URL': API_BASE_URL})

prompt = st.text_area('Enter your prompt', height=120, placeholder='Example: Explain Kubernetes service mesh in simple terms.')
temperature = st.slider('Temperature', min_value=0.0, max_value=2.0, value=0.2, step=0.1)
max_tokens = st.slider('Max tokens', min_value=32, max_value=1024, value=256, step=32)

if st.button('Generate response', type='primary'):
    if not prompt.strip():
        st.warning('Please enter a prompt first.')
    else:
        payload = {
            'prompt': prompt,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        try:
            with st.spinner('Calling backend...'):
                resp = requests.post(f'{API_BASE_URL}/chat', json=payload, timeout=90)

            if resp.ok:
                data = resp.json()
                st.success('Response received')
                st.markdown('### Answer')
                st.write(data['answer'])
                st.caption(f"Model: {data['model']} | Mock mode: {data['mock_mode']}")
            else:
                st.error(f'Backend error ({resp.status_code}): {resp.text}')
        except requests.RequestException as exc:
            st.error(f'Failed to connect to backend: {exc}')
