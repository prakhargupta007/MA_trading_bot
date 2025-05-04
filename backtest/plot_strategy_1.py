import matplotlib.pyplot as plt

from indicators.sma import calculate_sma
from indicators.rsi import calculate_rsi
from indicators.macd import calculate_macd

def plot_and_show_indicators_and_signals_of_strategy_1(data, signals, sma_long_period, sma_short_period, rsi_period, macd_fast, macd_short, macd_signal, ticker):
    # Create figure and axis
    fig, ax1 = plt.subplots(figsize=(14, 7))

    sma_short = calculate_sma(data, sma_short_period)
    sma_long = calculate_sma(data, sma_long_period)
    rsi = calculate_rsi(data, rsi_period)
    macd, macd_signal_line = calculate_macd(data, macd_fast, macd_short, macd_signal)

    # Plot closing price and indicators (SMA, MACD) on the primary axis (ax1)
    ax1.plot(data.index, data['Close'], label='Close Price', color='black')
    ax1.plot(data.index, sma_short, label='SMA Short', color='green')
    ax1.plot(data.index, sma_long, label='SMA Long', color='red')
    ax1.plot(data.index, macd, label='MACD', color='#FFD700')
    ax1.plot(data.index, macd_signal_line, label='MACD Signal Line', color='grey')

    # Plot buy and sell signals
    holding = False
    hold_start = None
    for i, signal in enumerate(signals):
        if signal == 'BUY':
            ax1.scatter(data.index[i], data['Close'].iloc[i], color='orange', label='BUY' if 'BUY' not in ax1.get_legend_handles_labels()[1] else "")
            hold_start = data.index[i]
            holding = True
        elif signal == 'SELL':
            ax1.scatter(data.index[i], data['Close'].iloc[i], color='blue', label='SELL' if 'SELL' not in ax1.get_legend_handles_labels()[1] else "")
            if holding and hold_start:
                ax1.axvspan(hold_start, data.index[i], color='lightgreen', alpha=0.3)
                holding = False

    # Title and labels for price-related data
    ax1.set_title(f'Backtested Strategy on {ticker} stock', fontsize=16)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')

    # Create a secondary axis for RSI
    ax2 = ax1.twinx()
    ax2.plot(data.index, rsi, label='RSI', color='purple')
    ax2.set_ylabel('RSI')

    # Add legends for both axes
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Show the plot
    plt.show()

    return fig
