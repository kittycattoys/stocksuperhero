import plotly.graph_objects as go
import streamlit as st

def plot_metric(df_fact, selected_stock_symbol):
    # Calculate min and max values for 'p' column
    min_p = df_fact['p'].min()
    max_p = df_fact['p'].max()
    
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

    # Add text annotations for min and max values
    fig.add_annotation(x=df_fact['dt_st'].max(), y=min_p,
                       text=f"Min: {min_p:.2f}",
                       showarrow=False, xanchor='left', yanchor='bottom',
                       font=dict(color='white'))

    fig.add_annotation(x=df_fact['dt_st'].max(), y=max_p,
                       text=f"Max: {max_p:.2f}",
                       showarrow=False, xanchor='left', yanchor='top',
                       font=dict(color='white'))

    # Customize chart layout
    fig.update_layout(
        title=f"{selected_stock_symbol} Stock Prices",
        height=500,
        xaxis_title=None,
        yaxis_title=None,
        showlegend=False, 
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x',
        dragmode=False,
        yaxis={
            'showspikes': True, 
            'spikemode': 'across', 
            'spikecolor': 'red', 
            'spikethickness': 1
        },
        xaxis={
            'showspikes': True, 
            'spikemode': 'across', 
            'spikecolor': 'red', 
            'spikethickness': 1
        },
        modebar=dict(remove=["zoom", "pan", "select2d", "lasso2d", "autoScale", "resetScale", "zoomIn", "zoomOut", "resetViews"])
    )

    # Display the Plotly chart
    st.plotly_chart(fig, use_container_width=True)