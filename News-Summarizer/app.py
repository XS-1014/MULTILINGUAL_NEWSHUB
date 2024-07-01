import streamlit as st
import requests
from newspaper import Article
from PIL import Image
from io import BytesIO
from transformers import pipeline


def fetch_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text, article.top_image if hasattr(article, 'top_image') else None

def query(payload):

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    # API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer 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"}
    response = requests.post(summarizer, headers=headers, json=payload)
    return response.json()

def main():
    st.set_page_config(
        page_title="News Summarizer",
        page_icon="📰",
        layout="wide"
    )

    st.title("📰 News Summarizer")

    # Sidebar configuration
    st.sidebar.subheader("User Input Options")
    input_option = st.sidebar.radio("", ["URL", "Text"])

    if input_option == "URL":
        # Collect user input (URL)
        url = st.sidebar.text_input("Enter the URL of the news article:")
        data, image_url = fetch_article(url) if url else ("", None)

    else:
        # Collect user input (Direct Text)
        data = st.sidebar.text_area("Enter the text for summarization:", height=300)
        image_url = None

    # Main content area
    st.sidebar.subheader("Summarization Settings")
    max_length = st.sidebar.slider("Select the maximum length for the summary:", min_value=20, max_value=500, value=150)
    show_original_text = st.sidebar.checkbox("Show Original Text", value=True)

    # Summarize when the user clicks the button
    if st.sidebar.button("Summarize"):
        min_length = max_length // 4
        payload = {
            "inputs": data,
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
