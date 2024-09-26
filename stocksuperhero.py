import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client
from datetime import datetime

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide")

#Define the background color and quadrant colors
plot_bgcolor = "rgba(255, 255, 255, 0)"
quadrant_colors = [plot_bgcolor, "#f25829", "#f2a529", "#85e043", "#2bad4e"]
quadrant_text = ["", "<b>Very high</b>", "<b>High</b>", "<b>Medium</b>", "<b>Low</b>", "<b>Very low</b>"]
n_quadrants = len(quadrant_colors) - 1

# Set the current value and limits
current_value = 19.0
min_value = 0
max_value = 50
hand_length = np.sqrt(2) / 4
hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

# Function to create the pie chart
def create_pie_chart(font_size_factor):
    # Adjust font sizes based on the factor
    annotation_font_size = int(24 * font_size_factor)
    quadrant_label_font_size = int(12 * font_size_factor)

    fig = go.Figure(
        data=[go.Pie(
            values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
            rotation=90,
            hole=0.5,
            marker_colors=quadrant_colors,
            text=quadrant_text,
            textinfo="text",
            hoverinfo="skip",
        )],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=60, l=0, r=0),
            width=900,  # Width set to 900 pixels for horizontal space
            height=450,  # Maintain the height
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>Price / Sales</b><br><b>{current_value}x</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                    font=dict(size=annotation_font_size)
                ),
                # Adding quadrant labels
                go.layout.Annotation(
                    text="<b>Very High</b>",
                    x=0.5, y=0.9, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#f25829"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text="<b>High</b>",
                    x=0.8, y=0.9, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#f2a529"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text="<b>Medium</b>",
                    x=0.9, y=0.4, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#eff229"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text="<b>Low</b>",
                    x=0.5, y=0.2, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#85e043"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text="<b>Very Low</b>",
                    x=0.1, y=0.2, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#2bad4e"),
                    showarrow=False
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                )
            ]
        )
    )
    
    return fig

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

                    # Add rectangles for reference areas
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
                        dragmode=False,
                        xaxis={'showspikes': True, 'spikemode': 'across', 'spikethickness': 2, 'spikedash': 'dash', 'spikecolor': 'orange'},
                        modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"])
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No data available for the selected stock symbol.")
            else:
                st.error("Failed to fetch data from Supabase.")
        else:
            st.error("Please select a stock symbol.")

    # Place the PS Metric Bar Chart in its own expander
    with st.expander("PS Metric Bar Chart", expanded=False):
        if not filtered_df.empty and 'sym' in filtered_df.columns and 'ps' in filtered_df.columns:
            fig_bar = go.Figure()

            # Add bar chart
            fig_bar.add_trace(go.Bar(
                x=filtered_df['sym'], y=filtered_df['ps'],
                marker_color='steelblue', name='PS Metric',
                text=filtered_df['ps'],  # Add data labels
                textposition='auto',
                hoverinfo='text+name',
                hovertemplate='<b>Symbol:</b> %{x}<br><b>PS Metric:</b> %{y}<extra></extra>'
            ))

            # Highlight selected symbol
            fig_bar.update_traces(
                marker=dict(color=['orange' if sym == selected_stock_symbol else 'steelblue' for sym in filtered_df['sym']])
            )

            # Customize layout
            fig_bar.update_layout(
                title="PS Metric Bar Chart",
                #xaxis_title="Stock Symbols",
                #yaxis_title="PS Value",
                margin=dict(l=0, r=0, t=20, b=0),
                height=500
            )

            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No data available to display in the bar chart.")

    # Place the Gauge Chart in a separate expander
    with st.expander("Stock Superhero", expanded=True):
        # Fixed factor for font size (you can adjust it if needed)
        font_size_factor = 1.2  # Adjust this factor to scale font sizes
        # Create and display the pie chart
        fig = create_pie_chart(font_size_factor)
        st.plotly_chart(fig, use_container_width=True)
        