import aiohttp
import asyncio
import json
import streamlit as st

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")
st.subheader("Chat with Shadow", divider=True)


async def main():

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize thread_id
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = ""

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="./images/shadow.png"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar="./images/user.png"):
                st.markdown(message["content"])

    prompt = st.chat_input("Say something")
    if prompt:
        st.chat_message("user", avatar="./images/user.png").markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Point this to your actual SSE endpoint
        url = "https://shadow-fastapi-sk-rgrhhk5mtlr7i-function-app.azurewebsites.net/shadow-sk-no-stream"
        #url = "http://localhost:7071/shadow-sk"
        # Construct request payload
        payload = {"query": prompt, "thread_id": st.session_state.thread_id}

        # Stream the assistant's reply
        with st.chat_message("assistant", avatar="./images/shadow.png"):

            # Empty container to display the assistant's reply
            assistant_reply_box = st.empty()

            # A blank string to store the assistant's reply
            assistant_reply = ""
            thread_id = ""
            with st.spinner("Shadow is thinking..."):
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status == 200:
                            async for chunk, _ in response.content.iter_chunks():
                                # Decode chunk into text
                                text_chunk = chunk.decode("utf-8")

                                # The server might send multiple lines in one chunk,
                                # so we split by newlines to handle them individually
                                for line in text_chunk.splitlines(True):
                                    line = line.strip()
                                    if not line:
                                        # Skip empty lines
                                        continue
                                    # If we reach here, line should be JSON (e.g. data: {"data": "some content"}).
                                    try:
                                        # Handle extra "data:" prefix if present
                                        if line.startswith("data: "):
                                            line = line[len("data: ") :]

                                        json_data = json.loads(line)
                                        content = json_data.get("data", "")
                                        thread_id = json_data.get("thread_id", "")
                                        st.session_state.thread_id = thread_id

                                        if content:
                                            for line in content:
                                                # empty the container
                                                #assistant_reply_box.empty()
                                                # add the new text
                                                assistant_reply += line
                                                # display the new text
                                                assistant_reply_box.markdown(
                                                    assistant_reply
                                                )
                                                #await asyncio.sleep(0.001)

                                    except json.JSONDecodeError:
                                        print("Could not parse JSON:", line)

            #print(f"thread_id:  {thread_id}")
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_reply}
            )  


if __name__ == "__main__":
    asyncio.run(main())
