import random
import os
import string
from task import Task
import click


tasks = {}


this_dir = os.path.abspath(os.path.dirname(__file__))
text_fullpath = os.path.join(this_dir, "../../tasks.txt")


def generate_unique_id():
    id = ''.join(random.choices(string.ascii_letters + string.digits, k=2))
    if id in tasks:
        generate_unique_id()
    return id


def read_in_tasks():
    task_file = open(text_fullpath, 'r')
    lines = task_file.readlines()
    for line in lines:
        if line != '\n':
            parts = line.split(',')
            task = Task(parts[0], parts[1], parts[2], parts[3].replace('\n', ''))
            tasks.update({task.get_id(): task})
    task_file.close()


def save_to_file():
    task_file = open(text_fullpath, 'w')
    task_file.truncate(0)
    for key, value in tasks.items():
        task_file.write(f'{value.get_id()},{value.get_name()},{value.get_due_date()},{value.get_category()}\n')
    task_file.close()


@click.group()
def cli():
    read_in_tasks()


@cli.command()
def list():
    if not tasks:
        click.echo('\n')
        click.echo('Nothing to do!')
        click.echo('\n')
    else:
        task_list = []
        for key, value in tasks.items():
            task_list.append(value)
        task_list.sort(key=lambda r: r.category)
        current_category = task_list[0].get_category()
        click.echo('\n')
        click.echo(f'---- {current_category} ----'.upper())
        for t in task_list:
            if t.get_category() == current_category:
                click.echo(t.to_string())
            else:
                click.echo('\n')
                current_category = t.get_category()
                click.echo(f'---- {current_category} ----'.upper())
                click.echo(t.to_string())
        click.echo('\n')


@cli.command()
def remove():
    id = click.prompt('Id of task to remove', type=str)
    if id in tasks:
        tasks.pop(id)
        save_to_file()
    else:
        click.echo(f'No task with id: {id}')


@cli.command()
def add():
    id = generate_unique_id()
    name = click.prompt('Name', type=str)
    category = click.prompt('Category', type=str)
    due_date = click.prompt('Due date', type=str)
    task = Task(id, name, due_date, category)
    tasks.update({id: task})
    save_to_file()

@cli.command()
def update():
    id = click.prompt('Id of task to edit', type=str)
    if id not in tasks:
        click.echo(f'No task with id: {id}')
    else:
        task = tasks.get(id)
        new_name = click.prompt('Name', type=str)
        new_category = click.prompt('Category', type=str)
        new_due_date = click.prompt('Due date', type=str)
        task.update_task(new_name, new_due_date, new_category)
        save_to_file()



