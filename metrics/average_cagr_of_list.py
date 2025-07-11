def calculate_average_cagr_of_list(cagr_list):
    average_cagr = sum(cagr_list) / len(cagr_list)
    return round(average_cagr, 2)