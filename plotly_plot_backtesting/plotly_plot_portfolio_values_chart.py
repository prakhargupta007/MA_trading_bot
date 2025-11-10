import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio

# disable browser auto-open
pio.renderers.default = "browser"

def plotly_plot_portfolio_values(portfolio_values_series, data, ticker):
    """
    Plots and saves the portfolio value over time using Plotly.

    Args:
        portfolio_values_series (list or pd.Series): Portfolio values in time order.
        data (pd.DataFrame): The DataFrame used in backtesting (for date index).
        ticker (str): Stock ticker, used in chart title and filename.
    """

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,
        y=portfolio_values_series,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#2E04D4', width=2),
        marker=dict(size=1),
        hovertemplate='Date: %{x}<br>Value: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=f'Portfolio value of {ticker}',
        xaxis_title='Date',
        yaxis_title='Portfolio Value [USD]',
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )

    # ✅ define and create the output folder
    output_dir = "/Users/prakhar/Desktop/MA_trading_bot/automated_backtesting_results/backtesting_portfolio_plots"
    os.makedirs(output_dir, exist_ok=True)

    # ✅ create file path per ticker
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"{ticker}_portfolio_value_{timestamp}.html")

    # ✅ save without opening in browser
    fig.write_html(output_path, auto_open=False)

    print(f"✅ Portfolio plot saved at: {output_path}")
    return output_path
