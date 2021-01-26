import pandas as pd


def generate_string_from_array(array):
    array_string = ""

    for element in array:
        array_string = array_string + element + ', '

    return array_string[:-2]


def generate_top_n_list(query_result_dates, element_list, n):
    temp_df = pd.DataFrame()
    for key in query_result_dates.keys():
        temp_df = temp_df.append(query_result_dates[key])
    n_list = temp_df.sum(axis=0).filter(element_list).sort_values(ascending=False).index[:n]

    return n_list


def generate_option_array_from_list(list_of_options):
    options = []

    if len(list_of_options.shape) == 1:
        for option in list_of_options:
            temp_dict = {'label': option, 'value': option}
            options.append(temp_dict)
    else:
        for i in range(len(list_of_options)):
            temp_dict = {'label': list_of_options.iloc[i, 1],
                         'value': list_of_options.iloc[i, 0]}
            options.append(temp_dict)
    return options


def generate_df_from_query_result(query_result):
    df = pd.DataFrame()
    metric_list = query_result.keys()
    for metric in metric_list:
        df = df.append(query_result[metric])
    df.index = metric_list
    return df


def generate_category_options(columns):
    options = []
    for col in columns:
        category_text = col[len('category_'):].replace('_', ' ')
        temp_dict = {'label': category_text, 'value': col}
        options.append(temp_dict)

    return options


def generate_building_list_sim(building_list):
    building_list_sim = []
    for building in building_list:
        building_list_sim.append(building)
        building_list_sim.append("simulation_"+building)
    return building_list_sim
