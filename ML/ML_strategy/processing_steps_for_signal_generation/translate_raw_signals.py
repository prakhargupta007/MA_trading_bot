def translate_raw_signals(raw_signals):
    'raw_signals can also contain NaNs, so thes will get translated into HOLD'
    translated_signals = []
    for signal in raw_signals:
        if isinstance(signal, str):
            translated_signals.append(signal)
        elif signal == 0:
            translated_signals.append('SELL')
        elif signal == 1:
            translated_signals.append('HOLD')
        elif signal == 2:
            translated_signals.append('BUY')
            
    return translated_signals