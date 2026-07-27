import pandas as pd
import numpy as np

# Column mapping dictionary to translate Monday.com cryptic column hashes to standard executive labels
DEALS_COLUMN_MAP = {
    'text_mm5ncpg6': 'Owner',
    'text_mm5nr604': 'Company',
    'text_mm5ne413': 'Status',
    'text_mm5ntzme': 'Priority',
    'text_mm5ncq1b': 'Deal Value',
    'text_mm5nr6ag': 'Expected Close Date',
    'text_mm5ney30': 'Pipeline Stage',
    'text_mm5narqw': 'Product Line',
    'text_mm5nm2d9': 'Sector',
    'text_mm5nb16x': 'Created Date'
}

WORK_ORDERS_COLUMN_MAP = {
    'text_mm5n_wo_status': 'Order Status',
    'text_mm5n_wo_sector': 'Sector',
    'text_mm5n_wo_value': 'Order Value',
    'text_mm5n_wo_client': 'Client',
    'text_mm5n_wo_date': 'Execution Date'
}


def clean_deals_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans, normalizes, and handles messy data for the Deals board."""
    if df.empty:
        return df

    # 1. Rename raw column hashes to readable names if present
    df = df.rename(columns=DEALS_COLUMN_MAP)

    # 2. Clean numeric financial data (Deal Value)
    if 'Deal Value' in df.columns:
        df['Deal Value'] = (
            df['Deal Value']
            .astype(str)
            .str.replace(r'[^\d.]', '', regex=True)  # Remove currency symbols or commas
            .replace('', np.nan)
        )
        df['Deal Value'] = pd.to_numeric(df['Deal Value'], errors='coerce').fillna(0.0)

    # 3. Clean and standardize Date fields
    date_cols = [col for col in ['Expected Close Date', 'Created Date'] if col in df.columns]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        df[col] = df[col].fillna('Unscheduled')

    # 4. Normalize string categorical fields
    string_cols = ['Owner', 'Company', 'Status', 'Priority', 'Pipeline Stage', 'Product Line', 'Sector']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'None', ''], 'Unassigned / Unknown')

    return df


def clean_work_orders_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans, normalizes, and handles messy data for the Work Orders board."""
    if df.empty:
        return df

    # 1. Rename raw column hashes
    df = df.rename(columns=WORK_ORDERS_COLUMN_MAP)

    # 2. Clean numeric values
    if 'Order Value' in df.columns:
        df['Order Value'] = (
            df['Order Value']
            .astype(str)
            .str.replace(r'[^\d.]', '', regex=True)
            .replace('', np.nan)
        )
        df['Order Value'] = pd.to_numeric(df['Order Value'], errors='coerce').fillna(0.0)

    # 3. Clean Date fields
    if 'Execution Date' in df.columns:
        df['Execution Date'] = pd.to_datetime(df['Execution Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        df['Execution Date'] = df['Execution Date'].fillna('Unscheduled')

    # 4. Standardize Text fields
    string_cols = ['Order Status', 'Sector', 'Client']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'None', ''], 'Unassigned / Unknown')

    return df


def process_board_data(deals_raw: list, work_orders_raw: list):
    """Primary pipeline function to turn raw API list data into sanitized dataframes."""
    deals_df = pd.DataFrame(deals_raw) if deals_raw else pd.DataFrame()
    work_orders_df = pd.DataFrame(work_orders_raw) if work_orders_raw else pd.DataFrame()

    clean_deals = clean_deals_dataframe(deals_df)
    clean_work_orders = clean_work_orders_dataframe(work_orders_df)

    return clean_deals, clean_work_orders


if __name__ == "__main__":
    print("Testing Data Processor locally...")
    sample_raw = [{
        'item_id': '2805468452',
        'name': 'Naruto',
        'text_mm5ncpg6': 'OWNER_001',
        'text_mm5nr604': 'COMPANY089',
        'text_mm5ne413': 'Open',
        'text_mm5ncq1b': '489360',
        'text_mm5nr6ag': 'Thu Feb 26 2026 00:00:00 GMT+0000',
        'text_mm5nm2d9': 'Mining'
    }]
    cleaned_df, _ = process_board_data(sample_raw, [])
    print("Cleaned Sample Output:")
    print(cleaned_df[['Company', 'Owner', 'Status', 'Deal Value', 'Sector', 'Expected Close Date']])