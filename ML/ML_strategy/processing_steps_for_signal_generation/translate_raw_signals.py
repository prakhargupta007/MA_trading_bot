def translate_raw_signals(raw_signals):
    translated_signals = []
    for signal in raw_signals:
        if signal == 0:
            translated_signals.append('SELL')
        elif signal == 1:
            translated_signals.append('HOLD')
        elif signal == 2:
            translated_signals.append('BUY')

    return translated_signals