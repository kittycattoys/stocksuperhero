import numpy as np
import plotly.graph_objects as go

# Function to create the pie chart
def create_pie_chart(df_dim_det, metric_type, metric_color):
    # Define the background color and quadrant colors
    plot_bgcolor = "rgba(255, 255, 255, 0)"
    quadrant_colors = [plot_bgcolor, "lightgreen", "green", "orange", "red"]
    quadrant_text = ["", "<b>Premium</b>", "<b>Fair</b>", "<b>Discount</b>", "<b>Sale</b>"]
    n_quadrants = len(quadrant_colors) - 1

    # Set the current value and limits
    current_value = df_dim_det[f'{metric_type}n'].iloc[0]
    min_value = 0
    max_value = 180
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    # Fixed font sizes
    annotation_font_size = 24
    quadrant_label_font_size = 16

    fig = go.Figure(
        data=[go.Pie(
            values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
            rotation=90,
            hole=0.5,
            marker_colors=quadrant_colors,
            text=quadrant_text,
            textinfo="text",
            hoverinfo="skip",
            textfont=dict(color="dimgray") 
        )],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=40, l=50, r=50),
            width=350,
            height=350,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>{metric_type} {df_dim_det[f'{metric_type}t'].iloc[0]}</b><br><b>{df_dim_det[metric_type].iloc[0]}x</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.23, yanchor="bottom", yref="paper",
                    showarrow=False,
                    font=dict(size=annotation_font_size)
                ),

                # Adding quadrant labels
                go.layout.Annotation(
                    text=f"<b>{df_dim_det[f'{metric_type}max'].iloc[0]}x</b>",
                    x=1.13, y=0.43, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="lightgreen"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det[f'{metric_type}8'].iloc[0]}x</b>",
                    x=1, y=0.8, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="green"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det[f'{metric_type}5'].iloc[0]}x</b>",
                    x=0.5, y=0.95, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="yellow"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det[f'{metric_type}2'].iloc[0]}x</b>",
                    x=0, y=0.8, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="orange"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det[f'{metric_type}min'].iloc[0]}x</b>",
                    x=-0.13, y=0.43, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="red"),
                    showarrow=False
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.49, x1=0.51,
                    y0=0.49, y1=0.51,
                    fillcolor="yellow",
                    line_color="yellow",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="yellow", width=3)
                )
            ],
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
    )
    
    return fig