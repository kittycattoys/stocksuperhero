import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def plot_area_chart(df_fact, selected_stock_symbol, df_text_labels, metric_type, metric_color):
    if not df_fact.empty:
        # Plotting stock prices using Plotly
        df_fact['dt_st'] = pd.to_datetime(df_fact['dt_st']).dt.strftime("%b %y").astype(str)
        min_p = df_fact[metric_type].min()
        max_p = df_fact['high_tp'].max()
    
        # Adjust the y-axis range: scale down the minimum and adjust the maximum
        y_min = min_p * 0.9
        y_max = max_p * 1.05

        fig = go.Figure()

        # Add the area chart for stock prices
        fig.add_trace(go.Scatter(
            x=df_fact['dt_st'], 
            y=df_fact[metric_type],
            fill='tozeroy', 
            mode='lines', 
            name=f"{selected_stock_symbol} Stock Prices",
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y}<extra></extra>',
            #text=df_fact[metric_type],  # Add data labels
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

        # Customize layout
        fig.update_layout(
            #title=f"{selected_stock_symbol} Stock Prices",
            xaxis_title=None,
            yaxis_title=None,
            showlegend=False, 
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
            hovermode='x',
            dragmode=False,
            yaxis={
                'showspikes': True,    
                'spikemode': 'toaxis',
                'spikecolor': 'rgba(191, 191, 191, 1)',
                'spikethickness': 1,
                'spikedash': 'dash',
                'automargin': True, 
                'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
                'tickwidth': 1,
                'tickcolor': 'LightSteelBlue',
                'ticklen': 4,
                'ticklabelposition': 'inside top',
                #'ticksuffix': "%",
                #'tickprefix': "%",
                'fixedrange': True,  # Add this line
                'zeroline': False,
                #'range': [0, max(df_fact['p']) * 1.1],  # Add this line
                'range': [y_min, y_max],  # Set the dynamic y-axis range
            },
            xaxis={
                'zeroline': False,
                'showspikes': True,    
                'spikemode': 'toaxis',
                'spikecolor': 'rgba(191, 191, 191, 1)',
                'spikethickness': 1,
                'spikedash': 'dash',
                'tickmode': 'linear',
                'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
                'tickcolor': 'LightSteelBlue',
                'dtick': 36, 
                'tick0': False,
                'range': [min(df_fact['dt_st']), max(df_fact['dt_st'])],
            },
            modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"]),
        )

        st.plotly_chart(fig)
    else:
        st.warning(f"No stock price data found for {selected_stock_symbol}.")