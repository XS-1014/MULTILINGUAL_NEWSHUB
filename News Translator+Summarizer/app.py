import streamlit as st
import requests
import os
from newspaper import Article
from PIL import Image
from io import BytesIO
from deep_translator import GoogleTranslator
from langdetect import detect
from transformers import pipeline

# Function to detect language
def detect_language(text):
    try:
        # Detect the language
        lang = detect(text)
        return lang
    except Exception as e:
        print("Error detecting language:", str(e))
        return None

# Function to translate text to English
def translate_text(text):
    try:
        # Detect the source language
        source_language = detect(text)
        if source_language is None:
            return None, "Language detection failed."

        # Translate the text to English
        translated_text = GoogleTranslator(source=source_language, target='en').translate(text)
        return translated_text, source_language
    except Exception as e:
        return None, str(e)

# Function to fetch article content from URL
def fetch_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text, article.top_image if hasattr(article, 'top_image') else None

# Function to query Hugging Face API for summarization
def query(payload):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    # api_key = os.environ.get("HUGGING_FACE_API_KEY")
    # headers = {"Authorization": f"Bearer {api_key}"}
    headers = {"Authorization": f"Bearer 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"}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Main function
def main():
    # Enable session state to store translated text
    session_state = st.session_state
    if not hasattr(session_state, 'translated_text'):
        session_state.translated_text = ""

    st.set_page_config(
        page_title="Multifunctional News App",
        page_icon="🌐",
        layout="wide"
    )

    st.title("MultiLingual NewsHub 🌐📰")
    st.markdown("Breaking Language Barriers: Explore Global News, Summarized in English.")

    # Sidebar configuration
    st.sidebar.subheader("User Input Options")
    input_option = st.sidebar.radio("", ["URL", "Text"])

    if input_option == "URL":
        # Collect user input (URL)
        url = st.sidebar.text_input("Enter the URL of the news article:")
        data, image_url = fetch_article(url) if url else ("", None)

    else:
        # Collect user input (Direct Text)
        data = st.sidebar.text_area("Enter the text for translation and summarization in any language:", height=300)
        image_url = None

    # Translate when the user clicks the button
    if st.sidebar.button("Translate to En"):
        translated_text, detected_language = translate_text(data)

        st.markdown("---")

        # Display detected language message
        if detected_language:
            st.info(f"Language detected: {detected_language}")

        st.subheader(f"Original Text ({detected_language}):")
        st.text_area("", value=data, height=300)

        st.markdown("---")
        st.subheader("Translated Text (English):")
        st.text_area("", value=translated_text, height=300)

        # Use the translated text for summarization
        session_state.translated_text = translated_text

    st.sidebar.subheader("Summarization Settings")
    max_length = st.sidebar.slider("Select the maximum length for the summary:", min_value=20, max_value=500, value=150)
    show_original_text = st.sidebar.checkbox("Show Original Text", value=True)

    # Summarize when the user clicks the button
    if st.sidebar.button("Summarize"):
        # Check if translated text is available
        if not session_state.translated_text:
            st.warning("Please translate the text first.")
        else:
            min_length = max_length // 4
            payload = {
                "inputs": session_state.translated_text,
                "parameters": {"min_length": min_length, "max_length": max_length},
            }

            # Query the Hugging Face API
            output = query(payload)

            # Display the original text and summary side by side
            col1, col2 = st.columns(2)

            if show_original_text:
                with col1:
                    st.subheader("Original Text:")
                    st.text_area(" ", value=data, height=500)

                with col2:
                    st.subheader("Summary:")
                    if isinstance(output, list) and output and "summary_text" in output[0]:
                        st.write(output[0]["summary_text"])
                    elif isinstance(output, dict) and "summary_text" in output:
                        st.write(output["summary_text"])
                    else:
                        st.warning("Summary not available. Please check the input and try again.")

                    # Add 2 lines space
                    st.text("\n\n")

                    # Display the image under the summary
                    if image_url:
                        st.image(image_url, caption="Image from the article", use_column_width=True)

            else:
                # If original text is not shown, make summary and image larger
                st.subheader("Summary:")
                if isinstance(output, list) and output and "summary_text" in output[0]:
                    st.write(output[0]["summary_text"])
                elif isinstance(output, dict) and "summary_text" in output:
                    st.write(output["summary_text"])
                else:
                    st.warning("Summary not available. Please check the input and try again.")

                # Add 2 lines space
                st.text("\n\n\n")

                # Display the image under the summary
                if image_url:
                    st.image(image_url, caption="Image from the article", use_column_width=True)

    # Add GitHub link in the side panel
    st.markdown(
        '<div style="position: fixed; bottom: 10px; right: 10px;">'
        '<a href="https://github.com/sg-sparsh-goyal" target="_blank">'
        '<img src="https://img.shields.io/badge/GitHub-Profile-blue?style=social&logo=github" alt="GitHub">'
        '</a>'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
