import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import detect

def detect_language(text):
    try:
        # Detect the language
        lang = detect(text)
        return lang
    except Exception as e:
        print("Error detecting language:", str(e))
        return None

def translate_text(text, target_language='en'):
    try:
        # Detect the source language
        source_language = detect(text)
        if source_language is None:
            return None, "Language detection failed."

        # Translate the text
        translated_text = GoogleTranslator(source=source_language, target=target_language).translate(text)
        return translated_text, source_language
    except Exception as e:
        return None, str(e)

def main():
    st.set_page_config(page_title="Language Translation App", page_icon="🌐", layout="wide")

    # App title and description
    st.title("Language Translation App 🌐")
    st.markdown("Translate news articles from any language to English effortlessly!")

    # User input
    user_input = st.text_area("Enter news article in any language", height=200)

    # Translate button
    if st.button("Translate"):
        st.markdown("---")

        # Display detected language message
        detected_language = detect_language(user_input)
        if detected_language:
            st.info(f"Language detected: {detected_language}")

        st.subheader(f"Original Text ({detected_language}):")
        st.text_area("", value=user_input, height=300)

        # Display results
        st.markdown("---")
        st.subheader("Translated Text (English):")
        translated_text, _ = translate_text(user_input, target_language='en')
        if translated_text is not None:
            st.text_area("", value=translated_text, height=300)
        else:
            st.error("Translation failed. Please try again.")

    # Add GitHub link at the bottom right using CSS
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
