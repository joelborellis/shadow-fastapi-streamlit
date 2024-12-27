import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")

st.title("Stream Chat with Shadow Assistant")

# show all the session states in the sidebar
with st.sidebar:
    (st.write(st.session_state))
    

# Initialize thread_id in session state if not present
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = ""

#user_query = st.text_input("Your question:")
#submit_button = st.button("Send")

if user_query := st.chat_input("Say something"):
#if submit_button and user_query.strip():
    # Display the user's message
    st.chat_message("user").write(user_query)

    with st.status("Asking Shadow...", expanded=True) as response_status:
        # Placeholder for the assistant's typing
        assistant_message = st.chat_message("assistant", avatar="./images/shadow.png")
        message_placeholder = assistant_message.empty()

        # Construct request payload
        payload = {
            "query": user_query,
            "thread_id": st.session_state['thread_id']
        }

        
        # Call the streaming FastAPI endpoint
        #url = "http://localhost:7071/shadow"  # replace with your actual endpoint
        url = "https://shadow-fastapi-6azng7abetzb2-function-app.azurewebsites.net/shadow"  # replace with your actual endpoint
        #print(payload)
    
        response = requests.post(url, json=payload, stream=True)

        if response.status_code == 200:
                    accumulated_text = ""
                    # Process line-by-line streaming response
                    for line in response.iter_lines(decode_unicode=True):
                        if line:
                            try:
                                # Parse the top-level line of JSON
                                data = json.loads(line)
                                #print(f"Data:  {data}")
                                
                                # Extract the 'message' field which is a JSON string
                                message_data = data.get("message", "{}")
                                
                                # Parse the nested JSON in 'message'
                                #message_data = json.loads(message_str)
                                
                                # Extract thread_id and response from the nested message_data
                                returned_thread_id = message_data.get("thread_id", "")
                                text_chunk = message_data.get("response", "")

                                # Update thread_id in session state if it's provided
                                if returned_thread_id:
                                    st.session_state['thread_id'] = returned_thread_id

                                # If response is not a string, convert it to JSON text
                                if isinstance(text_chunk, (dict, list)):
                                    text_chunk = json.dumps(text_chunk)

                                # Simulate typing by adding characters one by one
                                for char in text_chunk:
                                    accumulated_text += char
                                    message_placeholder.markdown(accumulated_text)
                                    time.sleep(0.01)  # Adjust typing speed as desired
                            
                                response_status.update(label="Complete!", state="complete", expanded=True)
                            except json.JSONDecodeError:
                                # If there's an issue decoding JSON, just continue
                                pass
                    
        else:
            st.error(f"Error from server: {response.status_code}")