from config import INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH

def check_indicator_length(data,indicator_parameters):
    too_long_indicators = []
    for indicator,value in indicator_parameters.items():
        if indicator in INDICATORS_WHICH_ARE_NOT_TO_BE_CHECKED_FOR_LENGTH:
            continue
        if int(value) > len(data):
            too_long_indicators.append(indicator)
    if len(too_long_indicators) != 0:
        message = f'Please check the following indicators, they can\'t be calculated as they exceed the data\'s length\ which is {len(data)}:\n {too_long_indicators}'
        good_to_go = False
    else:
        message = 'All indicators are within the data\'s length'
        good_to_go = True
    return message, good_to_go


