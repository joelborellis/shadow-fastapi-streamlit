import aiohttp
import asyncio
import json
import streamlit as st

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")
st.subheader("🗨️ Chat with Shadow", divider=True)


async def main():

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize thread_id
    if "threadId" not in st.session_state:
        st.session_state.threadId = ""

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="./images/shadow.png"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar="./images/user.png"):
                st.markdown(message["content"])

    # --- Sidebar ---
    st.sidebar.header("Inputs")

    target_account = st.sidebar.selectbox(
        "Target Account",
        options=["-- Select an account --", "Glaxo", "Catepillar", "North Highland", "SBI Growth"],
        index=1
    )

    user_company = st.sidebar.selectbox(
        "User Company",
        options=["-- Select your company --", "Shadow", "North Highland"],
        index=1
    )

    demand_stage = st.sidebar.selectbox(
        "Demand Stage",
        options=["-- Select demand stage --", "Pre-Demand", "Interest", "Pain", "Need", "Project"],
        index=2
    )

    prompt = st.chat_input("Chat with Shadow...", accept_file=True, file_type=["pdf"])

    if prompt and prompt.text:
        st.chat_message("user", avatar="./images/user.png").markdown(prompt.text)

        st.session_state.messages.append({"role": "user", "content": prompt.text})

        # Point this to your actual SSE endpoint
        url = "https://shadow-endpoint-k33pqykzy3hqo-function-app.azurewebsites.net/shadow-sk"
        #url = "http://localhost:7071/shadow-sk-no-stream"
        # Construct request payload
        payload = {
            "query": prompt.text,
            "threadId": st.session_state.threadId,
            "additional_instructions": "Format your output in markdown",
            "user_company": user_company,
            "target_account": target_account,
            "demand_stage": demand_stage,
        }

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
                                        threadId= json_data.get("threadId", "")
                                        st.session_state.threadId = threadId

                                        if content:
                                            for line in content:
                                                # empty the container
                                                # assistant_reply_box.empty()
                                                # add the new text
                                                assistant_reply += line
                                                # display the new text
                                                assistant_reply_box.markdown(
                                                    assistant_reply
                                                )
                                                # await asyncio.sleep(0.001)

                                    except json.JSONDecodeError:
                                        print("Could not parse JSON:", line)

            # print(f"thread_id:  {thread_id}")
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_reply}
            )
    if prompt and prompt["files"]:
        pass  # TODO implement file upload


if __name__ == "__main__":
    asyncio.run(main())
