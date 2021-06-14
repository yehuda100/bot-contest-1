from pony.orm import *


db = Database()

class Users(db.Entity):
    id = PrimaryKey(int)
    todos = Set('Todo')


class Todo(db.Entity):
    id = PrimaryKey(int, auto=True)
    task = Optional(str)
    done = Required(int, size=8)
    user = Required(Users)


@db_session
def is_new_user(id):
    return not Users.exists(id=id)

@db_session
def add_user(id):
    Users(id=id)

@db_session
def add_task(id, task, done=0):
    Todo(task=task, user=id, done=done)

@db_session
def tasks_exists(id, status):
    return Todo.exists(lambda t: t.user.id == id and t.done in status)

@db_session
def task_list(id, status, page=1):
    result = select(t for t in Todo if t.user.id == id and t.done in status)[(page-1)*10:page*10]
    tasks = []
    for t in result:
        tasks.append([t.id, t.done, t.task])
    return tasks

@db_session
def task_count(id, status):
    return count(t for t in Todo if t.done in status)

@db_session
def get_task(id):
    return get((t.task, t.done) for t in Todo if t.id == id)

@db_session
def change_status(id, done):
    Todo[id].set(done=done)

@db_session
def delete(id):
    Todo[id].delete()

@db_session
def edit_task(id, task):
    Todo[id].set(task=task)









db.bind(provider='sqlite', filename='database.db', create_db=True)
db.generate_mapping(create_tables=True)


#by t.me/yehuda100
