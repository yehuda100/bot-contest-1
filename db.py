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
def is_new_user(id: int):
    return not Users.exists(id=id)

@db_session
def add_user(id: int):
    Users(id=id)

@db_session
def add_task(id: int, task: str, done: int=0) -> None:
    Todo(task=task, user=id, done=done)

@db_session
def tasks_exists(id: int, status: list) -> bool:
    return Todo.exists(lambda t: t.user.id == id and t.done in status)

@db_session
def task_list(id: int, status: list, page: int=1) -> list:
    result = select(t for t in Todo if t.user.id == id and t.done in status)[(page-1)*10:page*10]
    tasks = []
    for t in result:
        tasks.append([t.id, t.done, t.task])
    return tasks

@db_session
def task_count(id: int, status: list) -> int:
    return count(t for t in Todo if t.user.id == id and t.done in status)

@db_session
def get_task(id: int) -> tuple:
    return get((t.task, t.done) for t in Todo if t.id == id)

@db_session
def change_status(id: int, done: int) -> None:
    Todo[id].set(done=done)

@db_session
def delete(id: int) -> None:
    Todo[id].delete()

@db_session
def edit_task(id: int, task: str) -> None:
    Todo[id].set(task=task)


db.bind(provider='sqlite', filename='database.db', create_db=True)
db.generate_mapping(create_tables=True)


#by t.me/yehuda100
