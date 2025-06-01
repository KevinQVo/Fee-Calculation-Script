import streamlit as st
from datetime import datetime

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
supp_bill_input = st.text_input("Enter the Supplemental Bill Date (MM/DD/YYYY)")
quarter_end_input = st.text_input("Enter the Quarter End Date (MM/DD/YYYY)", "06/30/2025")
amount_input = st.text_input("Enter the amount (e.g. 1,000,000)")
rate_input = st.text_input("Enter the annual rate (e.g. 0.0012)")

# --- UDA Optional Fields ---
st.markdown("### 🔧 UDA Fields (Optional Overrides)")
port_id_input = st.text_input("Custodian #")
exclude_input = st.text_input("Exclude", "")
com_input = st.text_input("COM", "")

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

    st.subheader("📈 Fee Summary")
    st.write(f"**Days Left in Quarter**: {days_left}")
    st.success(f"**Calculated Fee**: ${fee:,.2f}")

    # --- Copy UDA Row ---
    txn_type = "CW Minus 1" if amount < 0 else "CD"
    uda_values = [
        "I", "1", exclude_input, com_input, "",
        supp_bill_date.strftime("%-m/%-d/%Y"),
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
        quarter_end_date.strftime("%-m/%-d/%Y"),
        "Billing", "PI", port_id_input,
        "Manual Fee Credit", "CASH", "USD",
        f"{fee:,.2f}"
    ] + [""] * 9 + [comment_note]

    st.markdown("### UDA Quick Entry")
    st.code("\t".join(str(v) for v in credit_values), language="text")
  
