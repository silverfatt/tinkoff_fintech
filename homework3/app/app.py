"""Logging Module"""
import logging
import re

import werkzeug.wrappers.response
from flask import Flask, redirect, render_template, request, url_for
from jinja2 import Template


def create_app() -> Flask:
    """
    Creates app
    :return: app
    """
    myapp = Flask(__name__)
    return myapp


logging.basicConfig(
    level=logging.DEBUG, filename='app_log.log', filemode='w', encoding='utf-8'
)
logger = logging.getLogger('logger')

POSTS_PER_PAGE = 10
active_tasks: list[str] = []
completed_tasks: list[str] = []
substrings: list[str] = []
type_of_list = 'active'
checker = ''
found_task = ''
app = create_app()


def change_type_of_list(command: str) -> str:
    """
    Changes type of list on screen
    :param command: command got from user
    :return: requested type of list
    """
    list_type = 'active'
    if command == 'Active':
        list_type = 'active'
    elif command == 'Completed':
        list_type = 'completed'
    elif command == 'Show All':
        list_type = 'all'
    return list_type


@app.route('/change_list', methods=['POST'])
def change_list() -> werkzeug.wrappers.response.Response:
    """
    Requests for changing list
    :return: Response
    """
    global type_of_list
    command = request.form.get('changer')
    type_of_list = change_type_of_list(str(command))
    return redirect(url_for('base'))


def add_element_to_active_tasks(new_todo: str, task_list: list[str]) -> str:
    """
    Adds element to active_tasks list and checks
    if new_todo element is already in list
    :param new_todo: new element
    :param task_list: list of active tasks
    """
    check_str = ''
    if new_todo and not new_todo.isspace():
        if task_list.count(new_todo) > 0:
            check_str = 'Already exists'
        else:
            task_list.append(new_todo)
    return check_str


@app.route('/add', methods=['POST'])
def add() -> werkzeug.wrappers.response.Response:
    """
    Add new task to active_tasks list
    :return: Response
    """
    global checker
    new_todo = request.form.get('task_adder')
    logger.debug('ADDING ELEMENT: %s', new_todo)
    checker = add_element_to_active_tasks(str(new_todo), active_tasks)
    return redirect(url_for('base'))


def search(subs: str, active_tasks: list[str], completed_tasks: list[str]) -> list[str]:
    """
    Searches a task in active_tasks and
    completed_tasks and generates list
    of found tasks
    :param subs: substring
    :param active_tasks: list of active tasks
    :param completed_tasks: list of completed tasks
    :return:
    """
    res_active = ['Active: ' + x for x in active_tasks if re.search(subs, x)]
    res_completed = ['Completed: ' + x for x in completed_tasks if re.search(subs, x)]
    return res_active + res_completed


@app.route('/search_substring', methods=['POST'])
def search_substring() -> werkzeug.wrappers.response.Response:
    """
    Searches a task
    :return: Response
    """
    global substrings
    subs = request.form.get('substring_searcher')
    substrings = search(str(subs), active_tasks, completed_tasks)
    return redirect(url_for('base'))


@app.route('/remove', methods=['POST'])
def remove() -> werkzeug.wrappers.response.Response:
    """
    Removes task from active_tasks and adds to completed_list
    :return: Response
    """
    todo_to_remove = request.form.get('deleter')
    logger.debug("REMOVING ELEMENT: %s", todo_to_remove)
    active_tasks.remove(str(todo_to_remove))
    completed_tasks.append(str(todo_to_remove))
    return redirect(url_for('base'))


@app.route('/clear', methods=['POST'])
def clear() -> werkzeug.wrappers.response.Response:
    """
    Clears completed_tasks list
    :return: Response
    """
    clearlist = request.form.get('cleanup')
    if clearlist == 'Clear':
        completed_tasks.clear()
    return redirect(url_for('base'))


@app.route('/', methods=['GET', 'POST'])
def base() -> str:
    """
    Renders start page
    :return: str
    """
    site = Template(
        render_template(
            'base.html',
            list_of_active_tasks=active_tasks,
            list_of_completed_tasks=completed_tasks,
            checker=checker,
            type_of_list=type_of_list,
            sublist=substrings,
        )
    )
    return site.render()


if __name__ == '__main__':
    app.run(debug=True)
