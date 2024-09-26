import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
import logging
from datetime import datetime

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    filtered_df = filter_dataframe(df_dim, st.session_state['selected_spst'], st.session_state['selected_ind'], st.session_state['selected_sec'])

    if not filtered_df.empty:
        filtered_df['sym_cn'] = filtered_df['sym'] + " - " + filtered_df['cn']

    with st.expander("Company Details", expanded=False):
        if not filtered_df.empty:
            filtered_df['logo_url'] = filtered_df['sym'].apply(lambda x: f"https://ttok.s3.us-west-2.amazonaws.com/{x}.svg")
            filtered_display = filtered_df[['logo_url', 'cn', 'sym', 'spst', 'ind', 'sec']]
            filtered_display.columns = ['Logo', 'Company Name', 'Symbol', 'SPST', 'Industry', 'Sector']
            def display_image(url):
                return f'<img src="{url}" style="border-radius:10px; width:50px; height:50px;" />'
            st.write(filtered_display.to_html(escape=False, formatters={'Logo': display_image}), unsafe_allow_html=True)
        else:
            st.write("No data available for the selected filters.")

    selected_stock_symbol = st.selectbox(
        "Select Stock Symbol (Searchable)", 
        filtered_df['sym_cn'] if not filtered_df.empty else []
    )

    if st.button("Fetch Stock Prices"):
        if selected_stock_symbol:
            stock_symbol = filtered_df.loc[filtered_df['sym_cn'] == selected_stock_symbol, 'sym'].values[0]
            response_fact = supabase.table('fact').select('dt_st, p').eq('sym', stock_symbol).execute()
            if response_fact.data:
                df_fact = pd.DataFrame(response_fact.data)
                if not df_fact.empty:
                    # Plotting stock prices using Plotly
                    fig = go.Figure()

                    # Add the area chart
                    fig.add_trace(go.Scatter(
                        x=df_fact['dt_st'], y=df_fact['p'],
                        fill='tozeroy', mode='lines', name=f"{stock_symbol} Stock Prices",
                        hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y}<extra></extra>',
                        text=df_fact['p'],  # Add data labels
                        textposition="top center"
                    ))

                    df_rectangles = pd.DataFrame({
                        'start_date': ["May-31-2019", "Jan-31-2015"], 
                        'end_date': ["May-31-2022", "Jan-31-2018"], 
                        'color': ['green', 'red'], 
                        'label': ['Reference Area 1', 'Reference Area 2']
                    })

                    # Loop through the dataframe to dynamically add vrects
                    for index, row in df_rectangles.iterrows():
                        fig.add_vrect(
                            x0=row['start_date'], x1=row['end_date'],
                            fillcolor=row['color'], opacity=0.2,
                            layer="below", line_width=0,
                            annotation_text=row['label'], annotation_position="top left"
                        )

                    # Customize layout
                    fig.update_layout(
                        title=f"{stock_symbol} Stock Prices",
                        xaxis_title=None,
                        yaxis_title=None,
                        showlegend=False,
                        margin=dict(l=20, r=20, t=40, b=20),
                        height=500,
                        hovermode='x',
                        dragmode=False,  # Disable drag mode
                        xaxis={'showspikes': True, 'spikemode': 'across', 'spikethickness': 2, 'spikedash': 'dash', 'spikecolor': 'orange'},
                        # Disable all modebar buttons (zoom, pan, etc.)
                        modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"])
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No data available for the selected stock symbol.")
            else:
                st.error("Failed to fetch data from Supabase.")
        else:
            st.error("Please select a stock symbol.")

    with st.expander("PS Metric Bar Chart", expanded=False):
        if not filtered_df.empty and 'sym' in filtered_df.columns and 'ps' in filtered_df.columns:
            fig_bar = go.Figure()

            # Add bar chart
            fig_bar.add_trace(go.Bar(
                x=filtered_df['sym'], y=filtered_df['ps'],
                marker_color='steelblue', name='PS Metric',
                text=filtered_df['ps'],  # Add data labels
                textposition='auto',
                hoverinfo='text+name',  # Display both text and name on hover
                hovertemplate='<b>Symbol:</b> %{x}<br><b>PS Metric:</b> %{y}<extra></extra>'  # Customize hovertemplate
            ))

            # Highlight selected symbol
            fig_bar.update_traces(
                marker=dict(color=['orange' if sym == selected_stock_symbol else 'steelblue' for sym in filtered_df['sym']])
            )

            # Customize layout
            fig_bar.update_layout(
                title="PS Metric Bar Chart",
                xaxis_title=None,
                yaxis_title="PS Metric",
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                height=500,
                hovermode='x',
                dragmode=False,  # Disable drag mode
                # Show a vertical line on hover similar to spike effect
                #xaxis=dict(showspikes=True, spikemode='across', spikethickness=2, spikedash='dash', spikecolor='orange'),
                #yaxis=dict(showspikes=False),  # We only want the x-axis spike
                modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"])
            )

            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No data available to display.")
