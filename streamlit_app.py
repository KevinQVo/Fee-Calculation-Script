import streamlit as st
from datetime import datetime

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

# --- Streamlit App ---

st.set_page_config(page_title="    Fee Calculator", layout="centered")
st.title("Fee Calculation Tool")

# Input Fields
supp_bill_input = st.text_input("Enter the Supplemental Bill Date (MM/DD/YYYY)", "03/04/2025")
quarter_end_input = st.text_input("Enter the Quarter End Date (MM/DD/YYYY)", "03/31/2025")
amount_input = st.text_input("Enter the amount (e.g. 1,000,000)", "500,000")
rate_input = st.text_input("Enter the annual rate (e.g. 0.0012)", "0.0012")

# Optional editable fields for UDA
st.markdown("### 🔧 UDA Fields (Optional Overrides)")
port_id_input = st.text_input("Port ID", "50202149")
exclude_input = st.text_input("Exclude", "")
com_input = st.text_input("COM", "")

# Parse inputs
amount = parse_number_with_commas(amount_input)
try:
    rate = float(rate_input)
except ValueError:
    rate = None

supp_bill_date = parse_date(supp_bill_input)
quarter_end_date = parse_date(quarter_end_input)

# Validation and Calculation
if amount is None:
    st.error("Please enter a valid amount.")
elif rate is None:
    st.error("Please enter a valid rate.")
elif supp_bill_date is None or quarter_end_date is None:
    st.error("Please enter valid dates in MM/DD/YYYY format.")
elif supp_bill_date > quarter_end_date:
    st.error("❌ Supplemental Bill Date must be before Quarter End Date.")
else:
    days_left = calculate_days_left(supp_bill_date, quarter_end_date)
    fee = calculate_annualized_fee(amount, rate, days_left)

    st.subheader("📈 Fee Summary")
    st.write(f"**Days Left in Quarter**: {days_left}")
    st.success(f"**Calculated Fee**: ${fee:,.2f}")

    # --- UDA Tool Output ---
    st.subheader("📄 UDA Tool Output")

    txn_type = "CW Minus 1" if amount < 0 else "CD"

    uda_headers = [
        "IUD", "Approved", "Exclude", "COM", "BLANK", "Date", "Source", "Unit", "Port ID",
        "Level", "BLANK", "Entity", "Txn Type", "Txn Count", "Local Curr", "Local Amt"
    ]

    uda_values = [
        "I", "1", exclude_input, com_input, "",
        supp_bill_date.strftime("%-m/%-d/%Y"),
        "Billing", "PI", port_id_input,
        "Asset", "", "Cash", txn_type, "1", "USD",
        f"{abs(amount):,.2f}"
    ]

    uda_df = {header: [value] for header, value in zip(uda_headers, uda_values)}
    st.dataframe(uda_df, use_container_width=True)
