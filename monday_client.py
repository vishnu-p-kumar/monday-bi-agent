import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from data_processor import process_board_data

# Load local .env variables if present
load_dotenv()


def get_secret(key_name: str, default: str = "") -> str:
    """
    Safely fetches credentials from Streamlit Cloud Secrets first,
    falling back to local environment variables (.env).
    """
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, default)


def fetch_board_items(board_id: str, api_key: str) -> list:
    """
    Executes a GraphQL query against Monday.com API v2 to retrieve items and column values.
    """
    if not api_key or not board_id:
        print(f"⚠️ Missing API Key or Board ID for board {board_id}")
        return []

    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "API-Version": "2023-10"
    }

    # GraphQL query fetching items and full column values
    query = """
    query ($board_id: [ID!]) {
      boards (ids: $board_id) {
        name
        items_page {
          items {
            id
            name
            column_values {
              id
              title
              text
              value
            }
          }
        }
      }
    }
    """

    payload = {
        "query": query,
        "variables": {"board_id": [str(board_id)]}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        boards = data.get("data", {}).get("boards", [])
        if not boards:
            print(f"⚠️ No boards found for ID: {board_id}")
            return []

        items = boards[0].get("items_page", {}).get("items", [])
        parsed_items = []

        for item in items:
            row = {
                "item_id": item.get("id"),
                "name": item.get("name")
            }
            # Capture column values by their column ID (hash)
            for col in item.get("column_values", []):
                col_id = col.get("id")
                col_text = col.get("text")
                if col_id:
                    row[col_id] = col_text if col_text is not None else ""
            parsed_items.append(row)

        return parsed_items

    except requests.exceptions.RequestException as req_err:
        print(f"❌ Network/API Error querying board {board_id}: {req_err}")
        return []
    except Exception as err:
        print(f"❌ Unexpected Error parsing board {board_id}: {err}")
        return []


def fetch_monday_board_data():
    """
    Main function called by app.py. Fetches raw board items from Monday.com
    and passes them to data_processor for clean mapping and normalization.
    """
    api_key = get_secret("MONDAY_API_KEY")
    deals_board_id = get_secret("DEALS_BOARD_ID")
    work_orders_board_id = get_secret("WORK_ORDERS_BOARD_ID")

    deals_raw = fetch_board_items(deals_board_id, api_key)
    work_orders_raw = fetch_board_items(work_orders_board_id, api_key)

    # Transform raw API response lists into clean DataFrames using data_processor
    deals_df, work_orders_df = process_board_data(deals_raw, work_orders_raw)

    return deals_df, work_orders_df


if __name__ == "__main__":
    print("Testing monday_client connection locally...")
    key = get_secret("MONDAY_API_KEY")
    deals_id = get_secret("DEALS_BOARD_ID")
    
    if key and deals_id:
        print(f"Fetching Deals Board ({deals_id})...")
        d_df, w_df = fetch_monday_board_data()
        print(f"✅ Success! Loaded {len(d_df)} Deals and {len(w_df)} Work Orders.")
        if not d_df.empty:
            print("Cleaned Deals Columns:", list(d_df.columns))
            print("First row sample:")
            print(d_df.iloc[0].to_dict())
    else:
        print("❌ Please configure MONDAY_API_KEY and DEALS_BOARD_ID in your .env file.")