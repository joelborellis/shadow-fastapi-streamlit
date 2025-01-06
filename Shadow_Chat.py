import aiohttp
import asyncio
import json
import streamlit as st

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")
st.title("Chat with Shadow")


async def fetch_response(url, payload):
    """Send a POST request to the server and return the response stream."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return response
                else:
                    st.error(f"Server responded with status code {response.status}")
                    return None
    except aiohttp.ClientError as e:
        st.error(f"An error occurred while connecting to the server: {str(e)}")
        return None


async def process_stream(response, assistant_reply_box):
    """Process the response stream and update the assistant's reply in real-time."""
    assistant_reply = ""
    print(response.status)
    try:
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
                                # If we reach here, line should be JSON (e.g. data: {"data": "some content"}).
                                try:
                                    # Handle extra "data:" prefix if present
                                    if line.startswith("data: "):
                                        line = line[len("data: ") :]

                                    json_data = json.loads(line)
                                    content = json_data.get("data", "")

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
                                            #await asyncio.sleep(0.005)

                                except json.JSONDecodeError:
                                    print("Could not parse JSON:", line)
    except asyncio.CancelledError:
        st.warning("Streaming was canceled.")
    except aiohttp.ClientPayloadError as e:
        st.error(f"Stream payload error: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred while processing the stream: {str(e)}")


async def main():
    prompt = st.chat_input("Say something")
    if prompt:
        st.chat_message("user").markdown(prompt)

        url = "http://localhost:7071/shadow-sk"  # Update to your actual endpoint
        payload = {"query": prompt}

        with st.chat_message("assistant"):
            assistant_reply_box = st.empty()
            response = await fetch_response(url, payload)
            if response:
                await process_stream(response, assistant_reply_box)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
