"""Ask page. Run with: streamlit run app.py"""
import os

import streamlit as st

MAX_QUESTIONS = 20  # per browser session, to protect the API key on a public URL

try:
    os.environ.setdefault("OPENROUTER_API_KEY", st.secrets["OPENROUTER_API_KEY"])
except Exception:
    pass  # no secrets file: fall back to the environment variable

from engine import answer  # noqa: E402  (after the key is in the environment)

st.set_page_config(page_title="Ask the Olist data")
st.title("Ask the Olist data")
st.caption("Type a business question. The app writes SQL, runs it, and shows its work.")

used = st.session_state.setdefault("used", 0)
question = st.text_input("Question", placeholder="Which 5 states have the most customers?")

if question:
    if used >= MAX_QUESTIONS:
        st.error(f"This session has reached its limit of {MAX_QUESTIONS} questions.")
        st.stop()
    st.session_state["used"] = used + 1

    with st.spinner("Writing and running SQL..."):
        result = answer(question)

    if result.refused:
        st.warning("This can't be answered from the data in this database.")
    elif result.error:
        st.error(f"The query failed: {result.error}")
        st.code(result.sql, language="sql")
    else:
        df = result.df
        st.dataframe(df, width="stretch")
        if len(df.columns) == 2 and len(df) > 1 and df.dtypes.iloc[1].kind in "if":
            st.bar_chart(df.set_index(df.columns[0]))
        st.code(result.sql, language="sql")
        if result.retried:
            st.caption("The first attempt failed; this is the corrected query.")
