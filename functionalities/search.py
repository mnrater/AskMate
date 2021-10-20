from functionalities import data_manager

QUESTION_ID_INDEX = 0
QUESTION_TITLE_INDEX = 4
QUESTION_MESSAGE_INDEX = 5
QUESTION_SUBMISSION_TIME = 1
Answer_SUBMISSION_TIME = 1
ANSWER_MESSAGE_INDEX = 4
QUESTION_ID_IN_ANSWER = 3


def get_id_question_after_search(search_phrase):
    questions = data_manager.import_data_list("question")
    list_id = []
    for question in questions:
        if search_phrase in question[QUESTION_TITLE_INDEX] or search_phrase in question[QUESTION_MESSAGE_INDEX]:
            list_id.append(question[QUESTION_ID_INDEX])

    answers = data_manager.import_data_list("answer")
    for answer in answers:
        if search_phrase in answer[ANSWER_MESSAGE_INDEX]:
            list_id.append(answer[QUESTION_ID_IN_ANSWER])
    return list_id
