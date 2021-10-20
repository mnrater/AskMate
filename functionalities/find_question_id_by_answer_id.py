from flask import Flask, render_template, request, redirect, url_for
from functionalities import data_manager, id_answers_flag


def find_question_id(answer_id):
    answers = data_manager.import_data_list("answer")
    id_question_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    for answer in answers:
        if answer_id == answer[id_answer_index]:
            question_id = int(answer[id_question_answer_index])
            return question_id
    return None


def find_answer_id(question_id):
    answers = data_manager.import_data_list("answer")
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    for answer in answers:
        if question_id == answer[id_answer_index]:
            return True
    return False


def cos():
    list_comments = []
    comments = data_manager.import_data_list("comment")
    for comment in comments:
        if comment[2] is not None:
            list_comments.append(comment[2])

    list_comments = set(list_comments)
    return list_comments


def find_user_id(mail):
    data = data_manager.return_account_data(str(mail).lower())
    user_id = data[0]
    return user_id


def find_question_id_by_comment(comment_id):
    comments = data_manager.import_data_list("comment")
    for comment in comments:
        if int(comment_id) == comment[0] and comment[1] is not None:
            question_id = int(comment[1])
            return question_id
    return None


def find_answer_id_by_comment(comment_id):
    comments = data_manager.import_data_list("comment")
    for comment in comments:
        if int(comment_id) == comment[0] and comment[2] is not None:
            answer_id = int(comment[2])
            return answer_id
    return None


def find_edited_count(comment_id):
    comments = data_manager.import_data_list("comment")
    for comment in comments:
        if int(comment_id) == comment[0]:
            return comment[5]
    return None


def find_comments_id_in_question(question_id):
    comments = data_manager.import_data_list("comment")
    list_of_comments_id = []
    for comment in comments:
        if int(question_id) == comment[1]:
            list_of_comments_id.append(comment[0])
    return list_of_comments_id


def find_answer_id_in_question(question_id):
    answers = data_manager.import_data_list("answer")
    list_of_answers_id = []
    for answer in answers:
        if int(question_id) == answer[3]:
            list_of_answers_id.append(answer[0])
    return list_of_answers_id
