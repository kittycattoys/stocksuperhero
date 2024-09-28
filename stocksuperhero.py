import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from datetime import datetime
from st_aggrid import AgGrid
from functions.agstyler import PINLEFT, PRECISION_TWO, draw_grid
from functions.gauge import create_pie_chart
from functions.area import plot_area_chart
from functions.bar import plot_bar_chart
from functions.metric import plot_metric
from functions.tradingview import show_single_stock_widget, show_ticker_tape
import yfinance as yf
import streamlit.components.v1 as components

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide")

# Supabase connection details
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Check if user is authenticated
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("Access Protected Application")
    with st.form("access_form"):
        user_key = st.text_input("Enter your app secret access key", type="password")
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        response = supabase.table('app_keys').select('key, login_timestamps, watchlist').eq('key', user_key).execute()
        if response.data:
            st.session_state['authenticated'] = True
            st.success("Access Granted!")
            current_timestamp = datetime.now().isoformat()
            timestamps = response.data[0].get('login_timestamps', [])
            timestamps.append(current_timestamp)
            supabase.table('app_keys').update({'login_timestamps': timestamps}).eq('key', user_key).execute()

            # Store user_key and watchlist in session_state
            st.session_state['user_key'] = user_key
            st.session_state['watchlist'] = response.data[0].get('watchlist', [])
        else:
            st.error("Invalid access key. The app is protected.")
else:
    st.title("Welcome Superhero")

# Function to reapply watchlist filter
def apply_watchlist_filter():
    if watchlist:
        watchlist_symbols = [item['symbol'] for item in watchlist]
        return df_dim[df_dim['sym'].isin(watchlist_symbols)]
    else:
        return pd.DataFrame()  # Blank dataframe if watchlist is empty

if st.session_state['authenticated']:
    user_key = st.session_state.get('user_key')

    # Ensure the watchlist is loaded in session state
    watchlist = st.session_state.get('watchlist', [])
    print(watchlist)

   # Check if 'df_dim' is loaded and populated
    if 'df_dim' not in st.session_state:
        response_dim = supabase.table('dim').select('sym, spst, cn, ind, sec, ps, ex').execute()
        if response_dim.data is None:
            st.error("Failed to fetch data from Supabase.")
        else:
            st.session_state['df_dim'] = pd.DataFrame(response_dim.data)

    df_dim = st.session_state['df_dim']

    # Filter the dataframe by the watchlist initially on login
    filtered_df = apply_watchlist_filter()


    selected_stock_symbol = 'SBUX'

    def filter_dataframe(df, selected_spst, selected_ind, selected_sec):
        if selected_spst:
            df = df[df['spst'].isin(selected_spst)]
        if selected_ind:
            df = df[df['ind'].isin(selected_ind)]
        if selected_sec:
            df = df[df['sec'].isin(selected_sec)]
        return df

    def update_dropdowns(df, selected_spst, selected_ind, selected_sec):
        available_spst = df['spst'].unique().tolist()
        available_sec = df['sec'].unique().tolist()

        if selected_sec:
            filtered_df = df[df['sec'].isin(selected_sec)]
            available_ind = filtered_df['ind'].unique().tolist()
        else:
            available_ind = df['ind'].unique().tolist()

        return available_spst, available_ind, available_sec, df

    if 'selected_spst' not in st.session_state:
        st.session_state['selected_spst'] = []
    if 'selected_ind' not in st.session_state:
        st.session_state['selected_ind'] = []
    if 'selected_sec' not in st.session_state:
        st.session_state['selected_sec'] = []

    available_spst, available_ind, available_sec, filtered_df = update_dropdowns(
        df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec']
    )

    # Create an expander for dropdowns and table
    with st.expander("Filter Options and Data Table", expanded=True):
        col1, col2, col3 = st.columns(3)

        # Filtering options
        with col1:
            st.session_state['selected_sec'] = st.multiselect(
                "Select Sector", available_sec, default=st.session_state['selected_sec'], key="sector_multiselect"
            )
        
        with col2:
            st.session_state['selected_ind'] = st.multiselect(
                "Select Industry", available_ind, default=st.session_state['selected_ind'], key="industry_multiselect"
            )
        
        with col3:
            st.session_state['selected_spst'] = st.multiselect(
                "Select SPST Values", available_spst, default=st.session_state['selected_spst'], key="spst_multiselect"
            )

        # Button to clear all filters and reapply the watchlist
        if st.button("Clear All Filters and Reapply Watchlist"):
            # Clear the dropdown filters
            st.session_state['selected_sec'] = []
            st.session_state['selected_ind'] = []
            st.session_state['selected_spst'] = []
            # Reapply the watchlist filter
            filtered_df = apply_watchlist_filter()    

        # Only filter if dropdowns are updated; don't overwrite watchlist
        if st.session_state['selected_spst'] or st.session_state['selected_ind'] or st.session_state['selected_sec']:
            filtered_df = filter_dataframe(df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec'])
        else:
            # If no filters are selected, keep showing the watchlist only
            filtered_df = apply_watchlist_filter()

        if not filtered_df.empty:
            filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']
            df = filtered_df
            formatter = {
                'sym': ('Symbol', PINLEFT),
                'ind': ('Industry', {'width': 140}),
                'ps': ('P/S', {**PRECISION_TWO, 'width': 80}),
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
        response_fact = supabase.table('fact').select('dt_st, p, high_tp, mid_tp, low_tp').eq('sym', selected_stock_symbol).execute()
        if response_fact.data:
            df_fact = pd.DataFrame(response_fact.data)
            if not df_fact.empty:
                # MAIN APP AREA - FACT AND DIM
                #TradingView Widgets
                # Safely fetch stock prices and exchange symbol
                if not filtered_df.empty and selected_stock_symbol in filtered_df['sym'].values:
                    selected_exchange = filtered_df[filtered_df['sym'] == selected_stock_symbol]['ex'].values
                    if len(selected_exchange) > 0:
                        formatted_symbol = f"{selected_exchange[0]}:{selected_stock_symbol}"
                        print(formatted_symbol)
                        show_single_stock_widget(formatted_symbol)
                    else:
                        st.warning("Exchange information is missing for the selected stock symbol.")
                else:
                    st.warning(f"Stock symbol {selected_stock_symbol} not found in the filtered data.")

                # Bar Chart
                fig_bar = plot_bar_chart(filtered_df, selected_stock_symbol)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.write("No data available to display in the bar chart.")

                # Metric
                plot_metric(df_fact, selected_stock_symbol)

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

    #GAUGES FROM DIM NOT FACT
    st.markdown(
        """
        <style>
        /* Add your CSS styles here */
        .element-container {
            display: flex;
            justify-content: center;
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
        fig1 = create_pie_chart()
        st.plotly_chart(fig1, use_container_width=False, config={'displayModeBar': False})
        st.write("</div>", unsafe_allow_html=True)

    with col2:
        st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
        fig2 = create_pie_chart()
        st.plotly_chart(fig2, use_container_width=False, config={'displayModeBar': False})
        st.write("</div>", unsafe_allow_html=True)

    # Second row of charts
    col3, col4 = st.columns(2)

    with col3:
        st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
        fig3 = create_pie_chart()
        st.plotly_chart(fig3, use_container_width=False, config={'displayModeBar': False})
        st.write("</div>", unsafe_allow_html=True)

    with col4:
        st.write("<div style='text-align: center;'>", unsafe_allow_html=True)
        fig4 = create_pie_chart()
        st.plotly_chart(fig4, use_container_width=False, config={'displayModeBar': False})
        st.write("</div>", unsafe_allow_html=True)