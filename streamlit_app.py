import streamlit as st
import pandas as pd
from datetime import datetime

# --- Initialize session state for storing rows ---
if "excel_rows" not in st.session_state:
    st.session_state.excel_rows = []

# --- Helper Functions ---
def parse_number_with_commas(number_str):
    try:
        return float(str(number_str).replace(',', ''))
    except ValueError:
        return None

def calculate_days_left(start_date, end_date):
    delta = (end_date - start_date).days + 1
    return max(delta, 0)

def calculate_annualized_fee(amount, rate, days, days_in_year=365):
    return amount * rate * (days / days_in_year)

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        return None

# --- Streamlit App Setup ---
st.set_page_config(page_title="Fee Calculator", layout="centered")
st.title("Fee Calculation Tool")

# --- Input Fields ---
supp_bill_input = st.text_input("Enter the Supplemental Bill Date (MM/DD/YYYY)", "05/03/2025")
quarter_end_input = st.text_input("Enter the Quarter End Date (MM/DD/YYYY)", "06/30/2025")
amount_input = st.text_input("Enter the amount (e.g. 1,000,000)", "100000")
rate_input = st.text_input("Enter the annual rate (e.g. 0.0012)", "0.0007")
port_id_input = st.text_input("Custodian #")

# --- Hidden Logic Fields ---
exclude_input = ""
com_input = ""

# --- Input Parsing ---
amount = parse_number_with_commas(amount_input)
rate = float(rate_input) if rate_input.replace('.', '', 1).isdigit() else None
supp_bill_date = parse_date(supp_bill_input)
quarter_end_date = parse_date(quarter_end_input)

# --- Validation ---
if amount is None:
    st.error("Please enter a valid amount.")
elif rate is None:
    st.error("Please enter a valid rate.")
elif not supp_bill_date or not quarter_end_date:
    st.error("Please enter valid dates in MM/DD/YYYY format.")
elif supp_bill_date > quarter_end_date:
    st.error("Supplemental Bill Date must be before Quarter End Date.")
else:
    # --- Calculations ---
    days_left = calculate_days_left(supp_bill_date, quarter_end_date)
    fee = calculate_annualized_fee(amount, rate, days_left)

    st.subheader("\U0001F4C8 Fee Summary")
    st.write(f"**Days Left in Quarter**: {days_left}")
    st.success(f"**Calculated Fee**: ${fee:,.2f}")

    # --- Copy UDA Row ---
    txn_type = "CW Minus 1" if amount < 0 else "CD"
    uda_values = [
        "I", "1", exclude_input, com_input, "",
        supp_bill_date.strftime("%m/%d/%Y"),
        "Billing", "PI", port_id_input,
        "Asset", "", "Cash", txn_type, "1", "USD",
        f"{abs(amount):,.2f}"
    ]

    st.markdown("### Transaction CashFlow Quick Entry")
    st.code("\t".join(str(v) for v in uda_values), language="text")

    # --- Copy Manual Fee Credit Row ---
    comment_note = (
        f"Manual Credit due to a withdrawal of ${abs(amount):,.2f} on {supp_bill_date.strftime('%m/%d/%Y')}"
        if amount < 0 else
        f"Manual fee due to a deposit of ${amount:,.2f} on {supp_bill_date.strftime('%m/%d/%Y')}"
    )

    credit_values = [
        "I", "",
        quarter_end_date.strftime("%m/%d/%Y"),
        "Billing", "PI", port_id_input,
        "Manual Fee Credit", "CASH", "USD",
        f"{fee:,.2f}"
    ] + ["" for _ in range(9)] + [comment_note]

    st.markdown("### UDA Quick Entry")
    st.code("\t".join(str(v) for v in credit_values), language="text")

    # --- Additional Input Fields ---
    request_date_input = st.text_input("Request Date")
    submitter_input = st.text_input("Submitter")
    blk_input = st.text_input("BLK #")
    processor_input = st.text_input("Processor")
    auditor_input = st.text_input("Auditor")

    # --- Excel Table Row ---
    deposit_type = "Deposit" if amount > 0 else "Withdrawal"
    fee_or_credit = "Fee" if amount > 0 else "Credit"
    today = datetime.now().strftime("%m/%d/%Y")

    new_excel_row = {
        "Request Date": request_date_input,
        "Submitter": submitter_input,
        "BLK #": blk_input,
        "Custodian": port_id_input,
        "Transaction Date": supp_bill_date.strftime("%m/%d/%Y"),
        "Deposit/Withdrawal": deposit_type,
        "Manual Fee/Credit": fee_or_credit,
        "UDA Billing Date": quarter_end_date.strftime("%m/%d/%Y"),
        "Amount": f"{fee:,.2f}",
        "Processor": processor_input,
        "Date Processed": today,
        "Auditor": auditor_input,
        "Date Audited": "",
        "UDA": comment_note
    }

    if st.button("➕ Add to Excel Table"):
        st.session_state.excel_rows.append(new_excel_row)

# --- Display Excel Table ---
if st.session_state.excel_rows:
    st.markdown("### \U0001F4C4 Excel Table (All Entries)")

    df = pd.DataFrame(st.session_state.excel_rows)
    df.index = [''] * len(df)  # hide row numbers
    st.dataframe(df, use_container_width=True)

    # --- Delete Row Section ---
    st.markdown("### 🗑️ Delete a Row")
    row_options = [f"Row {i+1}" for i in range(len(st.session_state.excel_rows))]
    row_to_delete = st.selectbox("Select a row to delete:", row_options)

    if st.button("❌ Delete Selected Row"):
        index = row_options.index(row_to_delete)
        st.session_state.excel_rows.pop(index)
        st.rerun()

    # --- Clear All Rows ---
    if st.button("🧹 Clear All Rows"):
        st.session_state.excel_rows = []
        st.rerun()

st.markdown("---")
st.markdown("**Author: Kevin Vo**")
