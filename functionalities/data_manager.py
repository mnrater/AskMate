import os
import random
import string
from typing import List, Dict
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from functionalities import database_common
import hashlib
import base64
import uuid
import binascii

SORTING_DICT = {
    "answer": {
        "categories_indexes": {
            "id": 0,
            "submision_time": 1,
            "vote_number": 2,
            "question_id": 3,
            "message": 4,
            "image_path": 5}
    },
    "question": {
        "categories_indexes": {
            "id": 0,
            "submision_time": 1,
            "view_number": 2,
            "vote_number": 3,
            "title": 4,
            "message": 5,
            "image_path": 6}

    }
}


@database_common.connection_handler
def add_to_database(cursor, mode: str, data: dict) -> None:
    '''
    mode: "question"/"answer"
    data: dictionary of values like {"submission_time": 2020-10-16 16:36:00 ... }
    return: None
    '''
    if mode == "question":
        keys_expected = ['submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
    elif mode == "answer":
        keys_expected = ['submission_time', 'vote_number', 'question_id', 'message', 'image']
    elif mode == "comment":
        keys_expected = ['question_id', 'answer_id', 'message', 'submission_time', 'edited_count']
    elif mode == "add_new_tag":
        keys_expected = ['name']
    elif mode == "add_tag_to_question":
        keys_expected = ['question_id', 'tag_id']
    elif mode == "add_user":
        keys_expected = ['username', "password", "register_date"]
    elif mode == "add_user_personal_info":
        keys_expected = ['user_id', "salt", "hash"]
    else:
        raise ValueError("Wrong mode!")
    for key in keys_expected:
        if key not in data:
            raise ValueError(f'Missing expected key: {key}')
    if mode == "question":
        query = sql.SQL("INSERT INTO question ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "answer":
        query = sql.SQL("INSERT INTO answer ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "comment":
        query = sql.SQL("INSERT INTO comment ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "add_new_tag":
        query = sql.SQL("INSERT INTO tag ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "add_tag_to_question":
        query = sql.SQL("INSERT INTO question_tag ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "add_user":
        query = sql.SQL("INSERT INTO account ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    if mode == "add_user_personal_info":
        query = sql.SQL("INSERT INTO personal_info ({}) VALUES ({})").format(
            sql.SQL(', ').join(map(sql.Identifier, keys_expected)),
            sql.SQL(', ').join(map(sql.Placeholder, keys_expected)))
    cursor.execute(query, data)


@database_common.connection_handler
def import_data_list(cursor, mode: str) -> list:
    '''
    mode: "question"/"answer"
    return: list of data
    '''
    if mode == "question":
        query = """
            SELECT *
            FROM question
            ORDER BY id"""
    if mode == "answer":
        query = """
            SELECT *
            FROM answer
            ORDER BY id"""
    if mode == "comment":
        query = """
           SELECT *
           FROM comment
           ORDER BY id"""
    if mode == "tag":
        query = """
           SELECT *
           FROM tag
           ORDER BY id"""
    if mode == "question_tag":
        query = """
           SELECT *
           FROM question_tag
           ORDER BY question_id"""
    cursor.execute(query, {'mode': mode})
    return cursor.fetchall()


@database_common.connection_handler
def import_newest_five(cursor, mode: str) -> list:
    '''
    mode: "question"/"answer"
    return: list of data
    '''
    if mode == "question":
        query = """
            SELECT *
            FROM question
            ORDER BY submission_time DESC
            LIMIT 5"""
    if mode == "answer":
        query = """
            SELECT *
            FROM answer
            ORDER BY submission_time DESC
            LIMIT 5"""
    if mode == "comment":
        query = """
               SELECT *
               FROM comment
               ORDER BY submission_time DESC
               LIMIT 5"""
    cursor.execute(query, {'mode': mode})
    return cursor.fetchall()


@database_common.connection_handler
def import_unique_tag_names(cursor) -> list:
    '''
    mode: "tag"
    return: list of tags
    '''
    query = """
        SELECT DISTINCT name
        FROM tag"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def find_id_of_a_tag(cursor, tag) -> list:
    '''
    mode: "tag"
    return: list of tags
    '''
    query = """
        SELECT DISTINCT id
        FROM tag
        WHERE name = %(tag)s
        LIMIT 1"""
    cursor.execute(query, {'tag': tag})
    return cursor.fetchall()


@database_common.connection_handler
def import_sorted_list(cursor, mode: str, sort_type: str, asc_desc: str) -> list:
    '''
    mode: "question"/"answer..."
    return: sorted list of data
    '''
    query = """
        SELECT *
        FROM {}
        ORDER BY {} {}""".format(mode, sort_type, asc_desc)
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def import_headers(cursor, mode: str) -> list:
    '''
    mode: "question"/"answer"
    return: list of headers
    '''
    if mode == "question":
        query = """
        SELECT COLUMN_NAME 
        FROM information_schema.columns
        WHERE table_name = 'question'
        """
    elif mode == "answer":
        query = """
        SELECT COLUMN_NAME 
        FROM information_schema.columns
        WHERE table_name = 'answer'
        """
    elif mode == "comment":
        query = """
        SELECT COLUMN_NAME 
        FROM information_schema.columns
        WHERE table_name = 'comment'
        """
    else:
        raise ValueError("No such mode!")
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def edit_value(cursor, mode: str, question_id: int, column_to_replace: str, data_to_replace) -> None:
    if mode == "question":
        if column_to_replace == "vote_number":
            data_to_replace = int(data_to_replace)
            query = """
            UPDATE question
            SET vote_number = %(data_to_replace)s
            WHERE id = %(question_id)s
            """
        if column_to_replace == "image":
            query = """
            UPDATE question
            SET image = %(data_to_replace)s
            WHERE id = %(question_id)s
            """
    elif mode == "answer":
        if column_to_replace == "vote_number":
            data_to_replace = int(data_to_replace)
            query = """
            UPDATE answer
            SET vote_number = %(data_to_replace)s
            WHERE id = %(question_id)s
            """
        if column_to_replace == "image":
            query = """
            UPDATE answer
            SET image = %(data_to_replace)s
            WHERE id = %(question_id)s
            """
    else:
        raise ValueError("No such mode!")
    cursor.execute(query, {'mode': mode, 'question_id': question_id, 'column_to_replace': column_to_replace,
                           'data_to_replace': data_to_replace})


@database_common.connection_handler
def edit_line(cursor, mode: str, _id: int, dict_replace: dict) -> None:
    if mode == "question":
        new_submission_time = dict_replace['submission_time']
        new_title = dict_replace['title']
        new_message = dict_replace['message']
        new_image = dict_replace['image']
        query = """
        UPDATE question 
        SET submission_time = %(new_submission_time)s,
            title = %(new_title)s,
            message = %(new_message)s,
            image = %(new_image)s
        WHERE id = %(_id)s
        """

        cursor.execute(query,
                       {'mode': mode, '_id': _id, 'new_submission_time': new_submission_time, 'new_title': new_title,
                        'new_message': new_message, 'new_image': new_image})

    elif mode == "answer":
        new_submission_time = dict_replace['submission_time']
        new_message = dict_replace['message']
        new_image = dict_replace['image']
        query = """
        UPDATE answer
        SET submission_time = %(new_submission_time)s,
            message = %(new_message)s,
            image = %(new_image)s
        WHERE id = %(_id)s
        """

        cursor.execute(query, {'mode': mode, '_id': _id, 'new_submission_time': new_submission_time,
                               'new_message': new_message, 'new_image': new_image})

    elif mode == "comment":
        new_submission_time = dict_replace['submission_time']
        new_message = dict_replace['message']
        new_edited_count = dict_replace['edited_count']
        query = """
        UPDATE comment
        SET message = %(new_message)s,
            submission_time = %(new_submission_time)s,
            edited_count = %(new_edited_count)s
        WHERE id = %(_id)s
        """

        cursor.execute(query, {'mode': mode, '_id': _id, 'new_message': new_message,
                               'new_submission_time': new_submission_time, 'new_edited_count': new_edited_count})

    else:
        raise ValueError("No such mode!")


@database_common.connection_handler
def delete_line(cursor, mode: str, _id: int) -> None:
    if mode == "question":
        query = """
        DELETE FROM question
        WHERE id = %(_id)s
        """
        cursor.execute(query, {'_id': _id})

    elif mode == "answer":
        query = """
        DELETE FROM answer 
        WHERE id = %(_id)s
        """
        delete_connected_comment_query = """
        DELETE FROM comment
        WHERE answer_id = %(_id)s
        """
        cursor.execute(delete_connected_comment_query, {'_id': _id})
        cursor.execute(query, {'_id': _id})

    elif mode == "comment":
        query = """
        DELETE FROM comment
        WHERE id = %(_id)s
        """
        cursor.execute(query, {'_id': _id})
    else:
        raise ValueError("No such mode!")


@database_common.connection_handler
def delete_tag(cursor, question_id, tag_id) -> None:
    query = """
        DELETE FROM question_tag
        WHERE tag_id = %(tag_id)s AND question_id = %(question_id)s
        """
    cursor.execute(query, {'tag_id': tag_id, 'question_id': question_id})


@database_common.connection_handler
def delete_all_tags(cursor, question_id) -> None:
    query = """
        DELETE FROM question_tag
        WHERE question_id = %(question_id)s
        """
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def return_account_data(cursor, user_email) -> None:
    query = """
            SELECT *
            FROM account
            WHERE username = %(user_email)s
            LIMIT 1
            """
    cursor.execute(query, {'user_email': user_email})
    return cursor.fetchone()


@database_common.connection_handler
def return_personal_account_data(cursor, user_id) -> None:
    query = """
            SELECT *
            FROM personal_info
            WHERE user_id = %(user_id)s
            LIMIT 1
            """
    cursor.execute(query, {'user_id': user_id})
    return cursor.fetchone()


def generate_id(number_of_small_letters=4,
                number_of_capital_letters=2,
                number_of_digits=2,
                number_of_special_chars=2,
                allowed_special_chars=r"_+-!"):
    small_letters = [random.choice(string.ascii_lowercase) for _ in range(number_of_small_letters)]
    capital_letters = [random.choice(string.ascii_uppercase) for _ in range(number_of_capital_letters)]
    digits = [str(random.choice(range(0, 10))) for _ in range(number_of_digits)]
    special_chars = [random.choice(allowed_special_chars) for _ in range(number_of_special_chars)]
    drawn_signs = small_letters + capital_letters + digits + special_chars
    random.shuffle(drawn_signs)
    return "".join(drawn_signs)


def hash_and_salt_password(password):
    salt = hashlib.sha256(os.urandom(32)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    salt_final = salt.decode('ascii')
    pwd_final = (salt + pwdhash).decode('ascii')
    return pwd_final, salt_final


def check_password(user_password, salt, database_password):
    salt_final = salt.encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', user_password.encode('utf-8'), salt_final, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    pwd_final = (salt_final + pwdhash).decode('ascii')
    return pwd_final == database_password
