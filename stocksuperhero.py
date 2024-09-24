import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client, Client
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

st.set_page_config(layout="wide")

# Initialize session state to store DataFrame if it doesn't exist
if 'df' not in st.session_state:
    st.session_state['df'] = pd.DataFrame()
    logging.info("Initialized empty DataFrame in session state.")

# Query to fetch data for the select boxes (symbols and spst values)
response_dim = supabase.table('dim').select('sym, spst, cn').execute()  # Ensure 'cn' (company name) is included

# Extract the list of unique 'spst' values and symbols ('sym')
if response_dim.data is None:
    st.error("Failed to fetch data from Supabase.")
    logging.error(f"Error in response_dim: {response_dim}")
    symbols = []  # Empty list in case of failure
    spst_values = []  # Empty list for multi-select
else:
    # Create a DataFrame from the response data
    df_dim = pd.DataFrame(response_dim.data)
    
    # Extract unique 'spst' column values for the multi-select dropdown
    spst_values = df_dim['spst'].unique().tolist()
    logging.info(f"Fetched unique 'spst' values for multi-select: {spst_values}")

# Multi-select for selecting multiple 'spst' values
if spst_values:
    selected_spst_values = st.multiselect("Select SPST Values", spst_values, default=spst_values)
    logging.info(f"Selected SPST values: {selected_spst_values}")

    # Filter symbols based on the selected SPST values
    if selected_spst_values:
        filtered_symbols = df_dim[df_dim['spst'].isin(selected_spst_values)]['sym'].unique().tolist()
    else:
        filtered_symbols = df_dim['sym'].unique().tolist()

    logging.info(f"Filtered symbols based on selected SPST values: {filtered_symbols}")
else:
    filtered_symbols = []

# If there are filtered symbols, populate the select box for symbols
if filtered_symbols:
    stock_symbol = st.selectbox('Select Stock Symbol', filtered_symbols)
    logging.info(f"Selected stock symbol: {stock_symbol}")

    # Get the corresponding 'spst' value and company name for the selected symbol
    selected_row = df_dim.loc[df_dim['sym'] == stock_symbol]
    if not selected_row.empty:
        spst_value = selected_row['spst'].values[0]
        company_name = selected_row['cn'].values[0]
        
        # Create columns layout
        col1, col2 = st.columns(2)

        with col1:
            # Display the company name with label
            logo_url = f"https://ttok.s3.us-west-2.amazonaws.com/{stock_symbol}.svg"
            st.markdown(f"<div style='text-align:center;'><img src='{logo_url}' style='border-radius:10px; width:100px; height:100px;'/></div>", unsafe_allow_html=True)
            # Display the current spst value with label
            st.markdown("<p style='font-size:12px;'>Company Name</p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='font-weight:bold'>{company_name}</h1>", unsafe_allow_html=True)

        with col2:
            # Display the current spst value with label
            st.markdown("<p style='font-size:12px;'>Sales Per Share</p>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='font-weight:bold'>{spst_value}</h1>", unsafe_allow_html=True)
         
# Button to refresh data
if st.button('Refresh Data'):
    logging.info("Refresh Data button clicked.")
    try:
        # Modify the query to fetch data for the selected stock symbol and selected 'spst' values
        if selected_spst_values:
            query = f"SELECT dt_st, p FROM fact WHERE sym = '{stock_symbol}' AND spst IN ({', '.join([f'\'{v}\'' for v in selected_spst_values])})"
        else:
            query = f"SELECT dt_st, p FROM fact WHERE sym = '{stock_symbol}'"
        
        logging.info(f"Executing query: {query}")

        # Fetch data into a DataFrame
        response_fact = supabase.table('fact').select('dt_st, p').eq('sym', stock_symbol).execute()

        # Check if there's data in the response
        if response_fact.data is None:
            st.error("Failed to fetch data from Supabase.")
            logging.error(f"Error in response_fact: {response_fact}")
        else:
            # Convert response data to DataFrame
            st.session_state['df'] = pd.DataFrame(response_fact.data)
            logging.info("Data fetched successfully.")

            if st.session_state['df'].empty:
                st.write("No data available for the selected stock symbol and SPST values.")
                logging.warning("No data available for the selected stock symbol and SPST values.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")

# Check if DataFrame has data
if not st.session_state['df'].empty:
    # Calculate min and max values for 'p' column
    min_p = st.session_state['df']['p'].min()
    max_p = st.session_state['df']['p'].max()

    # Base Altair area chart
    chart = alt.Chart(st.session_state['df']).mark_area().encode(
        x='dt_st:T',
        y='p:Q',
        tooltip=['dt_st:T', 'p:Q']
    ).properties(
        title=f"{stock_symbol} Stock Prices",
        height=500
    )

    # Add horizontal reference lines for min and max
    min_line = alt.Chart(pd.DataFrame({'p': [min_p], 'label': [f'Min: {min_p:.2f}']})).mark_rule(
        color='blue', strokeWidth=2
    ).encode(
        y='p:Q'
    )

    max_line = alt.Chart(pd.DataFrame({'p': [max_p], 'label': [f'Max: {max_p:.2f}']})).mark_rule(
        color='red', strokeWidth=2
    ).encode(
        y='p:Q'
    )

    # Add text labels for min and max lines
    min_text = alt.Chart(pd.DataFrame({'p': [min_p], 'label': [f'Min: {min_p:.2f}']})).mark_text(
        align='left', baseline='middle', dx=5, dy=-10, color='white' 
    ).encode(
        y='p:Q',
        text='label:N'
    )

    max_text = alt.Chart(pd.DataFrame({'p': [max_p], 'label': [f'Max: {max_p:.2f}']})).mark_text(
        align='left', baseline='middle', dx=5, dy=10, color='white' 
    ).encode(
        y='p:Q',
        text='label:N'
    )

    # Layer the base chart, reference lines, and text labels
    final_chart = chart + min_line + max_line + min_text + max_text

    # Display the final chart
    st.altair_chart(final_chart, use_container_width=True)
else:
    logging.info("DataFrame is empty, no chart to display.")