import plotly.graph_objects as go
from config import OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART
import os

import plotly.io as pio
pio.renderers.default = "browser"

def plotly_plot_universal_strategy_signals_and_save(data, signals, ticker):
    fig = go.Figure()

    # Plot close price
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'],
        mode='lines',
        name='Close Price',
        line=dict(color='black')
    ))

    # Store buy/sell points
    buy_x = []
    buy_y = []
    sell_x = []
    sell_y = []
    hold_regions = []

    holding = False
    hold_start = None

    for i, signal in enumerate(signals):
        if signal == 'BUY':
            buy_x.append(data.index[i])
            buy_y.append(data['Close'].iloc[i])
            hold_start = data.index[i]
            holding = True
        elif signal == 'SELL':
            sell_x.append(data.index[i])
            sell_y.append(data['Close'].iloc[i])
            if holding and hold_start:
                hold_regions.append((hold_start, data.index[i]))
                holding = False

    # Add BUY markers
    fig.add_trace(go.Scatter(
        x=buy_x, y=buy_y,
        mode='markers',
        name='BUY',
        marker=dict(color='orange', size=10, symbol='triangle-up')
    ))

    # Add SELL markers
    fig.add_trace(go.Scatter(
        x=sell_x, y=sell_y,
        mode='markers',
        name='SELL',
        marker=dict(color='blue', size=10, symbol='triangle-down')
    ))

    # Add shaded regions between BUY and SELL
    for start, end in hold_regions:
        fig.add_vrect(
            x0=start, x1=end,
            fillcolor='lightgreen',
            opacity=0.3,
            line_width=0
        )

    # Update layout
    fig.update_layout(
        title=f'Backtested Strategy on {ticker} stock',
        xaxis_title='Date',
        yaxis_title='Price',
        hovermode='x unified',
        template='plotly_white',
        height=600
    )

    # Show the figure
    fig.show()

    # Hard-coded folder path
    file_name = f"{ticker}_strategy_plot.html"
    # Save the interactive chart as HTML into that folder
    full_path = os.path.join(OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART, file_name)
    fig.write_html(full_path)


