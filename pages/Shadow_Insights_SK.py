import streamlit as st
import requests
import json
import time
import asyncio
import aiohttp

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")

st.title("Shadow Insights SK")

async def consume_sse(url: str, payload: str):
    """
    Connects to an SSE endpoint and prints out parsed JSON lines.
    """

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
                
                # Placeholder for the assistant's typing
                assistant_message = st.chat_message("assistant", avatar="./images/shadow.png")
                message_placeholder = assistant_message.empty()
                # A blank string to store the assistant's reply
                assistant_reply = ""

                async for chunk, _ in response.content.iter_chunks():
                    # Decode chunk into text
                    text_chunk = chunk.decode("utf-8")

                    # The server might send multiple lines in one chunk,
                    # so we split by newlines to handle them individually
                    for line in text_chunk.splitlines():
                        line = line.strip()
                        if not line:
                            # Skip empty lines
                            continue

                        if line.startswith("event: partial"):
                            # This is the SSE event descriptor line; skip it
                            continue

                        # If we reach here, line should be JSON (e.g. {"data": "some content"})
                        try:
                            json_data = json.loads(line)
                            # The server code yields {"data": "..."} so you can extract that:
                            content = json_data.get("data")
                            print("Received SSE data:", content)
                            assistant_reply += content
                            message_placeholder.markdown(assistant_reply)
                        except json.JSONDecodeError:
                            print("Could not parse JSON:", line)


async def main():
    if query := st.chat_input("Say something"):
        st.chat_message("user").write(query)

        # Point this to your actual SSE endpoint
        url = "http://localhost:7071/shadow-sk"

        # Construct request payload
        payload = {"query": query}
        await consume_sse(url, payload)

# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())