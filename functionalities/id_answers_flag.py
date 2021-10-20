from functionalities import data_manager


def check_if_any_answers(question_id):
    if question_id is None:
        question_id = 0
    question_id = int(question_id)
    is_flag = False
    answers = data_manager.import_data_list("answer")
    for answer in answers:
        if answer[3] == question_id:
            is_flag = True
            return is_flag
    return is_flag


def check_if_any_comments(question_id):
    is_flag_comment = False
    comments = data_manager.import_data_list("comment")
    for comment in comments:
        if comment[1] == question_id:
            is_flag_comment = True
            return is_flag_comment
    return is_flag_comment


def check_if_any_comments_in_answers(answer_id):
    is_flag_comment = False
    answers = data_manager.import_data_list("comment")
    for answer in answers:
        if answer[1] == answer_id:
            is_flag_comment = True
            return is_flag_comment
    return is_flag_comment


def check_if_any_tags(question_id):
    if question_id is None:
        question_id = 0
    question_id = int(question_id)
    tags = data_manager.import_data_list("question_tag")
    is_flag_tag = False
    for tag in tags:
        if tag[0] == question_id:
            is_flag_tag = True
            return is_flag_tag
    return is_flag_tag