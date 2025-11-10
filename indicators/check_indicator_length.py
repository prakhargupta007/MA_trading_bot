from config import INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH

def check_indicator_length(data, indicator_parameters):
    too_long_indicators = []

    for indicator, value in indicator_parameters.items():
        # Skip indicators explicitly marked to ignore
        if indicator in INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH:
            continue

        # Skip non-numeric or invalid types safely
        try:
            val_int = int(value)
        except (ValueError, TypeError):
            continue  # e.g. strings like 'sentiment' or file paths

        # Perform the length check only for numeric values
        if val_int > len(data):
            too_long_indicators.append(indicator)

    if too_long_indicators:
        message = (
            f"Please check the following indicators, they can't be calculated as they "
            f"exceed the data's length ({len(data)}):\n {too_long_indicators}"
        )
        good_to_go = False
    else:
        message = "✅ All indicators are within the data's length"
        good_to_go = True

    return message, good_to_go