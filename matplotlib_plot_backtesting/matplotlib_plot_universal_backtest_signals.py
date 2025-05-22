# Universal fucntion that can be used for any startegy
import matplotlib.pyplot as plt

def matplotlib_plot_universal_strategy_signals(data, signals, ticker):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plot closing price
    ax.plot(data.index, data['Close'], label='Close Price', color='black')

    holding = False
    hold_start = None

    #Plot buy and sell signals
    for i, signal in enumerate(signals):
        if signal == 'BUY':
            ax.scatter(data.index[i], data['Close'].iloc[i], color='orange', label='BUY' if 'BUY' not in ax.get_legend_handles_labels()[1] else "")
            hold_start = data.index[i]
            holding = True
        elif signal == 'SELL':
            ax.scatter(data.index[i], data['Close'].iloc[i], color='blue', label='SELL' if 'SELL' not in ax.get_legend_handles_labels()[1] else "")
            if holding and hold_start:
                ax.axvspan(hold_start, data.index[i], color='lightgreen', alpha=0.3)
                holding = False

    # Title and labels
    ax.set_title(f'Backtested Strategy on {ticker} stock', fontsize=16)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()

    plt.show()
