from groq import Groq
import streamlit as st
import re
from config import GROQ_API_KEY


@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except:
        api_key = GROQ_API_KEY
    return Groq(api_key=api_key)


def generate_caption(title, desc, custom_prompt):
    client = get_groq_client()
    prompt = custom_prompt.format(title=title, desc=desc)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
    )
    caption = response.choices[0].message.content.strip()

    lines = caption.split("\n")
    processed_lines = []

    for line in lines:
        line = line.strip()
        if line == ".":
            processed_lines.append(".")
            processed_lines.append("")
        else:
            processed_lines.append(line)

    result = "\n".join(processed_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result