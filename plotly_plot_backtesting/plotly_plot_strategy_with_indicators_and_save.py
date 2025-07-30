import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from config import OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART

# Import all indicator calculation functions
from indicators.sma import calculate_sma
from indicators.ema import calculate_ema
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd

def plotly_plot_strategy_with_indicators_and_save(data, signals, ticker, chosen_strategy, indicator_parameters):
    """
    Plots price, indicators, and trading signals for any strategy and saves the plot as HTML.
    
    Args:
        data (pd.DataFrame): Price data with 'Close' column
        signals (list): List of trading signals ('BUY', 'SELL', 'HOLD')
        ticker (str): Stock ticker symbol
        chosen_strategy (str): Name of the strategy being used
        indicator_parameters (dict): Dictionary containing all indicator parameters
    """
    # Get the required indicators for this strategy from the indicator map
    from indicators.strategywise_indicator_map import indicator_map
    required_indicators = indicator_map.get(chosen_strategy.lower(), [])
    
    # Calculate all indicators
    calculated_indicators = {}
    
    if 'sma_short' in required_indicators:
        calculated_indicators['sma_short'] = calculate_sma(data, indicator_parameters['sma_short_period'])
    if 'sma_long' in required_indicators:
        calculated_indicators['sma_long'] = calculate_sma(data, indicator_parameters['sma_long_period'])
    if 'ema_short' in required_indicators:
        calculated_indicators['ema_short'] = calculate_ema(data, indicator_parameters['ema_short_period'])
    if 'ema_long' in required_indicators:
        calculated_indicators['ema_long'] = calculate_ema(data, indicator_parameters['ema_long_period'])
    if 'rsi' in required_indicators:
        calculated_indicators['rsi'] = calculate_rsi(data, indicator_parameters['rsi_period'])
    if 'macd' in required_indicators or 'macd_signal' in required_indicators:
        macd, macd_signal = calculate_macd(
            data, 
            indicator_parameters['macd_fast'], 
            indicator_parameters['macd_slow'], 
            indicator_parameters['macd_signal']
        )
        calculated_indicators['macd'] = macd
        calculated_indicators['macd_signal'] = macd_signal

    # Determine number of subplots needed
    n_subplots = 1  # Start with 1 for price
    if 'rsi' in calculated_indicators:
        n_subplots += 1
    if 'macd' in calculated_indicators:
        n_subplots += 1

    # Create subplots
    fig = make_subplots(
        rows=n_subplots, 
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=([f'Price and Indicators'] + 
                       ['RSI'] * ('rsi' in calculated_indicators) +
                       ['MACD'] * ('macd' in calculated_indicators))
    )

    # Plot price and moving averages on the first subplot
    fig.add_trace(
        go.Scatter(
            x=data.index, 
            y=data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='black')
        ),
        row=1, col=1
    )

    # Add moving averages
    for indicator in ['sma_short', 'sma_long', 'ema_short', 'ema_long']:
        if indicator in calculated_indicators:
            # Assign user-specified colors for each indicator
            color_map = {
                'sma_short': '#72d600',   # soft green
                'sma_long': '#00750a',    # deep forest green
                'ema_short': '#fad016',   # golden yellow
                'ema_long': '#cc062e'     # crimson red
            }
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=calculated_indicators[indicator],
                    mode='lines',
                    name=indicator.upper(),
                    line=dict(color=color_map[indicator])
                ),
                row=1, col=1
            )

    # Add RSI if present
    if 'rsi' in calculated_indicators:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=calculated_indicators['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#28bdba')
            ),
            row=2 if 'rsi' in calculated_indicators else 1,
            col=1
        )
        # Add overbought/oversold lines
        fig.add_hline(y=indicator_parameters['rsi_overbought'], line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=indicator_parameters['rsi_oversold'], line_dash="dash", line_color="green", row=2, col=1)

    # Add MACD if present
    if 'macd' in calculated_indicators:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=calculated_indicators['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#9308a8')
            ),
            row=n_subplots,
            col=1
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=calculated_indicators['macd_signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='#f50fa8')
            ),
            row=n_subplots,
            col=1
        )

    # Store buy/sell points and hold regions
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

    # Add BUY markers (blue)
    fig.add_trace(
        go.Scatter(
            x=buy_x, 
            y=buy_y,
            mode='markers',
            name='BUY',
            marker=dict(color='blue', size=10, symbol='triangle-up')
        ),
        row=1, col=1
    )

    # Add SELL markers (orange)
    fig.add_trace(
        go.Scatter(
            x=sell_x, 
            y=sell_y,
            mode='markers',
            name='SELL',
            marker=dict(color='orange', size=10, symbol='triangle-down')
        ),
        row=1, col=1
    )

    # Add shaded regions between BUY and SELL
    for start, end in hold_regions:
        fig.add_vrect(
            x0=start, 
            x1=end,
            fillcolor='lightgreen',
            opacity=0.3,
            line_width=0,
            row=1, 
            col=1
        )

    # Update layout
    fig.update_layout(
        title=f'Plot of backtested {chosen_strategy.upper()} Strategy on {ticker} Stock with indicators',
        xaxis_title='Date',
        height=600 * n_subplots,  # Increased from 300 to 600 for better visibility
        showlegend=True,
        template='plotly_white',
        hovermode='x unified'
    )

    # Update y-axis labels
    fig.update_yaxes(title_text="Price", row=1, col=1)
    if 'rsi' in calculated_indicators:
        fig.update_yaxes(title_text="RSI", row=2, col=1)
    if 'macd' in calculated_indicators:
        fig.update_yaxes(title_text="MACD", row=n_subplots, col=1)

    # Show the figure
    fig.show()

    # Save the interactive chart as HTML
    file_name = f"{ticker}_{chosen_strategy}_strategy_with_indicators_plot.html"
    full_path = os.path.join(OUTPUT_FOLDER_PATH_FOR_PLOTLY_CHART, file_name)
    fig.write_html(full_path) 