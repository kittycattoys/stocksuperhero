import plotly.graph_objects as go
import streamlit as st
import pandas as pd

def plot_macd_chart(df_tech):
    # Create the figure
    figuree = go.Figure()

    # Add the MACD line
     # Add the MACD line
    figuree.add_trace(go.Scatter(
        x=df_tech['dt_st'], 
        y=df_tech['md'],
        #mode='lines',
        line=dict(color='white', width=2),
        #name="MACD Line"
    ))

    # Add the Signal line
    figuree.add_trace(go.Scatter(
        x=df_tech['dt_st'], 
        y=df_tech['mds'],
        fill='tozeroy',  # Fill between the signal line and 0
        line=dict(color='#eeaf12', width=2),
        #name="Signal Line"
    ))

    # Add the Histogram as bars
    figuree.add_trace(go.Bar(
        x=df_tech['dt_st'], 
        y=df_tech['mdh'],
        marker_color='DeepSkyBlue',
        name="Histogram"
    ))


    figuree.update_layout(
        showlegend=False,  # Hide the legend
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        modebar=dict(
            remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"]
        ),
        xaxis={
            #'zeroline': False,
            #'showspikes': True,    
            #'spikemode': 'toaxis',
            #'spikecolor': 'rgba(191, 191, 191, 1)',
            #'spikethickness': 1,
            #'spikedash': 'dash',
            #'tickmode': 'linear',
            'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
            #'tickcolor': 'LightSteelBlue',
            #'dtick': 36,  # Adjust as needed for your data
            #'range': [min(df_tech['dt_st']), max(df_tech['dt_st'])],
        },
        yaxis={ 
            #'showspikes': True,    
            #'spikemode': 'toaxis',
            #'spikecolor': 'rgba(191, 191, 191, 1)',
            #'spikethickness': 1,
            #'spikedash': 'dash',
            #'automargin': True,
            'tickfont': {'size': 12, 'color': 'LightSteelBlue'},
            #'tickwidth': 1,
            #'tickcolor': 'LightSteelBlue',
            'ticklen': 4,
            #'ticklabelposition': 'inside top',
            #'fixedrange': True,
            #'zeroline': False,
        },
    )

    st.plotly_chart(figuree, use_container_width=True)

