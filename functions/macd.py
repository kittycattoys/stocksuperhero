import plotly.graph_objects as go
import streamlit as st
import pandas as pd

# Assuming response_tech is already fetched and contains data
# df_tech = pd.DataFrame(response_tech.data)  # Your DataFrame

def plot_macd_chart(df_tech):
    # Create the figure
    fig = go.Figure()

    # Add the MACD line
    fig.add_trace(go.Scatter(
        x=df_tech['dt_st'], 
        y=df_tech['md'],
        mode='lines',
        line=dict(color='black', width=5),
        name="MACD Line"
    ))

    # Add the Signal line
    fig.add_trace(go.Scatter(
        x=df_tech['dt_st'], 
        y=df_tech['mds'],
        fill='tozeroy',  # Fill between the signal line and 0
        line=dict(color='#eeaf12', width=5),
        name="Signal Line"
    ))

    # Add the Histogram as bars
    fig.add_trace(go.Bar(
        x=df_tech['dt_st'], 
        y=df_tech['mdh'],
        marker_color='DeepSkyBlue',
        name="Histogram"
    ))

    # Customize layout similar to the previous settings
    fig.update_layout(
        plot_bgcolor='white',
        showlegend=False,  # Hide the legend
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
            'fixedrange': True,
            'zeroline': False,
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
            'dtick': 36,  # Adjust as needed for your data
            'range': [min(df_tech['dt_st']), max(df_tech['dt_st'])],
        },
        modebar=dict(
            remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"]
        )
    )

    # Update the chart's trace formatting
    #fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))

    # Display the chart in Streamlit with container width set to True
    st.plotly_chart(fig, use_container_width=True)

# Example usage within the Streamlit app:
# plot_macd_chart(df_tech)
