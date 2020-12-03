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
    for option in list_of_options:
        temps_dict = {'label': option, 'value': option}
        options.append(temps_dict)
    return options
