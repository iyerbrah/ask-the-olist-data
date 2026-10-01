# Ask the Olist data

Ask a business question in plain English; get the answer, a chart, and the SQL that produced it.
The Scorecard page reports how often the generated SQL is correct, measured against a
hand-written benchmark.

## Setup

1. `pip install -r requirements.txt`
2. Download the Olist dataset from Kaggle and unzip the CSVs into `data/`.
3. `python build_db.py`
4. Create `.streamlit/secrets.toml` containing one line: `OPENROUTER_API_KEY = "your-key"`.
5. `streamlit run app.py`

## Evaluate

    python evaluate.py --setup all

`evaluate.py` reads the key from the `OPENROUTER_API_KEY` environment variable, or from
`.streamlit/secrets.toml` if that is not set.
The model is set by `DEFAULT_MODEL` in `engine.py`, or the `ASKDATA_MODEL` environment variable.

## How it works

- `engine.py` builds the prompt, calls the model, checks the SQL is a single SELECT,
  and runs it on a read-only connection with external access switched off.
- `schema.md` holds the table notes sent with every question.
- `benchmark.yaml` holds questions with known-correct SQL. Scoring compares result
  tables, not SQL text. Row order, column order and column names are ignored, and extra
  columns in the generated result are allowed.
- `evaluate.py` runs four setups, each adding one thing, to show what each is worth.

## Results

60 questions: 15 easy (one table), 20 medium (joins and grouping), 15 hard (depend on a
business rule or a trap in the data), 10 that cannot be answered from this data.
One run per row, on 2 October 2026.

| Setup | Model | Accuracy | Easy | Medium | Hard | Unanswerable |
|---|---|---|---|---|---|---|
| Table and column names only | deepseek-v4-pro | 83% (50/60) | 15/15 | 19/20 | 6/15 | 10/10 |
| + schema notes | deepseek-v4-pro | 98% (59/60) | 15/15 | 19/20 | 15/15 | 10/10 |
| + worked examples | deepseek-v4-pro | 97% (58/60) | 15/15 | 18/20 | 15/15 | 10/10 |
| + retry on SQL error (full) | deepseek-v4-pro | 98% (59/60) | 15/15 | 19/20 | 15/15 | 10/10 |
| Full | deepseek-v4-flash | 95% (57/60) | 15/15 | 17/20 | 15/15 | 10/10 |

What the numbers say:

- **The schema notes do almost all the work.** Without them the model gets 6 of 15 hard
  questions; with them, 15 of 15. Every one of those failures was a missing business rule
  (what counts as revenue, what counts as a customer), not bad SQL.
- **The worked examples and the retry added nothing measurable.** The last three
  deepseek-v4-pro rows differ by one question, which is within run-to-run noise. The retry
  never fired: no generated query failed to execute.
- **The examples introduced a new failure.** After seeing a revenue example with a
  delivered-only filter, both models started adding that filter to questions that did not
  ask for it ("which category has the most items sold?"). All three failures of the cheaper
  model are this one mistake.
- **Refusing was easy here.** All 10 unanswerable questions were refused in every setup,
  which suggests those questions are too obviously out of scope to be a hard test.

Limits: each row is a single run, so differences of one or two questions are not
meaningful; 60 questions on one database is a small benchmark; and the hard questions
test rules that the schema notes state outright, so they measure whether the model follows
the notes, not whether it can discover the rules.

The full benchmark, all five runs, used about 376,000 input and 73,000 output tokens,
which cost roughly $0.09.
