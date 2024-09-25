import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client, Client
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase connection details
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.set_page_config(layout="wide")

# Initialize session state to store DataFrame if it doesn't exist
if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()
    logging.info("Initialized empty DataFrame in session state.")

# Query to fetch data for symbols, spst, ind, sec, and company name
response_dim = supabase.table('dim').select('sym, spst, cn, ind, sec').execute()

# Extract the list of unique values and populate DataFrame
if response_dim.data is None:
    st.error("Failed to fetch data from Supabase.")
    logging.error(f"Error in response_dim: {response_dim}")
else:
    df_dim = pd.DataFrame(response_dim.data)

# Extract unique values for SPST, Industry, and Sector
spst_values = df_dim['spst'].unique().tolist()
ind_values = df_dim['ind'].unique().tolist()
sec_values = df_dim['sec'].unique().tolist()

# Multi-select dropdowns for SPST, Industry (ind), and Sector (sec) with cross-filtering logic
selected_spst_values = st.multiselect("Select SPST Values", spst_values, default=spst_values)
selected_ind_values = st.multiselect("Select Industry", ind_values, default=ind_values)
selected_sec_values = st.multiselect("Select Sector", sec_values, default=sec_values)

# Cross-filter logic - apply filters one by one to maintain cross-dropdown relationships
filtered_df = df_dim.copy()

if selected_spst_values:
    filtered_df = filtered_df[filtered_df['spst'].isin(selected_spst_values)]

if selected_ind_values:
    filtered_df = filtered_df[filtered_df['ind'].isin(selected_ind_values)]

if selected_sec_values:
    filtered_df = filtered_df[filtered_df['sec'].isin(selected_sec_values)]

# Create a searchable dropdown for symbols that includes both 'sym' and 'cn'
filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']
selected_stock_symbol = st.selectbox(
    "Select Stock Symbol (Searchable)",
    filtered_df['sym_cn'],
)

# Extract selected symbol and get company name
if selected_stock_symbol:
    stock_symbol = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'sym'].values[0]
    company_name = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'cn'].values[0]

# Function to generate the logo URL based on stock symbol
def get_logo_url(symbol):
    return f"https://ttok.s3.us-west-2.amazonaws.com/{symbol}.svg"

# Collapsible section to show filtered data in a table
with st.expander("Show/Hide Filtered Company Data"):
    if not filtered_df.empty:
        # Add the company logo, company name, and related fields to the table
        filtered_df['logo_img'] = filtered_df['sym'].apply(lambda sym: f'<img src="{get_logo_url(sym)}" style="border-radius:10px; width:100px; height:100px;"/>')
        display_df = filtered_df[['logo_img', 'cn', 'sym', 'spst', 'ind', 'sec']]

        # Render the table as an HTML table with images
        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write("No companies match the selected filters.")

# Add the button to fetch and display the chart data for the selected stock symbol
if st.button('Fetch Stock Data'):
    if stock_symbol:
        response_fact = supabase.table('fact').select('dt_st, p').eq('sym', stock_symbol).execute()
        if response_fact.data:
            df_fact = pd.DataFrame(response_fact.data)
            if not df_fact.empty:
                # Plotting stock prices using Altair without axis titles
                chart = alt.Chart(df_fact).mark_area().encode(
                    x=alt.X('dt_st:T', axis=alt.Axis(title=None, grid=True)),  # Visible X-axis, gridlines, no title
                    y=alt.Y('p:Q', axis=alt.Axis(title=None, grid=True)),   
                    tooltip=['dt_st:T', 'p:Q']
                ).properties(
                    title=f"{stock_symbol} Stock Prices",
                    height=500
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No data available for the selected stock symbol.")
        else:
            st.error("Failed to fetch data from Supabase.")
    else:
        st.write("Please select a stock symbol first.")
