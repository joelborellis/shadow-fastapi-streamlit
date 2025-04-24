import streamlit as st
import os

from openai import OpenAI, OpenAIError


from dotenv import load_dotenv

# necessary Azure imports
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

load_dotenv()

st.subheader("🔍 Shadow Seller - Search Testing", divider=True)

with st.expander("⚙️ Search Parameter Settings"):
    with st.container():
        tab1, tab2 = st.tabs(["Top Docs", "Index"])
        # tab1.subheader("Set Top Docs")
        top = tab1.slider("Top Docs", 0, 5, 3)
        # tab3.subheader("Choose an Index")
        index_name = tab2.selectbox(
            "Choose Index", ("shadow-sales-index", "shadow-sales-index-customer", "shadow-customer")
        )
st.divider()

vector_store_address: str = os.environ.get("AZURE_SEARCH_ENDPOINT")
vector_store_key: str = os.environ.get("AZURE_SEARCH_ADMIN_KEY")
model_embed: str = os.environ.get("OPENAI_EMBED_MODEL")
credential_search = AzureKeyCredential(vector_store_key)
openai_client = OpenAI()


def get_embedding(query, model):
    try:
        text = query.replace("\n", " ")
        return (
            openai_client.embeddings.create(input=[text], model=model).data[0].embedding
        )
    except OpenAIError as ai_err:
        ai_response_msg = ai_err.body["message"]
        print(ai_response_msg)
        pass  # (optional)


search_client = SearchClient(
    endpoint=vector_store_address,
    index_name=index_name,
    credential=credential_search,
)


def search_api(query: str) -> str:
    vector_query = VectorizedQuery(
        vector=get_embedding(query, model_embed),
        k_nearest_neighbors=5,
        fields="contentVector",
    )

    r = search_client.search(
        search_text=query,  # this is set to query to force a hybrid search
        vector_queries=[vector_query],
        select=["title", "content", "category", "sourcefile", "content_tokens"],
        top=top,
    )
    with st.container():
        for doc in r:
            title = doc["title"]
            score = doc["@search.score"]
            sourcefile = doc["sourcefile"]
            category = doc["category"]
            total_tokens = doc["content_tokens"]
            st.write(f"**Title:** {title}")
            st.write(f"**Score:** {score}")
            st.write(f"**Sourcefile:** {sourcefile}")
            st.write(f"**Category:** {category}")
            st.write(f"**Total Tokens:** {total_tokens}")
            content = doc["content"]
            with st.expander("Content"):
                st.markdown(content)

def search_api_new(query: str) -> str:
    vector_query = VectorizedQuery(
        vector=get_embedding(query, model_embed),
        k_nearest_neighbors=5,
        fields="text_vector",
    )

    r = search_client.search(
        search_text=query,  # this is set to query to force a hybrid search
        vector_queries=[vector_query],
        select=["title", "chunk"],
        top=top,
    )
    with st.container():
        for doc in r:
            title = doc["title"]
            score = doc["@search.score"]
            chunk = doc["chunk"]
            st.write(f"**Title:** {title}")
            st.write(f"**Score:** {score}")
            with st.expander("Content"):
                st.markdown(chunk)

with st.form("search_form"):
    query = st.text_area(
        "Enter search query:",
        "Can you align the categories of stories to use across the sales process so I can build them into my account strategy?",
    )
    submitted = st.form_submit_button("Submit")

    st.divider()

    if submitted:
        if index_name.strip() == "shadow-customer":
            result = search_api_new(query)
        else:
            result = search_api(query)
