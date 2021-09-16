import os
import string
import click
from task import Task
from datetime import datetime
from itertools import permutations


this_dir = os.path.abspath(os.path.dirname(__file__))
text_fullpath = os.path.join(this_dir, "../../tasks.txt")


def string_to_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d').date()


def read_in_tasks():
    task_file = open(text_fullpath, 'r')
    lines = task_file.readlines()
    tasks = []
    for line in lines:
        if line != '\n':
            parts = line.split(',')
            task = Task(parts[0], parts[1], string_to_date(parts[2]), parts[3].replace('\n', ''))
            tasks.append(task)
    task_file.close()
    return tasks


def save_to_file(tasks):
    task_file = open(text_fullpath, 'w')
    task_file.truncate(0)
    for t in tasks:
        task_file.write(f'{t.get_id()},{t.get_name()},{t.get_due_date()},{t.get_category().upper()}\n')
    task_file.close()


def days_till_due(date):
    days = date - datetime.today().date()
    return days.days


def is_valid_date(date):
    try:
        valid_date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return False


def echo_with_color(task_info, days):
    if days == 0:
        click.echo(f'{task_info}' + click.style(' (due today)', fg='yellow'))
    elif days < 0:
        click.echo(f'{task_info}' + click.style(f' (overdue by {abs(days)} days)', fg='red'))
    else:
        click.echo(f'{task_info}' + click.style(f' ({days} days)', fg='green'))


class Tasks:

    def __init__(self):
        self.tasks = read_in_tasks()

    def append_task(self, task):
        self.tasks.append_task(task)

    def sort_by_date(self):
        self.tasks.sort(key=lambda x: x.due_date)
        return self.tasks

    def sort_by_category_then_date(self):
        self.tasks.sort(key=lambda x: (x.category, x.due_date))
        return self.tasks

    def get_tasks(self):
        return self.tasks

    def generate_unique_id(self):
        allowed_chars = string.ascii_lowercase + string.digits
        l = ["".join(i) for i in permutations(allowed_chars, 2)]
        used_ids = [t.id for t in self.tasks]
        for id in l:
            if id not in used_ids:
                return id
        raise ValueError(f"All {len(l)} unique ids have been used!")

    def is_empty(self):
        if not self.tasks:
            return True
        return False


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = Tasks()


@cli.command(help='List tasks grouped by category.')
@click.pass_context
def list(ctx):
    if ctx.obj.is_empty():
        click.echo('\nNothing to do!\n')
    else:
        sorted_tasks = ctx.obj.sort_by_category_then_date()
        current_category = sorted_tasks[0].get_category()
        click.echo(f'\n---- {current_category} ----'.upper())
        for t in sorted_tasks:
            days = days_till_due(t.get_due_date())
            if t.get_category() == current_category:
                echo_with_color(t.to_string(), days)
            else:
                current_category = t.get_category()
                click.echo(f'\n---- {current_category} ----'.upper())
                echo_with_color(t.to_string(), days)
        click.echo('\n')


@cli.command(help='List tasks as one group.')
@click.pass_context
def lag(ctx):
    click.echo('\n')
    click.echo('---- ALL TASKS ----')
    sorted_tasks = ctx.obj.sort_by_date()
    for t in sorted_tasks:
        days = days_till_due(t.get_due_date())
        echo_with_color(t.to_string_with_category(), days)
    click.echo('\n')


@cli.command(help='Remove a task.')
@click.pass_context
def delete(ctx):
    id = click.prompt('Id of task to delete (Q to exit)', type=str)
    if id == 'Q':
        return
    tasks = ctx.obj.get_tasks()
    for target_task in tasks:
        if target_task.get_id() == id:
            if click.confirm(f'Delete task: {target_task.to_string_with_category()}?'):
                tasks.remove(target_task)
                save_to_file(tasks)
                click.echo('Task deleted.')
                return
            else:
                click.echo('Delete canceled.')
                return
    click.echo(f'No task with id: {id}')


@cli.command(help='Create a new task.')
@click.pass_context
def new(ctx):
    tasks = ctx.obj.get_tasks()
    id = ctx.obj.generate_unique_id()
    name = click.prompt('Name', type=str)
    category = click.prompt('Category', type=str)
    due_date = click.prompt('Due date (yyyy-mm-dd)', type=str)
    if is_valid_date(due_date) == False:
        click.echo('Task creation aborted.')
        click.echo('Invalid date. Check format matches: yyyy-mm-dd or yyyy-m-d.')
        return
    task = Task(id, name, string_to_date(due_date), category)
    tasks.append(task)
    save_to_file(tasks)
    click.echo('Task created.')


@cli.command(help='Edit a task.')
@click.pass_context
def update(ctx):
    tasks = ctx.obj.get_tasks()
    id = click.prompt('Id of task to update', type=str)
    for target_task in tasks:
        if target_task.get_id() == id:
            new_name = click.prompt('Name', type=str)
            new_category = click.prompt('Category', type=str)
            new_due_date = click.prompt('Due date (yyyy-mm-dd)', type=str)
            if is_valid_date(new_due_date) == False:
                click.echo('Update aborted.')
                click.echo('Invalid date. Check format matches: yyyy-mm-dd or yyyy-m-d.')
                return
            target_task.update_task(new_name, new_due_date, new_category)
            save_to_file(tasks)
            click.echo('Task updated.')
            return
    click.echo(f'No task with id: {id}')
