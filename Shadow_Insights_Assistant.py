import asyncio
import os
import streamlit as st

from semantic_kernel.kernel import Kernel
from semantic_kernel.agents.open_ai import OpenAIAssistantAgent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

# Import the modified plugin class
from plugins.shadow_insights_plugin import ShadowInsightsPlugin
from tools.searchshadow import SearchShadow
from tools.searchcustomer import SearchCustomer

ASSISTANT_ID = os.environ.get("ASSISTANT_ID")

# Initialize the search clients to pass to the Plugin
search_shadow_client = SearchShadow()
search_customer_client = SearchCustomer()

st.set_page_config(page_title="Shadow Assistant", page_icon="💬")
st.subheader("Chat with Shadow", divider=True)

# (1) Create the instance of the Kernel
kernel = Kernel()

# (2) Add plugin
# Instantiate ShadowInsightsPlugin and pass the search clients
shadow_plugin = ShadowInsightsPlugin(search_shadow_client, search_customer_client)

# (3) Register plugin with the Kernel
kernel.add_plugin(shadow_plugin, plugin_name="shadowRetrievalPlugin")


# A helper method to invoke the agent with the user input
async def invoke_agent(
    agent: OpenAIAssistantAgent,
    thread_id: str,
    input: str,
    history: list[ChatMessageContent],
) -> None:
    """Invoke the agent with the user input."""
    
    message_user = ChatMessageContent(role=AuthorRole.USER, content=input)
    await agent.add_chat_message(thread_id=thread_id, message=message_user)

    # Add the user message to the history
    history.append(message_user)
    
    st.session_state.messages.append(message_user) # add to the messages in session so we can write it on the sidebar

    #print(f"# {AuthorRole.USER}: '{input}'")
    st.chat_message("user", avatar="./images/user.png").markdown(input)

    # Stream the assistant's reply
    with st.chat_message("assistant", avatar="./images/shadow.png"):
        # Empty container to display the assistant's reply
        assistant_reply_box = st.empty()
        # A blank string to store the assistant's reply
        assistant_reply = ""

        first_chunk = True
        print(history)
        async for content in agent.invoke_stream(thread_id=thread_id, messages=history):
            if content.role != AuthorRole.TOOL:
                if first_chunk:
                    print(f"# {content.role}: ", end="", flush=True)
                    first_chunk = False
                assistant_reply += content.content
                # display the new text
                assistant_reply_box.markdown(assistant_reply)

                print(content.content, end="", flush=True)
                
        message_assistant = ChatMessageContent(role=AuthorRole.ASSISTANT, content=assistant_reply)
        st.session_state.messages.append(message_assistant)
        print()


async def main():
    
    # Initialize thread_id
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = ""
        
    # Initialize thread_id
    if "messages" not in st.session_state:
        st.session_state.messages = []

    agent = await OpenAIAssistantAgent.retrieve(
        id=ASSISTANT_ID, kernel=kernel, ai_model_id="gpt-4o"
    )
    prompt = st.chat_input("Say something")
    if prompt:
        # Check if thread_id is empty
        if st.session_state.thread_id.strip():
            # thread_id is not empty; retrieve it
            current_thread_id = st.session_state.thread_id
            #st.write(f"Current thread_id: {current_thread_id}")
        else:
            # thread_id is empty; create a new one
            current_thread_id = await agent.create_thread()
            st.session_state.thread_id = current_thread_id
            
        history: list[ChatMessageContent] = []

        await invoke_agent(agent, thread_id=current_thread_id, input=prompt, history=history)

        with st.sidebar:
            st.write(f"**Current thread_id:** {current_thread_id}")
            st.divider()
            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                st.write(f"**{message.role}:**  {message}")
            #for content in history:
            #    if content.content: # only write if the content is not blank
            #        st.write(f"-- {content.role}: \n{content.content}")
        
if __name__ == "__main__":
    asyncio.run(main())
