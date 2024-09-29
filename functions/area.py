import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def plot_area_chart(df_fact, selected_stock_symbol):
    if not df_fact.empty:
        # Ensure 'dt_st' is a datetime object for proper plotting
        df_fact['dt_st'] = pd.to_datetime(df_fact['dt_st'])

        fig = go.Figure()

        # Add the area chart for stock prices
        fig.add_trace(go.Scatter(
            x=df_fact['dt_st'], 
            y=df_fact['p'],
            fill='tozeroy', 
            mode='lines', 
            name=f"{selected_stock_symbol} Stock Prices",
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y}<extra></extra>',
            text=df_fact['p'],  # Add data labels
            textposition="top center"
        ))

        # Add the line charts for high_tp, mid_tp, low_tp
        fig.add_trace(go.Scatter(
            x=df_fact['dt_st'], 
            y=df_fact['high_tp'],
            mode='lines', 
            line=dict(color='red', width=2),
            name='High TP',
            hovertemplate='<b>Date:</b> %{x}<br><b>High TP:</b> %{y}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=df_fact['dt_st'], 
            y=df_fact['mid_tp'],
            mode='lines', 
            line=dict(color='white', width=2),
            name='Mid TP',
            hovertemplate='<b>Date:</b> %{x}<br><b>Mid TP:</b> %{y}<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=df_fact['dt_st'], 
            y=df_fact['low_tp'],
            mode='lines', 
            line=dict(color='green', width=2),
            name='Low TP',
            hovertemplate='<b>Date:</b> %{x}<br><b>Low TP:</b> %{y}<extra></extra>'
        ))

        # Add rectangles for reference areas
        df_rectangles = pd.DataFrame({
            'start_date': [pd.Timestamp("2023-05-19"), pd.Timestamp("2023-01-15")], 
            'end_date': [pd.Timestamp("2023-05-22"), pd.Timestamp("2023-01-18")], 
            'color': ['green', 'red'], 
            'label': ['Reference Area 1', 'Reference Area 2']
        })

        # Loop through the dataframe to dynamically add vertical rectangles
        for index, row in df_rectangles.iterrows():
            fig.add_vrect(
                x0=row['start_date'], 
                x1=row['end_date'],
                fillcolor=row['color'], 
                opacity=0.2,
                layer="below", 
                line_width=0,
                annotation_text=row['label'], 
                annotation_position="top left"
            )

        # Customize layout
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False, 
            margin=dict(l=0, r=0, t=30, b=0),
            height=500,
            hovermode='x',
            dragmode=False,
            yaxis={
                'showspikes': True, 
                'spikemode': 'across', 
                'spikecolor': 'red', 
                'spikethickness': 1,
                'ticklabelposition': 'inside',
                'automargin': True, 
            },
            xaxis={
                'showspikes': True, 
                'spikemode': 'across', 
                'spikecolor': 'red', 
                'spikethickness': 1,
                'tickmode': 'linear',
                'tickfont': {'size': 10, 'color': 'grey'},
                'dtick': 'M1',  # Adjust to show monthly ticks
                'range': [df_fact['dt_st'].min(), df_fact['dt_st'].max()],  # Set x-axis range
            },
            modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"]),
        )

        st.plotly_chart(fig)
    else:
        st.warning(f"No stock price data found for {selected_stock_symbol}.")
