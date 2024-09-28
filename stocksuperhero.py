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
        response = supabase.table('app_keys').select('key, login_timestamps').eq('key', user_key).execute()
        if response.data:
            st.session_state['authenticated'] = True
            st.success("Access Granted!")
            current_timestamp = datetime.now().isoformat()
            timestamps = response.data[0].get('login_timestamps', [])
            timestamps.append(current_timestamp)
            supabase.table('app_keys').update({'login_timestamps': timestamps}).eq('key', user_key).execute()
        else:
            st.error("Invalid access key. The app is protected.")
else:
    st.title("Welcome Superhero")

if st.session_state['authenticated']:
    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

    response_dim = supabase.table('dim').select('sym, spst, cn, ind, sec, ps').execute()
    
    if response_dim.data is None:
        st.error("Failed to fetch data from Supabase.")
    else:
        df_dim = pd.DataFrame(response_dim.data)
   
    selected_stock_symbol = 'SBUX'
    filtered_df = pd.DataFrame()

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

        filtered_df = filter_dataframe(df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec'])

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
                #MAIN APP AREA - FACT AND DIM
                # Price
                plot_area_chart(df_fact, selected_stock_symbol)

                #Bar Chart
                fig_bar = plot_bar_chart(filtered_df, selected_stock_symbol)
                if fig_bar:
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.write("No data available to display in the bar chart.")

                #Metric
                plot_metric(df_fact, selected_stock_symbol)

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