import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"

def plotly_plot_portfolio_values(portfolio_values_series, data, ticker):
    '''
    Plots the portfolio values over time using Plotly and opens the chart in the browser.

    Arguments:
        portfolio_values_series (list or pd.Series): Portfolio values (must be in time order)
        data (pd.DataFrame): The same DataFrame used in the backtest, to extract the correct date index
        hex_color (str): Hex color code for the line (default is Plotly blue)
    '''
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index,  # Dates on x-axis
        y=portfolio_values_series,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#2E04D4', width=2),
        marker=dict(size=1),  # Small dots
        hovertemplate='Date: %{x}<br>Value: %{y}<extra></extra>'  # Clean hoverbox
    ))

    fig.update_layout(
        title=f'Portfolio value of {ticker}',
        xaxis_title='Date',
        yaxis_title='Portfolio Value [USD]',
        template='plotly_white',
        height=500,
        hovermode='x unified'
    )

    fig.show()
