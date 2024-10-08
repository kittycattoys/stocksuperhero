import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client
from datetime import datetime
from functools import partial
import plotly.graph_objects as go
from st_aggrid import AgGrid
from functions.agstyler import PINLEFT, PRECISION_TWO, draw_grid, highlight
from functions.gauge import create_pie_chart
from functions.area import plot_area_chart
from functions.bar import plot_bar_chart
from functions.metric import plot_metric
from functions.tradingview import show_single_stock_widget, show_ticker_tape
from functions.macd import plot_macd_chart
import yfinance as yf
import streamlit.components.v1 as components
from time import sleep

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide")

# Supabase connection details
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)
selected_stock_symbol = 'SBUX'

# Function to switch tables based on time period selection
def get_fact_table_for_period(period):
    if period == "Daily":
        return 'fact_daily'
    elif period == "Weekly":
        return 'fact'
    else:
        return 'fact_monthly'

def login_user(user_key):
    response = supabase.table('app_keys').select('watchlist').eq('key', user_key).execute()
    print('login response')
    print(response)
    print(response.data)
    if response.data:
        st.toast('Your login was successful!', icon='🔓')
        st.session_state['authenticated'] = True
        current_timestamp = datetime.now().isoformat()
        timestamps = response.data[0].get('login_timestamps', [])
        timestamps.append(current_timestamp)
        supabase.table('app_keys').update({'login_timestamps': timestamps}).eq('key', user_key).execute()
        st.session_state['user_key'] = user_key
        st.session_state['watchlist'] = response.data[0].get('watchlist', [])
        st.rerun()  # Force rerun to apply login
    else:
        st.error("Invalid access key.")

# Function to filter dataframe
def filter_dataframe(df, selected_pst, selected_ind, selected_sec):
    if selected_pst:
        df = df[df['pst'].isin(selected_pst)]
    if selected_ind:
        df = df[df['ind'].isin(selected_ind)]
    if selected_sec:
        df = df[df['sec'].isin(selected_sec)]
    return df

def update_dropdowns(df, selected_sec):
    available_sec = df['sec'].unique().tolist()

    # Update industries based on selected sectors
    if selected_sec:
        available_ind = df[df['sec'].isin(selected_sec)]['ind'].unique().tolist()
    else:
        available_ind = df['ind'].unique().tolist()

    available_pst = df['pst'].unique().tolist()
    return available_pst, available_ind, available_sec

def on_pst_change(arg):
    st.toast(f"First Toast: {arg}")
    if arg == "sec":
        st.toast(f"Confirmed Sec? {arg}")
    elif arg == "ind":
        st.toast(f"Confirmed Ind? {arg}")
    else: 
        st.toast(f"Confirmed Other? {arg}")

# Authentication check
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    with st.expander("Login", expanded=True):
        with st.form("access_form"):
            user_key_input = st.text_input("Enter Access Key", type="password")
            submit_button = st.form_submit_button("Verify Access Key Now")
        if submit_button and user_key_input:
            login_user(user_key_input)
else:
    user_key = st.session_state.get('user_key')
    # Ensure the watchlist is loaded in session state
    watchlist = st.session_state.get('watchlist', [])
    
    # Ensure 'df_dim' is loaded
    if 'df_dim' not in st.session_state:
        response_dim = supabase.table('dim').select('sym, cn, ind, sec, ps, pst, dy, dyt, pe, pet, ex').execute()
        st.session_state['df_dim'] = pd.DataFrame(response_dim.data)
    
    df_dim = st.session_state['df_dim']

    # Initialize session state for filters
    if 'selected_sec' not in st.session_state:
        st.session_state['selected_sec'] = []
    if 'selected_ind' not in st.session_state:
        st.session_state['selected_ind'] = []
    if 'selected_pst' not in st.session_state:
        st.session_state['selected_pst'] = []

    # Get updated dropdowns
    available_pst, available_ind, available_sec = update_dropdowns(df_dim, st.session_state['selected_sec'])

    # Filter options inside an expander
    with st.expander("Filter Options", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state['selected_sec'] = st.multiselect(
                "Select Sector", 
                available_sec, 
                #default=st.session_state['selected_sec'], 
                key="sector_multiselect",
                on_change=partial(on_pst_change, "sec")
            )
            if st.session_state['selected_sec']:
                st.success(f"Selected Sectors: {', '.join(st.session_state['selected_sec'])}")
            else:
                st.error("No Sector selected")

        with col2:
            if st.session_state['selected_sec']:
                available_ind = df_dim[df_dim['sec'].isin(st.session_state['selected_sec'])]['ind'].unique().tolist()
            st.session_state['selected_ind'] = st.multiselect(
                "Select Industry", 
                available_ind, 
                #default=st.session_state['selected_ind'], 
                key="industry_multiselect",
                on_change=partial(on_pst_change, "ind")
            )
            if st.session_state['selected_ind']:
                st.success(f"Selected Industries: {', '.join(st.session_state['selected_ind'])}")
            else:
                st.error("No Industry selected")

        with col3:
            st.session_state['selected_pst'] = st.multiselect(
                "Select PST Values", 
                available_pst, 
                #default=st.session_state.get('selected_pst', []),  # Ensure default is not None
                key="pst_multiselect",
                on_change=partial(on_pst_change, "ps")
            )
            if st.session_state['selected_pst']:
                st.success(f"Selected PST Values: {', '.join(st.session_state['selected_pst'])}")
            else:
                st.error("No PST Values selected")

        # Filter dataframe based on selections
        filtered_df = filter_dataframe(df_dim, st.session_state['selected_pst'], st.session_state['selected_ind'], st.session_state['selected_sec'])

        # Button to clear filters
        if st.button("Clear All Filters"):
            st.session_state['selected_sec'] = []
            st.session_state['selected_ind'] = []
            st.session_state['selected_pst'] = []
            st.rerun()

        # Add the radio button for time period selection
        time_period = st.radio("Select Time Period", options=["Daily", "Weekly", "Monthly"], index=2)
        fact_table = get_fact_table_for_period(time_period)  

    if not filtered_df.empty:
        #first df test
        #st.dataframe(filtered_df)

        #Main DF TEST
        filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']
        df = filtered_df
        values_with_colors = {
            "Expensive": ("#f25829", "black"),
            "High": ("#f2a529", "black"),
            "Low": ("#85e043", "black"),
            "Cheap": ("#2bad4e", "black")
        }
        highlight_function = highlight(values_with_colors)  
        formatter = {
            'sym': ('Symbol', PINLEFT),
            'ind': ('Industry', {'width': 140}),
            'ps': ('P/S', {**PRECISION_TWO, 'width': 80}),
            'pst': ('PS Type', {
                'cellStyle': highlight_function  # Apply the highlight function here
                }),
            'pe': ('P/E', {**PRECISION_TWO, 'width': 80}),
            'pet': ('PE Type', {
                'cellStyle': highlight_function  # Apply the highlight function here
                }),
            }

        # Draw the grid with single selection and use checkbox as a boolean
        data = draw_grid(
            df.head(100),
            formatter=formatter,
            fit_columns=True,
            selection='single',  # Use 'single' or 'multiple' as required
            use_checkbox=True,  # Use checkbox as a boolean
            max_height=300,
        )

        # Safely check if selected_rows exists and is not empty
        selected_rows = getattr(data, 'selected_rows', None)

        # Check if selected_rows is not None and is a list
        if selected_rows is not None and isinstance(selected_rows, list) and len(selected_rows) > 0:
            # Process selected rows
            for selected_row in selected_rows:
                if isinstance(selected_row, dict):
                    selected_stock_symbol = selected_row.get('sym', 'N/A')

        # This block is now outside the expander
    if selected_stock_symbol:
        # Fetch stock prices based on selected stock symbol
        response_dim_det = supabase.table('dim_det').select('sym, pst, cn, ind, sec, ps, sps, psmin, ps2, ps5, ps8, psmax, psn, pst, pe, eps, pemin, pe2, pe5, pe8, pemax, pen, pet, dy, d, dymin, dy2, dy5, dy8, dymax, dyn, dyt, ex, trend_json_ss').eq('sym', selected_stock_symbol).execute()
        response_fact = supabase.table(fact_table).select('sym, dt_st, p, high_tp, mid_tp, low_tp, ps, sps, pe, eps, dy, d').eq('sym', selected_stock_symbol).execute()
        response_tech = supabase.table('stocksuperhero_tech_monthly').select('sym, dt_st, p, rsi, md, mds, mdh').eq('sym', selected_stock_symbol).execute()
        if response_fact.data:
            df_fact = pd.DataFrame(response_fact.data)
            df_dim_det = pd.DataFrame(response_dim_det.data)
            df_tech = pd.DataFrame(response_tech.data)
            if not df_fact.empty:
                # Extract the first row's 'trend_json_ss' data (if there's only one row per stock symbol)
                json_data = df_dim_det.loc[0, 'trend_json_ss']

                # Step 3: Convert the extracted JSON data into a dataframe
                df_text_labels = pd.json_normalize(json_data)

                # Step 4: Display the resulting df_text_labels
                print(df_text_labels)

                # MAIN APP AREA - FACT AND DIM
                st.markdown("""
                    <style>
                    .col1 {
                        max-width: 150px !important;
                        padding: 0px !important;
                        margin: 0px !important;
                    }
                    .col2 {
                        padding: 0px !important;
                        margin: 0px !important;
                    }
                    .col3 {
                        padding: 0px !important;
                        margin: 0px !important;
                    }
                    .rounded-image {
                        border-radius: 15px;  /* Adjust the radius as needed */
                    }
                    </style>
                    """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 3, 3], gap="small")  # Adjust ratio for the layout

                with col1:
                    # Display the company logo (left-aligned with a fixed width)
                    image_url = f"https://ttok.s3.us-west-2.amazonaws.com/{selected_stock_symbol}.svg"
                    st.markdown(f'<img src="{image_url}" width="120" class="rounded-image" alt="{selected_stock_symbol}">', unsafe_allow_html=True)

                with col2:
                    # Display the sector and industry (aligned with the company name and symbol)
                    st.subheader(f"{df_dim_det['cn'].iloc[0]} - {selected_stock_symbol}")
                    # Display the company name and symbol
                    st.markdown(f"{df_dim_det['sec'].iloc[0]} - {df_dim_det['ind'].iloc[0]}")
                    # Apply the custom class to col2 for styling
                    st.markdown('<div class="col2"></div>', unsafe_allow_html=True)

                with col3:
                    # Real-time price widget
                    if not filtered_df.empty and selected_stock_symbol in filtered_df['sym'].values:
                        selected_exchange = filtered_df[filtered_df['sym'] == selected_stock_symbol]['ex'].values
                        if len(selected_exchange) > 0:
                            formatted_symbol = f"{selected_exchange[0]}:{selected_stock_symbol}"
                            #print(formatted_symbol)
                            show_single_stock_widget(formatted_symbol)
                        else:
                            st.warning("Exchange information is missing for the selected stock symbol.")
                    else:
                        st.warning(f"Stock symbol {selected_stock_symbol} not found in the filtered data.")        

                plot_area_chart(df_fact, selected_stock_symbol, df_text_labels, metric_type='p', metric_color='dodgerblue')

                
                plot_macd_chart(df_tech)
                
                # Bar Chart
                fig_bar = plot_bar_chart(filtered_df, selected_stock_symbol)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.write("No data available to display in the bar chart.")

                # Metric
                df_text_labels['dt_st'] = pd.to_datetime(df_text_labels['dt_st']).dt.strftime("%b %y").astype(str)
                plot_metric(df_fact, selected_stock_symbol, df_text_labels, metric_type='ps', metric_color='hotpink')
                plot_metric(df_fact, selected_stock_symbol, df_text_labels, metric_type='pe', metric_color='orange')
                plot_metric(df_fact, selected_stock_symbol, df_text_labels, metric_type='dy', metric_color='purple')

                #GAUGES FROM DIM NOT FACT
                st.markdown(
                    """
                    <style>
                    /* Add your CSS styles here */
                    .element-container {
                        display: flex;
                        justify-content: center;
                        margin: 0px !important;
                        padding: 0px !important;
                    }
                    </style>
                    """, 
                    unsafe_allow_html=True
                )

                # Layout for charts
                col1, col2 = st.columns(2)

                # First row of charts
                with col1:
                    st.write("<div style='text-align: center; margin-bottom: 0;'>", unsafe_allow_html=True)
                    fig1 = create_pie_chart(df_dim_det, metric_type='ps', metric_color='hotpink')
                    st.plotly_chart(fig1, use_container_width=False, config={'displayModeBar': False}, key="chart1")
                    st.write("</div>", unsafe_allow_html=True)

                with col2:
                    st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
                    fig2 = create_pie_chart(df_dim_det, metric_type='pe', metric_color='hotpink')
                    st.plotly_chart(fig2, use_container_width=False, config={'displayModeBar': False}, key="chart2")
                    st.write("</div>", unsafe_allow_html=True)

                # Second row of charts
                col3, col4 = st.columns(2)

                with col3:
                    st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
                    fig3 = create_pie_chart(df_dim_det, metric_type='dy', metric_color='hotpink')
                    st.plotly_chart(fig3, use_container_width=False, config={'displayModeBar': False}, key="chart3")
                    st.write("</div>", unsafe_allow_html=True)

                with col4:
                    st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
                    fig4 = create_pie_chart(df_dim_det, metric_type='ps', metric_color='hotpink')
                    st.plotly_chart(fig4, use_container_width=False, config={'displayModeBar': False}, key="chart4")
                    st.write("</div>", unsafe_allow_html=True)

                # Add Watchlist Functionality
                watchlist = st.session_state.get('watchlist', [])
                
                # Check if the selected stock symbol is already in the watchlist
                if any(item['symbol'] == selected_stock_symbol for item in watchlist):
                    st.warning(f"{selected_stock_symbol} is already in your watchlist.")
                elif len(watchlist) < 5:
                    if st.button("Add to Watchlist"):
                        # Fetch price from Yahoo Finance
                        stock_data = yf.Ticker(selected_stock_symbol)
                        price = stock_data.history(period='1d')['Close'].iloc[-1]
                        timestamp = datetime.now().isoformat()
    
                        # Add the stock to the watchlist
                        watchlist.append({
                            'symbol': selected_stock_symbol,
                            'timestamp': timestamp,
                            'price': price
                        })
    
                        # Update watchlist in Supabase
                        supabase.table('app_keys').update({'watchlist': watchlist}).eq('key', st.session_state['user_key']).execute()
                        st.session_state['watchlist'] = watchlist
                        st.success(f"{selected_stock_symbol} added to watchlist.")
                else:
                    st.warning("Watchlist is full. Please remove an existing stock to add a new one.")

                # Ticker Tape
                st.subheader("Watchlist Ticker Tape")
                if watchlist:
                    show_ticker_tape()
                else:
                    st.write("Your watchlist is empty.")
    
                # Display Watchlist
                st.subheader("Your Watchlist")
                for idx, item in enumerate(watchlist):
                    st.write(f"{item['symbol']} - Added on {item['timestamp']} at ${item['price']:.2f}")
                    
                    # Assign a unique key to each remove button using the stock symbol
                    if st.button(f"Remove {item['symbol']} from Watchlist", key=f"remove_{item['symbol']}"):
                        watchlist.remove(item)
                        supabase.table('app_keys').update({'watchlist': watchlist}).eq('key', st.session_state['user_key']).execute()
                        st.session_state['watchlist'] = watchlist
                        st.rerun()  # Rerun to update the display

            else:
                st.warning(f"No stock price data found for {selected_stock_symbol}.")
        else:
            st.error(f"Failed to fetch data for {selected_stock_symbol}.")

    else:
        st.warning("No data matches the selected filters.")