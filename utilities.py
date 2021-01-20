import pandas as pd
def generate_string_from_array(array):
    array_string = ""

    for element in array:
        array_string = array_string + element + ', '

    return array_string[:-2]


def generate_top_n_df(df, n):
    sorted_df = df.sort_values(by=df.index[0], axis=1, ascending=False)
    col_to_drop = sorted_df.columns[n:]
    sorted_df['others'] = sorted_df.loc[:, col_to_drop].sum(axis=1)
    sorted_df = sorted_df.drop(columns=col_to_drop)
    return sorted_df


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
