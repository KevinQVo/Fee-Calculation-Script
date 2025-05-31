import streamlit as st
from datetime import datetime

st.title("Fee Calulation Script")

def parse_number_with_commas(number_str):
    try:
        return float(str(number_str).replace(',', ''))
    except ValueError:
        return None

def calculate_days_left(start_date, end_date):
    delta = (end_date - start_date).days
    return max(delta, 0)

def calculate_annualized_fee(amount, rate, days, days_in_year=365):
    return amount * rate * (days / days_in_year)

st.title("Fee Calculation Tool")


# Input Fields

supp_bill_date = st.date_input("Supplemental Bill Date", datetime.today())
quarter_end_date = st.date_input("Quarter End Date", datetime(2025, 3, 31))

amount_input = st.text_input("Enter the amount", "500,000")
rate_input = st.text_input("Enter the annual rate", "0.0012")

# Parse and calculate
amount = parse_number_with_commas(amount_input)
try:
    rate = float(rate_input)
except ValueError:
    rate = None

if amount is not None and rate is not None and supp_bill_date and quarter_end_date:
    days_left = calculate_days_left(supp_bill_date, quarter_end_date)
    fee = calculate_annualized_fee(amount, rate, days_left)

    st.subheader("📈 Fee Summary")
    st.write(f"**Amount**: ${amount:,.2f}")
    st.write(f"**Annual Rate**: {rate:.6f}")
    st.write(f"**Days Left in Quarter**: {days_left}")
    st.success(f"**Calculated Fee**: ${fee:,.2f}")
else:
    st.error("Please make sure amount and rate are valid numbers.")


st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
