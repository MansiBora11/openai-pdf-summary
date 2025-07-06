import os
import streamlit as st
import pdfplumber
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# Function to summarize text using Groq
def summarize_text(text, prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an expert assistant that reads and summarizes PDFs."},
            {"role": "user", "content": f"{prompt}\n\n{text}"}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# Streamlit app UI
st.set_page_config(page_title="PDF Summarizer", layout="centered")
st.title("📄 PDF Summarizer with Groq")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

summary_type = st.selectbox(
    "Choose summary type",
    ["Brief Summary", "Bullet Points", "Extract Action Items"]
)

custom_prompt = {
    "Brief Summary": "Summarize this document briefly:",
    "Bullet Points": "Summarize the document in bullet points:",
    "Extract Action Items": "List all key action items from this document:"
}

if uploaded_file is not None:
    if st.button("Summarize"):
        with st.spinner("Extracting text..."):
            text = extract_text_from_pdf(uploaded_file)
            st.text_area("📄 Extracted Text (first 1000 characters)", text[:1000])

        if not text.strip():
            st.error("❌ No text could be extracted from the uploaded PDF. Please try another file.")
        else:
            with st.spinner("Summarizing with Groq..."):
                summary = summarize_text(text, custom_prompt[summary_type])

            st.subheader("Summary Output:")
            st.text_area(label="", value=summary, height=300)
