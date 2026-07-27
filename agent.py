import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

load_dotenv()


def get_secret(key_name: str, default: str = "") -> str:
    """Reads Streamlit secrets first, then falls back to local environment variables."""
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, default)


class BIAgent:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        groq_api_key = get_secret("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is missing from environment variables.")
        self.client = Groq(api_key=groq_api_key)
        self.model_name = model_name

    def analyze_board(self, question: str, df_context: str) -> str:
        """Sends user question and formatted DataFrame context to Groq LLM for analysis."""
        system_prompt = (
            "You are an executive Business Intelligence assistant for Skylark Drones. "
            "You analyze tabular operational and sales data from Monday.com boards. "
            "Provide clear, concise, executive-level answers with key metrics, summaries, or risks."
        )

        user_prompt = f"""
Dataset context:
{df_context}

User Question: {question}

Please answer the question clearly using only the provided context.
"""

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        return response.choices[0].message.content


def _dataframe_context(deals_df: pd.DataFrame, work_orders_df: pd.DataFrame, max_rows: int = 25) -> str:
    """Builds a compact text snapshot of the loaded Monday.com data."""
    sections = []

    if deals_df is not None and not deals_df.empty:
        sections.append(
            "Deals data:\n"
            f"Rows: {len(deals_df)}\n"
            f"Columns: {', '.join(map(str, deals_df.columns))}\n"
            f"{deals_df.head(max_rows).to_string(index=False)}"
        )
    else:
        sections.append("Deals data: no records loaded.")

    if work_orders_df is not None and not work_orders_df.empty:
        sections.append(
            "Work orders data:\n"
            f"Rows: {len(work_orders_df)}\n"
            f"Columns: {', '.join(map(str, work_orders_df.columns))}\n"
            f"{work_orders_df.head(max_rows).to_string(index=False)}"
        )
    else:
        sections.append("Work orders data: no records loaded.")

    return "\n\n".join(sections)


def query_bi_agent(question: str, deals_df: pd.DataFrame, work_orders_df: pd.DataFrame) -> str:
    """Answers an ad-hoc BI question from the Streamlit app."""
    try:
        context = _dataframe_context(deals_df, work_orders_df)
        return BIAgent().analyze_board(question, context)
    except Exception as err:
        return f"Unable to generate an AI response: {err}"


def generate_leadership_briefing(
    deals_df: pd.DataFrame,
    work_orders_df: pd.DataFrame,
    selected_sectors: list[str],
    selected_period: str,
) -> str:
    """Generates a structured executive briefing from the current board data."""
    sectors = selected_sectors or ["All"]

    filtered_deals = deals_df
    filtered_work_orders = work_orders_df
    if "All" not in sectors:
        if deals_df is not None and not deals_df.empty and "Sector" in deals_df.columns:
            filtered_deals = deals_df[deals_df["Sector"].isin(sectors)]
        if work_orders_df is not None and not work_orders_df.empty and "Sector" in work_orders_df.columns:
            filtered_work_orders = work_orders_df[work_orders_df["Sector"].isin(sectors)]

    prompt = (
        "Create a concise leadership briefing for Skylark Drones.\n"
        f"Reporting period: {selected_period}\n"
        f"Target sectors: {', '.join(sectors)}\n\n"
        "Include pipeline status, operational highlights, visible risks, and recommended next actions."
    )

    try:
        context = _dataframe_context(filtered_deals, filtered_work_orders)
        return BIAgent().analyze_board(prompt, context)
    except Exception as err:
        return f"Unable to generate the briefing: {err}"


if __name__ == "__main__":
    from monday_client import fetch_monday_board_data

    print("Running pipeline test...")
    deals, work_orders = fetch_monday_board_data()
    query = "Provide a high-level summary of the top deals and operational status."

    print(f"\nQuerying Agent: '{query}'")
    answer = query_bi_agent(query, deals, work_orders)
    print("\n--- Executive Summary ---")
    print(answer)
