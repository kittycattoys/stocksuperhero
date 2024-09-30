import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def plot_metric(df_fact, selected_stock_symbol):
    # Calculate min and max values for 'p' column
    min_p = df_fact['p'].min()
    max_p = df_fact['p'].max()
    
    #df_fact['dt_st'] = pd.to_datetime(df_fact['dt_st']).dt.strftime("%b %y")
    # Create a Plotly figure for the area chart
    fig = go.Figure()

    # Add the area chart for stock prices
    fig.add_trace(go.Scatter(
        x=df_fact['dt_st'], 
        y=df_fact['p'],
        fill='tozeroy',  # Fill to the horizontal axis
        mode='lines',
        line=dict(color='hotpink'),
        hoverinfo='x+y',
        name=f"{selected_stock_symbol} Prices"
    ))

    # Add a horizontal reference line for the min value
    fig.add_shape(type='line',
                  x0=df_fact['dt_st'].min(),
                  x1=df_fact['dt_st'].max(),
                  y0=min_p, y1=min_p,
                  line=dict(color='blue', width=2))

    # Add a horizontal reference line for the max value
    fig.add_shape(type='line',
                  x0=df_fact['dt_st'].min(),
                  x1=df_fact['dt_st'].max(),
                  y0=max_p, y1=max_p,
                  line=dict(color='red', width=2))
    
    # Calculate the middle index of the x-axis for positioning the annotations
    mid_index = len(df_fact) // 2
    mid_x = df_fact['dt_st'].iloc[mid_index]

    # Add text annotation for the min value
    fig.add_annotation(x=mid_x, y=min_p,
                       text=f"Min: {min_p:.2f}",
                       showarrow=False, xanchor='center', yanchor='bottom',
                       font=dict(color='white'))

    # Add text annotation for the max value
    fig.add_annotation(x=mid_x, y=max_p,
                       text=f"Max: {max_p:.2f}",
                       showarrow=False, xanchor='center', yanchor='top',
                       font=dict(color='white'))

    # Customize chart layout
    fig.update_layout(
        #title=f"{selected_stock_symbol} Stock Prices",
        height=400,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False, 
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode='x',
        dragmode=False,
        yaxis={ 
            'showspikes': True,             # Enable spikelines
            'spikemode': 'toaxis',          # Spike to axis
            'spikecolor': 'rgba(228, 233, 237, 0.4)',  # Red color with 0.4 opacity using rgba
            'spikethickness': 1,            # Spike line thickness
            'spikedash': 'solid',           # Type of spike line (can be 'solid', 'dot', 'dash')
            'automargin': True,             # Auto margins
            'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
            'tickwidth': 1,
            'tickcolor': 'LightSteelBlue',
            'ticklen': 4,
            'ticklabelposition': 'inside top',
            'fixedrange': True,             # Disable zoom on the y-axis
            'zeroline': False,              # Remove the zero line
            #'spikesnap': 'cursor',          # Make the spike snap to the cursor position
            #'spikebgcolor': 'rgba(0, 0, 0, 0)',  # Transparent background for the spikeline
        },
        xaxis={
            'zeroline': False,
            'showspikes': True, 
            'spikemode': 'toaxis', 
            'spikecolor': 'rgba(228, 233, 237, 0.4)',
            'spikedash': 'solid', 
            'spikethickness': 1,
            'tickmode': 'linear',
            'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
            'tickcolor': 'LightSteelBlue',
            'dtick': 36, 
            'tick0': False,
            'range': [min(df_fact['dt_st']), max(df_fact['dt_st'])],
        },
        modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"])
    )

    # Display the Plotly chart
    st.plotly_chart(fig, use_container_width=True)