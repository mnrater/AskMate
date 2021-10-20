from functionalities import data_manager, id_answers_flag


def vote(mode_up_down, mode_question_answer, _id):
    # function that changes value of vote_number and returns list of lists.
    # mode_up_down = "up"/"down" depending on vote value that needs to be changed - up or down.
    # mode_question_answer = "question"/"answer" depending on question or answer needed to be voted.
    # _id = id of an entry.
    data = data_manager.import_data_list(mode_question_answer)
    votes_index = data_manager.SORTING_DICT[f"{mode_question_answer}"]["categories_indexes"]["vote_number"]
    id_index = data_manager.SORTING_DICT[f"{mode_question_answer}"]["categories_indexes"]["id"]
    for entry in data:
        if entry[id_index] == _id:
            new_vote_value = int(entry[votes_index])
            if mode_up_down == "up":
                new_vote_value += 1
                data_manager.edit_value(mode_question_answer, _id, "vote_number", new_vote_value)
            elif mode_up_down == "down":
                new_vote_value -= 1
                data_manager.edit_value(mode_question_answer, _id, "vote_number", new_vote_value)