from functionalities import data_manager, id_answers_flag


def refactor_to_brs(data):
    # function that refactors "\n" signs to "<br>" signs. Python to HTML refactor.
    # data = str/list/dict
    if isinstance(data, list):
        for entry in data:
            for counter in range(0, len(entry)):
                entry[counter] = entry[counter].replace('\\n', "<br>")
        return data
    elif isinstance(data, dict):
        for key, value in data.items():
            data[key] = value.replace('\\n', "<br>")
        return data
    elif isinstance(data, str):
        data = data.replace('\\n', "<br>")
        return data
    else:
        raise ValueError("Wrong input!")