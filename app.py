import streamlit as st
import pandas as pd

st.set_page_config(page_title="User Usage Dashboard", layout="wide")
st.title("📱 User Usage Breakdown")

# Upload CSV
uploaded_file = st.file_uploader("Upload usage CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Cleanup
    df['Phone Number'] = df['Phone Number'].astype(str)
    df['Statement Date'] = pd.to_datetime(df['Statement Date'], dayfirst=True)
    df['Amount (VAT excl) '] = pd.to_numeric(df['Amount (VAT excl) '], errors='coerce')
    df['Volume (MB)'] = pd.to_numeric(df['Volume (MB)'], errors='coerce')
    df['Messages'] = pd.to_numeric(df['Messages'], errors='coerce')

    # Select date
    period_options = df['Statement Date'].dt.strftime('%Y-%m-%d').unique()
    selected_date = st.selectbox("Select billing period (statement date)", sorted(period_options, reverse=True))
    df_period = df[df['Statement Date'].dt.strftime('%Y-%m-%d') == selected_date]

    # Aggregate by phone number and category
    df_summary = df_period.groupby(['Phone Number', 'Category']).agg({
        'Volume (MB)': 'sum',
        'Messages': 'sum',
        'Amount (VAT excl) ': 'sum',
        'Destination Country': lambda x: ', '.join(sorted(set(x.dropna())))
    }).reset_index()

    df_summary.columns = [
        'Phone Number', 'Usage Category', 'Total Data (MB)',
        'Total Messages', 'Total Amount (€)', 'Countries Involved'
    ]

    # Select phone number
    selected_number = st.selectbox("Select a phone number", df_summary['Phone Number'].unique())

    # Display user summary
    fiche = df_summary[df_summary['Phone Number'] == selected_number]

    st.subheader(f"Usage summary for {selected_number} on {selected_date}")
    st.dataframe(fiche, use_container_width=True)

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🌐 Data usage (MB) by category")
        st.bar_chart(fiche.set_index('Usage Category')['Total Data (MB)'])

    with col2:
        st.markdown("#### ✉️ Messages by category")
        st.bar_chart(fiche.set_index('Usage Category')['Total Messages'])

    st.markdown("#### 💳 Total cost by category (€)")
    st.bar_chart(fiche.set_index('Usage Category')['Total Amount (€)'])

    # Country view
    st.markdown("#### 🌍 Countries involved")
    for _, row in fiche.iterrows():
        st.markdown(f"**{row['Usage Category']}**: {row['Countries Involved']}")

else:
    st.info("Please upload a usage CSV file to begin.")