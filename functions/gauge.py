import numpy as np
import plotly.graph_objects as go

# Function to create the pie chart
def create_pie_chart(df_dim_det, metric_type, metric_color):
    # Define the background color and quadrant colors
    plot_bgcolor = "rgba(255, 255, 255, 0)"
    quadrant_colors = [plot_bgcolor, "#f25829", "#f2a529", "#85e043", "#2bad4e"]
    quadrant_text = ["", "<b>Very High</b>", "<b>High</b>", "<b>Medium</b>", "<b>Low</b>", "<b>Very low</b>"]
    n_quadrants = len(quadrant_colors) - 1

    # Set the current value and limits
    current_value = 19.0
    min_value = 0
    max_value = 50
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    # Fixed font sizes
    annotation_font_size = 22
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
        )],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=40, l=50, r=50),
            width=350,
            height=350,
            paper_bgcolor=plot_bgcolor,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>Price / Sales</b><br><b>{df_dim_det['ps'].iloc[0]}x</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.25, yanchor="bottom", yref="paper",
                    showarrow=False,
                    font=dict(size=annotation_font_size)
                ),

                # Adding quadrant labels
                go.layout.Annotation(
                    text=f"<b>{df_dim_det['psmax'].iloc[0]}x</b>",
                    x=1.1, y=0.5, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#f25829"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det['ps8'].iloc[0]}x</b>",
                    x=1, y=0.8, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#f2a529"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det['ps5'].iloc[0]}x</b>",
                    x=0.5, y=0.95, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#eff229"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det['ps2'].iloc[0]}x</b>",
                    x=0, y=0.8, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#85e043"),
                    showarrow=False
                ),
                go.layout.Annotation(
                    text=f"<b>{df_dim_det['psmin'].iloc[0]}x</b>",
                    x=-0.1, y=0.5, xanchor="center", yanchor="bottom",
                    font=dict(size=quadrant_label_font_size, color="#2bad4e"),
                    showarrow=False
                )
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="yellow",
                    line_color="yellow",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="yellow", width=4)
                )
            ],
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
    )
    
    return fig