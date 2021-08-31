class Task:

    def __init__(self, id, name, due_date, category):
        self.id = id
        self.name = name
        self.category = category
        self.due_date = due_date


    def get_id(self):
        return self.id


    def get_name(self):
        return self.name


    def get_category(self):
        return self.category


    def get_due_date(self):
        return self.due_date


    def to_string(self):
        return f'{self.id} - {self.name} - {self.due_date}'


    def update_task(self, new_name, new_due_date, new_category):
        self.name = new_name
        self.due_date = new_due_date
        self.category = new_category