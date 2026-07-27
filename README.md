# Monday BI Agent

Streamlit-based executive BI console for analyzing Monday.com sales pipeline and work order boards with a Groq-powered AI assistant.

## Features

- Syncs Deals and Work Orders data from Monday.com boards.
- Normalizes raw Monday.com column IDs into readable business fields.
- Shows executive KPIs for active deals, pipeline value, and work orders.
- Provides an AI copilot for questions about sales pipeline, revenue, and operations.
- Generates leadership briefings filtered by sector and reporting period.
- Includes a raw board inspector for reviewing the loaded dataframes.

## Project Structure

```text
.
├── app.py                 # Streamlit UI and dashboard workflow
├── agent.py               # Groq BI assistant and briefing helpers
├── data_processor.py      # Monday.com dataframe cleanup and normalization
├── monday_client.py       # Monday.com API client
├── requirements.txt       # Python dependencies
└── README.md
```

## Requirements

- Python 3.10+
- Monday.com API token
- Monday.com board IDs for Deals and Work Orders
- Groq API key

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Create a local `.env` file:

```env
MONDAY_API_KEY=your_monday_api_key
DEALS_BOARD_ID=your_deals_board_id
WORK_ORDERS_BOARD_ID=your_work_orders_board_id
GROQ_API_KEY=your_groq_api_key
```

The `.env` file is ignored by Git and should not be committed.

## Run the App

```bash
python -m streamlit run app.py
```

If the `streamlit` command is available on your PATH, this also works:

```bash
streamlit run app.py
```

## Streamlit Cloud Secrets

For Streamlit Cloud, add these secrets in the app settings:

```toml
MONDAY_API_KEY = "your_monday_api_key"
DEALS_BOARD_ID = "your_deals_board_id"
WORK_ORDERS_BOARD_ID = "your_work_orders_board_id"
GROQ_API_KEY = "your_groq_api_key"
```

## Local Checks

Run a syntax check:

```bash
python -m py_compile app.py agent.py monday_client.py data_processor.py
```

Run the data processor sample:

```bash
python data_processor.py
```

Run the Monday.com and AI pipeline smoke test:

```bash
python agent.py
```

The smoke test requires valid Monday.com and Groq credentials.

## Notes

- Monday.com column mappings live in `data_processor.py`.
- If board column IDs change in Monday.com, update `DEALS_COLUMN_MAP` or `WORK_ORDERS_COLUMN_MAP`.
- AI answers are generated only from the dataframe context sent by the app.
