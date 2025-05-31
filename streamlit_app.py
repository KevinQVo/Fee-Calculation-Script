import streamlit as st
from datetime import datetime

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

# --- Streamlit App ---

st.set_page_config(page_title="Fee Calculator", layout="centered")
st.title("📊 Fee Calculation Tool")


# Input Fields
amount_input = st.text_input("Enter the amount (e.g. 1,000,000)", "500,000")
rate_input = st.text_input("Enter the annual rate (e.g. 0.0012)", "0.0012")

supp_bill_date = st.date_input("Supplemental Bill Date", datetime.today())
quarter_end_date = st.date_input("Quarter End Date", datetime(datetime.today().year, 3, 31))

# Parse and calculate
amount = parse_number_with_commas(amount_input)
try:
    rate = float(rate_input)
except ValueError:
    rate = None

if amount is not None and rate is not None and supp_bill_date and quarter_end_date:
    if supp_bill_date > quarter_end_date:
        st.error("❌ Supplemental Bill Date must be before Quarter End Date.")
    else:
        days_left = calculate_days_left(supp_bill_date, quarter_end_date)
        fee = calculate_annualized_fee(amount, rate, days_left)

        st.subheader("📈 Fee Summary")
        st.write(f"**Amount**: ${amount:,.2f}")
        st.write(f"**Annual Rate**: {rate:.6f}")
        st.write(f"**Supplemental Bill Date**: {supp_bill_date.strftime('%m/%d/%Y')}")
        st.write(f"**Quarter End Date**: {quarter_end_date.strftime('%m/%d/%Y')}")
        st.write(f"**Days Left in Quarter**: {days_left}")
        st.success(f"**Calculated Fee**: ${fee:,.2f}")
else:
    st.warning("👆 Please enter a valid amount and rate to calculate the fee.")
