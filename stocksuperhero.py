import streamlit as st
import pandas as pd
import altair as alt
from supabase import create_client, Client
import logging

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase connection details
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Check if user is already authenticated
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Display the access form only if not authenticated
if not st.session_state['authenticated']:
    st.title("Access Protected Application")
    with st.form("access_form"):
        user_key = st.text_input("Enter your app secret access key", type="password")
        submit_button = st.form_submit_button("Submit")

    # Load the valid keys from secrets
    valid_keys = list(st.secrets["app_access_keys"].values())

    # Check if the user key matches any of the valid keys
    if submit_button:
        if user_key in valid_keys:
            st.session_state['authenticated'] = True  # Set the flag to indicate authentication success
            st.success("Access Granted!")
        else:
            st.error("Invalid access key. The app is protected.")
else:
    st.title("Welcome Superhero")

# Only show the main app if authenticated
if st.session_state['authenticated']:
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
        available_spst = df['spst'].unique().tolist()
        available_sec = df['sec'].unique().tolist()  # Keep all sectors available

        if selected_sec:
            filtered_df = df[df['sec'].isin(selected_sec)]
            available_ind = filtered_df['ind'].unique().tolist()
        else:
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
    with st.expander("Filter", expanded=False):
        st.session_state['selected_sec'] = st.multiselect(
            "Select Sector", available_sec, default=st.session_state['selected_sec'], key="sector_multiselect"
        )

        available_spst, available_ind, available_sec, filtered_df = update_dropdowns(
            df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec']
        )

        st.session_state['selected_ind'] = st.multiselect(
            "Select Industry", available_ind, default=st.session_state['selected_ind'], key="industry_multiselect"
        )
        
        st.session_state['selected_spst'] = st.multiselect(
            "Select SPST Values", available_spst, default=st.session_state['selected_spst'], key="spst_multiselect"
        )

    # Cross-filter the DataFrame based on the updated selections
    filtered_df = filter_dataframe(df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec'])

    # Create a column for sym_cn for the dropdown
    filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']

    # Display the DataFrame with logos, company names, symbols, SPST, industry, and sector in an expander
    with st.expander("Company Details", expanded=False):
        if not filtered_df.empty:
            # Add a column for the logo URL
            filtered_df['logo_url'] = filtered_df['sym'].apply(lambda x: f"https://ttok.s3.us-west-2.amazonaws.com/{x}.svg")
            filtered_display = filtered_df[['logo_url', 'cn', 'sym', 'spst', 'ind', 'sec']]
            
            # Set custom column names
            filtered_display.columns = ['Logo', 'Company Name', 'Symbol', 'SPST', 'Industry', 'Sector']
            
            # Create a table with images in HTML
            def display_image(url):
                return f'<img src="{url}" style="border-radius:10px; width:50px; height:50px;" />'

            # Display the filtered DataFrame with logos
            st.write(filtered_display.to_html(escape=False, formatters={'Logo': display_image}), unsafe_allow_html=True)
        else:
            st.write("No data available for the selected filters.")

    # Stock symbol dropdown (sym + cn) remains outside the expander
    selected_stock_symbol = st.selectbox(
        "Select Stock Symbol (Searchable)", 
        filtered_df['sym_cn'] if not filtered_df.empty else []
    )

    # Add a button to fetch data from the fact table
    if st.button("Fetch Stock Prices"):
        if selected_stock_symbol:
            stock_symbol = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'sym'].values[0]
            
            # Query the fact table and display the chart based on the selected symbol
            response_fact = supabase.table('fact').select('dt_st, p').eq('sym', stock_symbol).execute()
            if response_fact.data:
                df_fact = pd.DataFrame(response_fact.data)
                if not df_fact.empty:
                    # Plotting stock prices using Altair
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
        else:
            st.warning("Please select a stock symbol to fetch data.")
