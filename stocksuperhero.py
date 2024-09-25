import streamlit as st
import pandas as pd
import altair as alt  # Ensure Altair is imported
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

# Query to fetch data for symbols, spst, ind, and sec
response_dim = supabase.table('dim').select('sym, spst, cn, ind, sec').execute()

# Extract the list of unique values and populate DataFrame
if response_dim.data is None:
    st.error("Failed to fetch data from Supabase.")
    logging.error(f"Error in response_dim: {response_dim}")
else:
    df_dim = pd.DataFrame(response_dim.data)

# Function to filter dropdowns based on selections
def filter_dataframe(df, selected_spst, selected_ind, selected_sec):
    """Filter the DataFrame based on the selected dropdown values."""
    if selected_spst:
        df = df[df['spst'].isin(selected_spst)]
    if selected_ind:
        df = df[df['ind'].isin(selected_ind)]
    if selected_sec:
        df = df[df['sec'].isin(selected_sec)]
    return df

# Update dropdowns based on current selections
def update_dropdowns(df, selected_spst, selected_ind, selected_sec):
    """Update dropdown options based on the current filtered DataFrame."""
    # Keep the original DataFrame for available sectors
    available_spst = df['spst'].unique().tolist()
    available_sec = df['sec'].unique().tolist()  # Keep all sectors available

    # Check if any sector is selected
    if selected_sec:
        # Filter industries based on selected sectors
        filtered_df = df[df['sec'].isin(selected_sec)]
        available_ind = filtered_df['ind'].unique().tolist()
    else:
        # If no sector is selected, show all industries
        available_ind = df['ind'].unique().tolist()

    return available_spst, available_ind, available_sec, df

# Set default selections for dropdowns (if not in session_state)
if 'selected_spst' not in st.session_state:
    st.session_state['selected_spst'] = []
if 'selected_ind' not in st.session_state:
    st.session_state['selected_ind'] = []
if 'selected_sec' not in st.session_state:
    st.session_state['selected_sec'] = []

# Update dropdowns based on the current selections
available_spst, available_ind, available_sec, filtered_df = update_dropdowns(
    df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec']
)

# Multi-select dropdowns for Sector, Industry, and SPST
with st.expander("Filter by Sector, Industry, and SPST", expanded=True):
    # Sectors will always be available
    st.session_state['selected_sec'] = st.multiselect(
        "Select Sector", available_sec, default=st.session_state['selected_sec'], key="sector_multiselect"
    )

    # Update industries based on selected sectors
    available_spst, available_ind, available_sec, filtered_df = update_dropdowns(
        df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec']
    )

    # Industries dropdown should reflect only industries relevant to selected sectors
    st.session_state['selected_ind'] = st.multiselect(
        "Select Industry", available_ind, default=st.session_state['selected_ind'], key="industry_multiselect"
    )
    
    st.session_state['selected_spst'] = st.multiselect(
        "Select SPST Values", available_spst, default=st.session_state['selected_spst'], key="spst_multiselect"
    )

# Cross-filter the DataFrame based on the updated selections
filtered_df = filter_dataframe(df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec'])

# Stock symbol dropdown (sym + cn) remains outside the expander
filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']
selected_stock_symbol = st.selectbox(
    "Select Stock Symbol (Searchable)",
    filtered_df['sym_cn'],
)

# Extract selected symbol and get company name
if selected_stock_symbol:
    stock_symbol = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'sym'].values[0]
    company_name = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'cn'].values[0]

# Display filtered table inside an expanding/collapsible section
with st.expander("Show Filtered Companies Table", expanded=True):
    if not filtered_df.empty:
        # Display filtered data with images, company name, and more
        filtered_df['logo_url'] = filtered_df['sym'].apply(lambda x: f"https://ttok.s3.us-west-2.amazonaws.com/{x}.svg")
        filtered_df = filtered_df[['logo_url', 'cn', 'sym', 'spst', 'ind', 'sec']]
        
        # Set custom column names
        filtered_df.columns = ['Logo', 'Company Name', 'Symbol', 'SPST', 'Industry', 'Sector']
        
        # Display the DataFrame as an HTML table with images and sorting enabled
        def display_image(url):
            return f'<img src="{url}" style="border-radius:10px; width:50px; height:50px;" />'

        # Create a table with images in HTML
        st.write(filtered_df.to_html(escape=False, formatters={'Logo': display_image}), unsafe_allow_html=True)
        
        st.write(filtered_df)  # Also show as a regular table (sortable)
    else:
        st.write("No data matches the selected criteria.")

# Query the fact table and display the chart based on the selected symbol
if stock_symbol:
    response_fact = supabase.table('fact').select('dt_st, p').eq('sym', stock_symbol).execute()
    if response_fact.data:
        df_fact = pd.DataFrame(response_fact.data)
        if not df_fact.empty:
            # Plotting stock prices using Altair with visible axes, gridlines, and tooltips but without axis titles
            chart = alt.Chart(df_fact).mark_area().encode(
                x=alt.X('dt_st:T', axis=alt.Axis(title=None, grid=True)),  # Visible X-axis, gridlines, no title
                y=alt.Y('p:Q', axis=alt.Axis(title=None, grid=True)),      # Visible Y-axis, gridlines, no title
                tooltip=['dt_st:T', 'p:Q']  # Tooltip with date and price
            ).properties(
                title=f"{stock_symbol} Stock Prices",
                height=500
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No data available for the selected stock symbol.")
    else:
        st.error("Failed to fetch data from Supabase.")
