import json
import random
from typing import Callable, Optional, List
from uuid import uuid1, UUID
from enum import Enum
from datetime import datetime, date, timedelta
from rapidfuzz import fuzz


class Task:
    _id: UUID
    _title: str
    _description: str
    _category: str
    _due_date: date
    _priority: str
    _is_completed: bool

    def __init__(
            self,
            title: str,
            description: str,
            category: str,
            due_date: date,
            priority: str,
            is_completed: bool = False
    ):
        self._id = uuid1()
        self._title = title
        self._description = description
        self._category = category
        self._due_date = due_date
        self._priority = priority
        self._is_completed = is_completed

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def category(self):
        return self._category

    @property
    def due_date(self):
        return self._due_date

    @property
    def priority(self):
        return self._priority

    @property
    def is_completed(self):
        return self._is_completed

    def update(self, **kwargs):
        for key, value in kwargs.items():
            private_key = f"_{key}"
            if private_key in self.__dict__:
                expected_type = self.__annotations__.get(private_key)
                if isinstance(value, expected_type):
                    setattr(self, private_key, value)
                elif isinstance(value, Enum) and isinstance(value.value, expected_type):
                    setattr(self, private_key, value.value)
                elif value is None:
                    continue
                else:
                    raise TypeError(f"Field '{key}' must be of type {expected_type.__name__}.")
            else:
                raise AttributeError(f"'{key}' is not a valid field of Task.")

    def __str__(self):
        title_width = 20
        description_width = 30
        category_width = 10
        priority_width = 10
        date_width = 12
        status_width = 10

        title = self.title[:title_width].ljust(title_width)
        description = self.description[:description_width].ljust(description_width)
        try:
            category = self.category.value[:category_width].ljust(category_width)
        except:
            category = self.category[:category_width].ljust(category_width)

        try:
            priority = self.priority.value[:priority_width].ljust(priority_width)
        except:
            priority = self.priority[:priority_width].ljust(priority_width)

        due_date = str(self.due_date)[:date_width].ljust(date_width)
        status = 'Готово' if self.is_completed else 'Не готова'
        status = status[:status_width].ljust(status_width)

        return f"{title}|{description}|{category}|{priority}|{due_date}|{status}"


class TaskManager:
    def __init__(self):
        self.__tasks_dict = {}

    def create_task(
            self,
            title: str,
            description: str,
            category: str,
            due_date: date,
            priority: str,
            is_completed: bool = False
    ):
        task = Task(title, description, category, due_date, priority, is_completed)
        self.__tasks_dict[task.id] = task
        return task

    def update_task(self, id, **kwargs):
        task = self.__tasks_dict[id]
        task.update(**kwargs)
        return task

    def delete_task(self, id: UUID):
        return self.__tasks_dict.pop(id)

    def delete_tasks_in_category(self, category: str):
        removed = []
        for id, task in self.__tasks_dict.items():
            if task.category == category:
                removed.append(self.__tasks_dict.pop(id))
        return removed

    def get_tasks(self, tasks_filter: Optional[Callable[[Task], bool]] = None):
        if tasks_filter:
            return list(filter(tasks_filter, self.__tasks_dict.values()))
        return list(self.__tasks_dict.values())

    def search(
            self,
            is_completed: Optional[List[bool]] = None,
            keyword: Optional[str] = None,
            category: Optional[List[str]] = None,
    ):
        results = []
        for task in self.__tasks_dict.values():
            if keyword and not (
                    fuzz.partial_ratio(keyword.lower(), task.title.lower()) > 80 or
                    fuzz.partial_ratio(keyword.lower(), task.description.lower()) > 80 or
                    keyword.lower() in task.title.lower() or
                    keyword.lower() in task.description.lower()
            ):
                continue
            if category and task.category not in category:
                continue
            if is_completed and task.is_completed not in is_completed:
                continue
            results.append(task)
        return results

    def save(self, filepath):
        tasks_data = []
        for task in self.__tasks_dict.values():
            task_data = {
                'id': str(task.id),
                'title': task.title,
                'description': task.description,
                'category': task.category if not isinstance(task.category, Enum) else task.category.value,
                'due_date': task.due_date.strftime('%Y-%m-%d'),
                'priority': task.priority if not isinstance(task.category, Enum) else task.priority.value,
                'is_completed': task.is_completed
            }
            tasks_data.append(task_data)

        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(tasks_data, file, ensure_ascii=False, indent=4)

    def load(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            tasks_data = json.load(file)

        for task_data in tasks_data:
            task = Task(
                title=task_data['title'],
                description=task_data['description'],
                category=Categories(task_data['category']),
                due_date=datetime.strptime(task_data['due_date'], '%Y-%m-%d').date(),
                priority=Priority(task_data['priority']),
                is_completed=task_data['is_completed']
            )
            self.__tasks_dict[task.id] = task


class Categories(Enum):
    STUDY = 'Учеба'
    WORK = 'Работа'
    PERSONAL = 'Личное'


class Priority(Enum):
    LOW = 'Низкий'
    MEDIUM = 'Средний'
    HIGH = 'Высокий'


def fill_tasks(mgr: TaskManager):
    for i in range(15):
        mgr.create_task(
            title=f'Название {i}',
            description=f'Описание {i}',
            category=random.choice([Categories.WORK, Categories.STUDY, Categories.PERSONAL]),
            due_date=datetime.now() + timedelta(days=random.randint(1, 15)),
            priority=random.choice([Priority.LOW, Priority.MEDIUM, Priority.HIGH]),
            is_completed=bool(random.randint(0, 2))
        )


if __name__ == '__main__':
    manager = TaskManager()
    fill_tasks(manager)
    manager.save('test.json')

    new_manager = TaskManager()
    new_manager.load('test.json')

    for t in new_manager.get_tasks():
        print(t)
