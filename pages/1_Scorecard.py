"""Scorecard page: reads the files evaluate.py writes into results/."""
import glob
import json
import os

import pandas as pd
import streamlit as st
import yaml

st.title("Scorecard")
st.caption("How often the generated SQL returns the same result as a hand-written correct query.")

paths = sorted(glob.glob("results/*.json"))
if not paths:
    st.info("No results yet. Run `python evaluate.py` first.")
    st.stop()

runs = {os.path.basename(p).removesuffix(".json"): json.load(open(p, encoding="utf-8")) for p in paths}
rows = pd.DataFrame(
    [{"run": name, **item} for name, run in runs.items() for item in run["items"]]
)

st.subheader("Accuracy by setup")
overall = rows.groupby("run")["correct"].agg(accuracy="mean", questions="count")
st.dataframe(overall.style.format({"accuracy": "{:.0%}"}), width="stretch")

st.subheader("Accuracy by difficulty")
by_difficulty = rows.pivot_table(index="run", columns="difficulty", values="correct", aggfunc="mean")
st.dataframe(by_difficulty.style.format("{:.0%}"), width="stretch")

st.subheader("Failures")
chosen = st.selectbox("Run", list(runs))
labels = {}
if os.path.exists("failure_labels.yaml"):
    labels = (yaml.safe_load(open("failure_labels.yaml", encoding="utf-8")) or {}).get(chosen, {})

failures = rows[(rows["run"] == chosen) & (~rows["correct"])]
if failures.empty:
    st.success("No failures in this run.")
for item in failures.itertuples():
    with st.expander(f"{item.id} ({item.difficulty}): {item.question}"):
        st.markdown(f"**Why it failed:** {labels.get(item.id, 'not labelled yet')}")
        st.markdown("Generated")
        st.code(item.pred_sql, language="sql")
        st.markdown("Correct")
        st.code(item.gold_sql, language="sql")
        if item.error:
            st.caption(f"Error: {item.error}")
