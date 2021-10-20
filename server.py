import os
import sys
from flask import Flask, session

separator = ";_._;"

server_path = os.path.dirname(os.path.abspath(__file__))

sys.dont_write_bytecode = True
#


from flask import Flask, render_template, request, redirect, url_for
from functionalities import data_manager, id_answers_flag, refactor_new_lines_to_brs, vote, \
    find_question_id_by_answer_id, search
import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'


@app.route("/", methods=['GET', 'POST'])
def base():
    questions = data_manager.import_newest_five("question")
    headers = data_manager.import_headers("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    if request.method == 'POST':
        search_phrase = request.form['search_phrase']
        if search_phrase == "":
            return redirect("/list")
        else:
            return redirect(url_for('search_question', q=search_phrase))
    else:
        return render_template('base.html', questions=questions, headers=headers,
                               id_question_index=id_question_index)


@app.route("/question/<question_id>/upload", methods=["POST"])
def upload_to_question(question_id):
    object_id = question_id
    graphic_file = request.files["file"]

    if not graphic_file:
        return "Seems like file haven't been uploaded", 400

    for file in request.files.getlist("file"):
        # graphic save
        file_name = data_manager.generate_id() + ".jpg"
        final_image_path = "/".join([server_path, "images/question", file_name])
        file.save(final_image_path)
        # image_name_save_path = "/".join([server_path, "images/question"])

        # graphic path save to database
        data_manager.edit_value("question", object_id, "image", file_name)
    return render_template("upload_completed.html", object_type="question", object_id=question_id)


@app.route('/answer/<answer_id>/upload', methods=["POST"])
def upload_to_answer(answer_id):
    object_id = answer_id
    graphic_file = request.files["file"]

    if not graphic_file:
        return "Seems like file haven't been uploaded", 400

    for file in request.files.getlist("file"):
        # graphic save
        file_name = data_manager.generate_id() + ".jpg"
        final_image_path = "/".join([server_path, "images/answer", file_name])
        file.save(final_image_path)
        # image_name_save_path = "/".join([server_path, "images/answer"])

        # graphic path save to database
        data_manager.edit_value("question", object_id, "image", file_name)
    return render_template("upload_completed.html", object_type="answer", object_id=answer_id)


@app.route("/question/<question_id>/delete")
def remove_question(question_id):
    data_manager.delete_all_tags(int(question_id))
    list_of_comments_id = find_question_id_by_answer_id.find_comments_id_in_question(question_id)
    for element in list_of_comments_id:
        data_manager.delete_line("comment", element)
    list_of_answer_id = find_question_id_by_answer_id.find_answer_id_in_question(question_id)
    for element in list_of_answer_id:
        data_manager.delete_line("answer", element)
    data_manager.delete_line("question", question_id)
    return redirect("/list")


@app.route("/answer/<answer_id>/delete")
def remove_answer(answer_id):
    data_manager.delete_line("answer", int(answer_id))
    return redirect('/list')


@app.route('/list')
def list_questions():
    questions = data_manager.import_data_list("question")
    headers = data_manager.import_headers("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    return render_template('list_questions.html', questions=questions, headers=headers,
                           id_question_index=id_question_index)


@app.route('/list', methods=["POST"])
def sort_questions():
    headers = data_manager.import_headers("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    order = request.form["order_by"]
    print(order)

    if request.form['sorted_list'] == "Title" and (request.form["order_by"] == "ASC" or request.form["order_by"] == "DESC"):
        questions = data_manager.import_sorted_list("question", "title", str(order))

    elif request.form['sorted_list'] == "Submission time" and (request.form["order_by"] == "ASC" or request.form["order_by"] == "DESC"):
        questions = data_manager.import_sorted_list("question", "submission_time", str(order))

    elif request.form['sorted_list'] == "Message" and (request.form["order_by"] == "ASC" or request.form["order_by"] == "DESC"):
        questions = data_manager.import_sorted_list("question", "message", str(order))

    elif request.form['sorted_list'] == "Number of view" and (request.form["order_by"] == "ASC" or request.form["order_by"] == "DESC"):
        questions = data_manager.import_sorted_list("question", "view_number", str(order))

    elif request.form['sorted_list'] == "Number of votes" and (request.form["order_by"] == "ASC" or request.form["order_by"] == "DESC"):
        questions = data_manager.import_sorted_list("question", "vote_number", str(order))

    elif request.form['sorted_list'] == "order" or request.form["order_by"] == "ASC/DESC":
        return redirect('/list')

    return render_template('list_questions.html', questions=questions, headers=headers,
                           id_question_index=id_question_index)


@app.route('/question/<question_id>')
def list_question_by_id(question_id):
    if question_id is None:
        question_id = 0
    question_id = int(question_id)
    questions = data_manager.import_data_list("question")
    answers = data_manager.import_data_list("answer")
    answer_headers = data_manager.import_headers("answer")
    comments = data_manager.import_data_list("comment")
    comments_headers = data_manager.import_headers("comment")
    tags = data_manager.import_data_list("tag")
    question_tags = data_manager.import_data_list("question_tag")
    is_flag_tag = id_answers_flag.check_if_any_tags(question_id)
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    comment_id = find_question_id_by_answer_id.find_answer_id(question_id)
    list_comments = find_question_id_by_answer_id.cos()
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    return render_template('list_questions_by_id.html', answer_headers=answer_headers, questions=questions,
                           answers=answers,
                           question_id=question_id, is_flag=is_flag, id_question_index=id_question_index,
                           id_answer_index=id_answer_index, title_question_index=title_question_index,
                           message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index,
                           message_answer_index=message_answer_index, comments=comments,
                           is_flag_comment=is_flag_comment,
                           comments_headers=comments_headers, comment_id=comment_id, list_comments=list_comments,
                           tags=tags, question_tags=question_tags, is_flag_tag=is_flag_tag)


@app.route('/question/<question_id>/vote_up_list')
def vote_up_question_by_id_list_page(question_id):
    vote.vote("up", "question", int(question_id))
    return redirect("/list")


@app.route('/question/<question_id>/vote_up_base')
def vote_up_question_by_id_base_page(question_id):
    vote.vote("up", "question", int(question_id))
    return redirect("/")


@app.route('/answer/<answer_id>/vote_up')
def vote_up_answer_by_id(answer_id):
    answer_id = int(answer_id)
    question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    vote.vote("up", "answer", answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/vote_down_list')
def vote_down_question_by_id_list_page(question_id):
    vote.vote("down", "question", int(question_id))
    return redirect("/list")


@app.route('/question/<question_id>/vote_down_base')
def vote_down_question_by_id_base_page(question_id):
    vote.vote("down", "question", int(question_id))
    return redirect("/")


@app.route('/answer/<answer_id>/vote_down')
def vote_down_answer_by_id(answer_id):
    answer_id = int(answer_id)
    question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    vote.vote("down", "answer", answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/add_question', methods=['GET'])
def display_add_question():
    questions = data_manager.import_data_list("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    return render_template("question.html", questions=questions, id_question_index=id_question_index,
                           title_question_index=title_question_index, message_question_index=message_question_index)


@app.route('/add_question', methods=['POST'])
def add_question():
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    view_number = str(0)
    vote_number = str(0)
    title = request.form['title']
    message = request.form['message']
    image = "no_image"
    new_question = {"submission_time": submission_time, "view_number": view_number, "vote_number": vote_number,
                    "title": title, "message": message, "image": image}
    data_manager.add_to_database("question", new_question)
    return redirect('/list')


@app.route('/question/<question_id>/new_answer', methods=["GET"])
def post_answer(question_id):
    question_id = int(question_id)
    questions = data_manager.import_data_list("question")
    answers = data_manager.import_data_list("answer")
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    return render_template("post_answer.html", questions=questions, answers=answers, question_id=question_id,
                           is_flag=is_flag, id_question_index=id_question_index,
                           title_question_index=title_question_index, message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index,
                           message_answer_index=message_answer_index)


@app.route('/question/<question_id>/new_answer', methods=["POST"])
def add_an_answer(question_id):
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    vote_number = str(0)
    message = request.form['answer']
    image = "no_image"
    question_id = int(question_id)
    new_answer = {"submission_time": submission_time, "vote_number": vote_number, "question_id": question_id,
                  "message": message, "image": image}
    data_manager.add_to_database("answer", new_answer)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/edit_page', methods=["GET"])
def display_edit_a_question(question_id):
    question_id = int(question_id)
    questions = data_manager.import_data_list("question")
    answers = data_manager.import_data_list("answer")
    comments = data_manager.import_data_list("comment")
    tags = data_manager.import_data_list("tag")
    question_tags = data_manager.import_data_list("question_tag")
    is_flag_tag = id_answers_flag.check_if_any_tags(question_id)
    list_comments = find_question_id_by_answer_id.cos()
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    comment_id = find_question_id_by_answer_id.find_answer_id(question_id)
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    return render_template("edit_page_question.html", questions=questions, answers=answers, question_id=question_id,
                           id_question_index=id_question_index, comments=comments, is_flag=is_flag,
                           title_question_index=title_question_index, message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index, is_flag_comment=is_flag_comment,
                           message_answer_index=message_answer_index, comment_id=comment_id,
                           list_comments=list_comments,
                           tags=tags, question_tags=question_tags, is_flag_tag=is_flag_tag)


@app.route('/question/<question_id>/edit_page', methods=["POST"])
def edit_a_question(question_id):
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    title = request.form['title_question']
    message = request.form['message_question']
    image = "no_image"
    edit_question = {"submission_time": submission_time, "title": title, "message": message, "image": image}
    data_manager.edit_line("question", int(question_id), edit_question)
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/edit_page', methods=["GET"])
def display_edit_an_answer(answer_id):
    answer_id = int(answer_id)
    question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    questions = data_manager.import_data_list("question")
    answers = data_manager.import_data_list("answer")
    comments = data_manager.import_data_list("comment")
    list_comments = find_question_id_by_answer_id.cos()
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    comment_id = find_question_id_by_answer_id.find_answer_id(question_id)
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    return render_template("edit_page_answer.html", questions=questions, answers=answers, question_id=question_id,
                           id_answer_index=id_answer_index,
                           answer_id=answer_id, id_question_index=id_question_index, comments=comments, is_flag=is_flag,
                           title_question_index=title_question_index, message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index, is_flag_comment=is_flag_comment,
                           message_answer_index=message_answer_index, list_comments=list_comments,
                           comment_id=comment_id)


@app.route('/answer/<answer_id>/edit_page', methods=["POST"])
def edit_an_answer(answer_id):
    answer_id = int(answer_id)
    question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    message = request.form['message_answer']
    image = "no_image"
    edit_answer = {"submission_time": submission_time, "message": message, "image": image}
    data_manager.edit_line("answer", answer_id, edit_answer)
    return redirect(f'/question/{question_id}')


@app.route('/search/<q>')
def search_question(q):
    questions = data_manager.import_data_list("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    headers = data_manager.import_headers("question")
    list_of_id = search.get_id_question_after_search(q)
    return render_template("search_questions.html", questions=questions,
                           id_question_index=id_question_index, headers=headers,
                           title_question_index=title_question_index, list_of_id=list_of_id)


@app.route('/question/<question_id>/new-comment-page')
def display_comment_page(question_id):
    question_id = int(question_id)
    questions = data_manager.import_data_list("question")
    answers = data_manager.import_data_list("answer")
    answer_headers = data_manager.import_headers("answer")
    comments = data_manager.import_data_list("comment")
    comments_headers = data_manager.import_headers("comment")
    tags = data_manager.import_data_list("tag")
    question_tags = data_manager.import_data_list("question_tag")
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    comment_id = find_question_id_by_answer_id.find_answer_id(question_id)
    list_comments = find_question_id_by_answer_id.cos()
    is_flag_tag = id_answers_flag.check_if_any_tags(question_id)
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    return render_template('comment_page_question.html', answer_headers=answer_headers, questions=questions,
                           answers=answers,
                           question_id=question_id, is_flag=is_flag, id_question_index=id_question_index,
                           id_answer_index=id_answer_index, title_question_index=title_question_index,
                           message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index,
                           message_answer_index=message_answer_index, comments=comments,
                           is_flag_comment=is_flag_comment,
                           comments_headers=comments_headers, comment_id=comment_id, list_comments=list_comments,
                           tags=tags, question_tags=question_tags, is_flag_tag=is_flag_tag)


@app.route('/question/<question_id>/new-comment-page', methods=['POST'])
def comment_page(question_id):
    answer_id = None
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    message = request.form['comment']
    edited_count = None
    question_id = int(question_id)
    new_comment = {"question_id": question_id, "answer_id": answer_id, "message": message,
                   "submission_time": submission_time, "edited_count": edited_count}
    data_manager.add_to_database("comment", new_comment)
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/new-comment-page')
def display_comment_page_answers(answer_id):
    answer_id = int(answer_id)
    question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    questions = data_manager.import_data_list("question")
    tags = data_manager.import_data_list("tag")
    question_tags = data_manager.import_data_list("question_tag")
    is_flag_tag = id_answers_flag.check_if_any_tags(question_id)
    answers = data_manager.import_data_list("answer")
    comments = data_manager.import_data_list("comment")
    list_comments = find_question_id_by_answer_id.cos()
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    comment_id = find_question_id_by_answer_id.find_answer_id(question_id)
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    return render_template("comment_page_answer.html", questions=questions, answers=answers, question_id=question_id,
                           id_answer_index=id_answer_index,
                           answer_id=answer_id, id_question_index=id_question_index, comments=comments, is_flag=is_flag,
                           title_question_index=title_question_index, message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index, is_flag_comment=is_flag_comment,
                           message_answer_index=message_answer_index, list_comments=list_comments,
                           comment_id=comment_id,
                           tags=tags, question_tags=question_tags, is_flag_tag=is_flag_tag)


@app.route('/answer/<answer_id>/new-comment-page', methods=['POST'])
def comment_page_answer(answer_id):
    question_id = None
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    message = request.form['comment']
    edited_count = None
    new_comment = {"question_id": question_id, "answer_id": answer_id, "message": message,
                   "submission_time": submission_time, "edited_count": edited_count}
    data_manager.add_to_database("comment", new_comment)
    question_id = find_question_id_by_answer_id.find_question_id(int(answer_id))
    print(question_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/new-tag', methods=["GET"])
def display_tag_a_question(question_id):
    question_id = int(question_id)
    list_comments = find_question_id_by_answer_id.cos()
    questions = data_manager.import_data_list("question")
    tags = data_manager.import_data_list("tag")
    unique_tags = data_manager.import_unique_tag_names()
    answers = data_manager.import_data_list("answer")
    answer_headers = data_manager.import_headers("answer")
    comments = data_manager.import_data_list("comment")
    comments_headers = data_manager.import_headers("comment")
    is_flag = id_answers_flag.check_if_any_answers(question_id)
    is_flag_comment = id_answers_flag.check_if_any_comments(question_id)
    is_flag_tag = id_answers_flag.check_if_any_tags(question_id)
    question_tags = data_manager.import_data_list("question_tag")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    id_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["id"]
    id_question_in_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["question_id"]
    message_answer_index = data_manager.SORTING_DICT["answer"]["categories_indexes"]["message"]
    return render_template('tag_question.html', answer_headers=answer_headers, questions=questions, answers=answers,
                           question_id=question_id, is_flag=is_flag, id_question_index=id_question_index,
                           id_answer_index=id_answer_index, title_question_index=title_question_index,
                           list_comments=list_comments,
                           message_question_index=message_question_index,
                           id_question_in_answer_index=id_question_in_answer_index,
                           message_answer_index=message_answer_index, comments=comments,
                           is_flag_comment=is_flag_comment,
                           comments_headers=comments_headers, tags=tags, unique_tags=unique_tags,
                           question_tags=question_tags, is_flag_tag=is_flag_tag)


@app.route('/question/<question_id>/new-tag', methods=['POST'])
def tag_a_question(question_id):
    if "submit_button" in request.form:
        flag = True
        tag_name = request.form['tag']
    if "submit_button_2" in request.form:
        flag = False
        tag_name = request.form['question_tag']
    question_id = int(question_id)
    new_tag = {"name": tag_name}
    if flag == True:
        data_manager.add_to_database("add_new_tag", new_tag)
    tag_id_list = data_manager.find_id_of_a_tag(tag_name)
    tag_id = tag_id_list[0]
    new_tag_to_a_question = {'question_id': question_id, 'tag_id': tag_id}
    data_manager.add_to_database("add_tag_to_question", new_tag_to_a_question)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/tag/<tag_id>/delete endpoint')
def delete_tag(question_id, tag_id):
    question_id = int(question_id)
    tag_id = int(tag_id)
    data_manager.delete_tag(question_id, tag_id)
    return redirect(f'/question/{question_id}')


@app.route('/registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        user_email = request.form['user_email']
        check_data = data_manager.return_account_data(user_email.lower())
        user_password = request.form['user_password']
        hashed_and_salted_password, user_salt = data_manager.hash_and_salt_password(user_password)
        if check_data == None:
            register_date = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            new_user = {"username": user_email, "password": hashed_and_salted_password, "register_date": register_date}
            data_manager.add_to_database("add_user", new_user)
            user_id = find_question_id_by_answer_id.find_user_id(user_email)
            new_user_personal = {"user_id": user_id, "salt": str(user_salt), "hash": hashed_and_salted_password}
            data_manager.add_to_database("add_user_personal_info", new_user_personal)
            return render_template('register_passed.html')
        else:
            return render_template('register_failed.html')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user_email = request.form['user_email']
        check_data = data_manager.return_account_data(user_email.lower())
        user_password = request.form['user_password']
        if check_data == None:
            return render_template('login_failed.html')
        else:
            user_id = check_data[0]
            check_personal_info = data_manager.return_personal_account_data(user_id)
            salt = check_personal_info[2]
            hashed_password = check_personal_info[3]
            authorization = data_manager.check_password(user_password, salt, hashed_password)
            if authorization:
                session["user_id"] = check_data[0]
                session["user_email"] = check_data[1]
                return render_template('login_passed.html')
    return render_template('login_failed.html')


@app.route('/sign-out', methods=['GET', 'POST'])
def sign_out():
    if request.method == 'GET':
        session.pop("user_id", default=None)
        session.pop("user_email", default=None)
        return render_template('sign_out.html')


@app.route('/comment/<comment_id>/edit', methods=["GET"])
def display_edit_comment(comment_id):
    comments = data_manager.import_data_list("comment")
    questions = data_manager.import_data_list("question")
    id_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["id"]
    title_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["title"]
    message_question_index = data_manager.SORTING_DICT["question"]["categories_indexes"]["message"]
    question_id = find_question_id_by_answer_id.find_question_id_by_comment(comment_id)
    if question_id is None:
        answer_id = find_question_id_by_answer_id.find_answer_id_by_comment(comment_id)
        question_id = find_question_id_by_answer_id.find_question_id(answer_id)

    answer_id = find_question_id_by_answer_id.find_answer_id_by_comment(comment_id)
    return render_template("edit_page_comment.html", comments=comments, comment_id=int(comment_id),
                           question_id=question_id, answer_id=answer_id,
                           questions=questions, id_question_index=id_question_index,
                           title_question_index=title_question_index,
                           message_question_index=message_question_index)


@app.route('/comment/<comment_id>/edit', methods=["POST"])
def edit_comment(comment_id):
    answer_id = None
    submission_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    message = request.form["edited_comment"]
    edited_count = find_question_id_by_answer_id.find_edited_count(comment_id)
    if edited_count is None:
        edited_count = 1
    else:
        edited_count += 1
    question_id = find_question_id_by_answer_id.find_question_id_by_comment(comment_id)
    if question_id is None:
        question_id = 0
    question_id = int(question_id)
    edited_comment = {"question_id": question_id, "answer_id": answer_id, "message": message,
                      "submission_time": submission_time, "edited_count": edited_count}
    data_manager.edit_line("comment", int(comment_id), edited_comment)
    return redirect(f'/question/{question_id}')


@app.route('/comment/<comment_id>/delete_endpoint')
def delete_a_comment(comment_id):
    question_id = find_question_id_by_answer_id.find_question_id_by_comment(comment_id)
    if question_id is None:
        answer_id = find_question_id_by_answer_id.find_answer_id_by_comment(comment_id)
        question_id = find_question_id_by_answer_id.find_question_id(answer_id)
    data_manager.delete_line("comment", comment_id)
    return redirect(f'/question/{question_id}')


if __name__ == "__main__":
    app.run(port=8000)

