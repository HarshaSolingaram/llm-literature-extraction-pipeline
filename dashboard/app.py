import sqlite3
import pandas as pd
import streamlit as st


DB_FILE = "results/literature_pipeline.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM paper_extractions", conn)
    conn.close()
    return df


st.set_page_config(
    page_title="LLM Literature Extraction Pipeline",
    layout="wide"
)

st.title("LLM-Powered Scientific Literature Knowledge Extraction Pipeline")

try:
    df = load_data()

    st.subheader("Pipeline Summary")

    col1, col2 = st.columns(2)

    col1.metric("Total Papers Processed", len(df))
    col2.metric("Available Extraction Fields", len(df.columns) - 1)

    st.subheader("Search Extracted Knowledge")

    search_term = st.text_input("Search by keyword")

    if search_term:
        filtered_df = df[
            df.apply(
                lambda row: row.astype(str).str.contains(
                    search_term,
                    case=False,
                    na=False
                ).any(),
                axis=1
            )
        ]
    else:
        filtered_df = df

    st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Paper-Level Details")

    selected_paper = st.selectbox(
        "Select a paper",
        sorted(df["paper_name"].unique())
    )

    paper_row = df[df["paper_name"] == selected_paper].iloc[0]

    st.write("### Research Problem")
    st.write(paper_row["research_problem"])

    st.write("### Methodology")
    st.write(paper_row["methodology"])

    st.write("### Dataset")
    st.write(paper_row["dataset"])

    st.write("### Key Contribution")
    st.write(paper_row["key_contribution"])

    st.write("### Findings")
    st.write(paper_row["findings"])

    st.write("### Limitations")
    st.write(paper_row["limitations"])

    st.write("### Future Work")
    st.write(paper_row["future_work"])

except Exception as e:
    st.error("Database not found or pipeline not completed.")
    st.write("Run these commands first:")
    st.code(
        """
python src/text_extraction.py
python src/preprocessing.py
python src/llm_extraction.py
python src/smart_aggregation.py
python src/export_results.py
python src/database.py
streamlit run dashboard/app.py
        """
    )
    st.write(f"Error details: {e}")