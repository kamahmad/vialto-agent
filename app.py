import os
import json

import numpy as np
import faiss
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

load_dotenv(override=True)

@st.cache_resource
def load_data():
    """Loads reusable data."""
    
    index = faiss.read_index("article_embeddings.index")

    with open("article_data.json", "r", encoding='utf-8') as f:
        article_data = json.load(f)

    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    return index, article_data, model

def get_relevant_articles(query, top_k=3):
    """
    Chatbot function that retrieves relevant articles based on the user's query.
    """

    index, article_data, model = load_data()
    
    query_embedding = model.encode(query)

    # Perform a search in the FAISS index
    distances, indices = index.search(np.array([query_embedding]).astype('float32'), top_k)

    relevant_articles = []
    for i in range(top_k):
        if indices[0][i] != -1:
            relevant_articles.append(article_data[indices[0][i]])

    return relevant_articles

def generate_prompt(query):
    """
    Generates a prompt for the chatbot based on the user's query and the relevant articles.
    """
    
    relevant_articles = get_relevant_articles(query)
    print(relevant_articles)
    context = ""
    for article in relevant_articles:
        title = article.get('title', 'No Title')
        content = article.get('content', '')
        date_str = article.get('date', 'No Date')
        url = article.get('url', 'No URL')
        context += f"Title: {title}\nDate: {date_str}\nURL: {url}\nContent: {content}\n\n"
    
    if not context.strip():
        return "I'm sorry, but I couldn't find any relevant information in the provided articles to answer your question."

    system_prompt = f"""You are a helpful and friendly chatbot designed to answer questions based on the provided articles. Your expertise is limited to the topics of tax, global mobility, and immigration.

    **Instructions:**
    1.  Answer the user's question based only on the information provided in the "Context" section below.
    2.  Be concise and provide informative answers.
    3.  If the answer cannot be found within the context, politely refuse to answer by saying: "I'm sorry, but the answer to your question is not covered in the provided articles."
    4.  If the user asks a question outside the topics of tax, global mobility, or immigration, politely refuse to answer by saying: "I can only answer questions related to tax, global mobility, and immigration."
    5.  When referencing information from the articles, alwaysr cite the source URL(s) in brackets at the end of the sentence or paragraph.'
    6.  Do not invent or assume information not present in the articles.
    7.  Maintain a friendly and helpful tone.

    Question: {query}

    Context:
    {context}

    Answer:"""

    system_prompt = system_prompt.format(query=query, context=context)
    
    return system_prompt

def chatbot(query):
    """ Main function to interact with the chatbot. """
    
    prompt = generate_prompt(query)
    
    # Configure the Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Generate content using the Gemini model
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"An error occurred while generating the response: {e}"

st.title("Vialto Chatbot")

user_query = st.text_input("Ask me a question about tax, global mobility, or immigration:")

if user_query:
    response = chatbot(user_query)
    st.write("Chatbot:", response)
    st.write("If you have any further questions, feel free to ask!")


if __name__ == "__main__":
    pass
