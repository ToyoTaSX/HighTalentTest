import random
from datetime import timedelta

from classes import *
import curses


# Список объектов
# objects = ["Объект 1", "Объект 2", "Объект 3"]
# selected_objects = []

def fill_tasks(mgr: TaskManager):
    for i in range(10):
        mgr.create_task(
            title=f'Название {i}',
            description=f'Описание {i}',
            category=random.choice([Categories.WORK, Categories.STUDY, Categories.PERSONAL]),
            due_date=datetime.now() + timedelta(days=random.randint(1, 15)),
            priority=random.choice([Priority.LOW, Priority.MEDIUM, Priority.HIGH]),
            is_completed=bool(random.randint(0, 2))
        )


def main_menu(stdscr):
    task_manager = TaskManager()
    task_manager.load('test.json')
    # fill_tasks(task_manager)
    cursor_idx = 0
    curses.start_color()

    curses.curs_set(0)

    up_key = curses.KEY_UP
    down_key = curses.KEY_DOWN
    create_key = '1'
    search_key = '2'
    update_key = '3'
    delete_key = '4'
    next_key = curses.KEY_RIGHT
    prev_key = curses.KEY_LEFT

    page = 0
    selected_tasks = []
    tasks = []
    filters = {
        'category': None,
        'keyword': None,
        'is_completed': None
    }
    while True:
        tasks = task_manager.search(**filters)
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        tasks_on_page_count = height - 5
        # Заголовок
        title = " Главное меню:"
        stdscr.addstr(0, 8, title)

        # Кнопки с подсказкой, активность в зависимости от условий
        stdscr.addstr(1, 2, f"[{create_key}] Создать")
        stdscr.addstr(1, 22, f"[{search_key}] Фильтры {'(исп.)' if any(filters.values()) else ''}")
        stdscr.addstr(1, 36, f"[{update_key}] Посмотреть/Изменить".format(len(selected_tasks) == 1))
        stdscr.addstr(1, 62, f"[{delete_key}] Удалить".format(len(selected_tasks) > 0))
        stdscr.addstr(1, 82, f"[5] Выход")

        # Отображение списка объектов
        left = page * tasks_on_page_count
        right = left + tasks_on_page_count
        tasks_on_page = tasks[left:right]

        if (len(tasks_on_page) > 0):
            stdscr.addstr(3, 0, " Список объектов: (Используйте клавиши ↑↓ для выбора, Enter для выбора элемента) ")
            page_str = \
                (
                    f'Страница {page + 1} / {(len(tasks) // tasks_on_page_count) + 1 - int(not (bool(len(tasks) % tasks_on_page_count)))} '
                    f' товары {left + 1}-{left + len(tasks_on_page)} из {len(tasks)}')
            stdscr.addstr(4, 10, page_str)
        for idx, task in enumerate(tasks_on_page):
            task_str = str(task)[:width - 10]
            start_idx = 2
            if idx == cursor_idx:
                task_str = '>>' + task_str
                start_idx = 0
            if task in selected_tasks:
                stdscr.addstr(5 + idx, start_idx, task_str, curses.A_REVERSE)
            else:
                stdscr.addstr(5 + idx, start_idx, task_str)

        # Обработка событий клавиатуры
        key = stdscr.getch()
        if key == prev_key:
            page = max(0, page - 1)
            cursor_idx = 0
        elif key == next_key:
            page = min((len(tasks) // tasks_on_page_count) - int(not (bool(len(tasks) % tasks_on_page_count))),
                       page + 1)
            cursor_idx = 0
        elif key == up_key and len(tasks) > 0:
            cursor_idx = max(0, cursor_idx - 1)
        elif key == down_key and len(tasks) > 0:
            cursor_idx = min(len(tasks_on_page) - 1, cursor_idx + 1)
        elif len(tasks_on_page) > 0 and key in (curses.KEY_ENTER, 10, 13):
            selected_tasks.append(tasks_on_page[cursor_idx])

        # Обработчики действий кнопок
        if key == ord(create_key):  # Создать
            create_menu(stdscr, task_manager)
        elif key == ord(delete_key) and len(selected_tasks) > 0:  # Удалить
            for task in selected_tasks:
                task_manager.delete_task(task.id)
            selected_tasks = []

        elif key == ord(update_key):  # Изменить
            update_menu(stdscr, tasks_on_page[cursor_idx])

        elif key == ord(search_key):  # Поиск (обновляет список)
            filters = filter_menu(stdscr, filters)

        elif key == ord('5'):
            stdscr.clear()
            break

        stdscr.refresh()

    task_manager.save('tasks.json')


def update_menu(stdscr, old_task):
    categories = [i.value for i in Categories]
    priorities = [i.value for i in Priority]
    stdscr.clear()
    stdscr.addstr(0, 2, "Текущие данные")
    stdscr.addstr(1, 2, "[Enter] - возврат [Space] - изменить")
    stdscr.addstr(2, 2, f"Название: {old_task.title}")
    stdscr.addstr(3, 2, f"Описание: {old_task.description}")
    stdscr.addstr(4, 2, f"Категория: {old_task.category.value}")
    stdscr.addstr(5, 2, f"Дедлайн: {old_task.due_date}")
    stdscr.addstr(6, 2, f"Приоритет: {old_task.priority.value}")
    stdscr.addstr(7, 2, f"Статус: {'Готова' if old_task.is_completed else 'Не готова'}")
    stdscr.refresh()
    key = stdscr.getch()
    if key != ord(' '):
        return

    stdscr.clear()
    title = prompt_string(stdscr, "Название: ", 2, 1)
    stdscr.clear()
    description = prompt_string(stdscr, "Описание: ", 2, 1)
    stdscr.clear()
    category = prompt_choice(stdscr, "Категрия: ", 2, 1, categories)
    stdscr.clear()
    due_date = prompt_date(stdscr, "Дедлайн (ДД/ММ/ГГГГ): ", 2, 1)
    stdscr.clear()
    priority = prompt_choice(stdscr, "Приоритет: ", 2, 1, priorities)
    stdscr.clear()
    status = prompt_checkbox(stdscr, "Статус (Пробел чтобы изменить): ", 2, 1)

    # Вывод всех введенных данных
    stdscr.clear()
    stdscr.addstr(0, 2, "Новые данные")

    stdscr.addstr(2, 2, f"Название: {title}")
    stdscr.addstr(3, 2, f"Описание: {description}")
    stdscr.addstr(4, 2, f"Категория: {category}")
    stdscr.addstr(5, 2, f"Дедлайн: {due_date}")
    stdscr.addstr(6, 2, f"Приоритет: {priority}")
    stdscr.addstr(7, 2, f"Статус: {'Готова' if status else 'Не готова'}")
    stdscr.addstr(8, 2, f"Применить?: (y/n)")

    key = stdscr.getch()
    if key in [ord('y'), ord('Y'), ord('н'), ord('Н')]:
        old_task.update(
            title=title,
            description=description,
            category=Categories(category),
            due_date=due_date,
            priority=Priority(priority),
            is_completed=status
        )


def prompt_string(stdscr, prompt, x, y):
    """Запрос строки у пользователя"""
    stdscr.clear()
    stdscr.addstr(y, x, prompt)
    curses.echo()  # Включаем отображение вводимого текста
    input_str = stdscr.getstr(y, x + len(prompt), 64).decode('utf-8')
    return input_str.strip()


def prompt_choice(stdscr, prompt, x, y, options):
    """Запрос выбора из списка"""
    stdscr.addstr(y, x, prompt)
    selected_idx = 0
    while True:
        for idx, option in enumerate(options):
            if idx == selected_idx:
                stdscr.addstr(y + idx + 1, x, f"> {option}", curses.A_REVERSE)
            else:
                stdscr.addstr(y + idx + 1, x, f"  {option}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(options) - 1:
            selected_idx += 1
        elif key in (curses.KEY_ENTER, 10, 13):  # Enter
            return options[selected_idx]


def prompt_multy_choice(stdscr, prompt, x, y, options):
    curr_idx = 0
    selected = []
    while True:
        stdscr.clear()
        stdscr.addstr(0, 1, 'Enter - подтвердить, Space - выбор')
        stdscr.addstr(y, x, prompt)
        for idx, option in enumerate(options):
            opt_str = f"{option}"
            if idx == curr_idx:
                opt_str = '>>' + opt_str
            if option in selected:
                stdscr.addstr(y + idx + 1, x, opt_str, curses.A_REVERSE)
            else:
                stdscr.addstr(y + idx + 1, x, opt_str)
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            curr_idx = (curr_idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            curr_idx = (curr_idx + 1) % len(options)
        elif key == ord(' '):
            if options[curr_idx] in selected:
                selected.remove(options[curr_idx])
            else:
                selected.append(options[curr_idx])
        elif key in (curses.KEY_ENTER, 10, 13):  # Enter
            return selected if len(selected) > 0 else None


def prompt_date(stdscr, prompt, x, y):
    """Запрос даты в формате DD/MM/YYYY"""
    stdscr.addstr(y, x, prompt)
    curses.echo()
    input_date = stdscr.getstr(y, x + len(prompt), 10).decode('utf-8')
    try:
        return datetime.strptime(input_date, "%d/%m/%Y").date()
    except ValueError:
        return None  # Возвращаем None, если дата введена некорректно


def prompt_checkbox(stdscr, prompt, x, y):
    """Запрос состояния чекбокса (отметить/снять)"""
    is_check = False
    while True:
        stdscr.clear()
        stdscr.addstr(y, x, prompt + f" [{'*' if is_check else ' '}]")
        key = stdscr.getch()
        if key == 10:  # Enter для завершения
            return is_check
        elif key == ord(' '):  # Пробел для переключения состояния
            is_check = not is_check
        stdscr.refresh()


def create_menu(stdscr, task_manager: TaskManager):
    categories = [i.value for i in Categories]
    priorities = [i.value for i in Priority]
    stdscr.clear()
    title = prompt_string(stdscr, "Название: ", 2, 1)
    stdscr.clear()
    description = prompt_string(stdscr, "Описание: ", 2, 1)
    stdscr.clear()
    category = prompt_choice(stdscr, "Категрия: ", 2, 1, categories)
    stdscr.clear()
    due_date = prompt_date(stdscr, "Дедлайн (ДД/ММ/ГГГГ): ", 2, 1)
    stdscr.clear()
    priority = prompt_choice(stdscr, "Приоритет: ", 2, 1, priorities)
    stdscr.clear()
    status = prompt_checkbox(stdscr, "Статус (Пробел чтобы изменить): ", 2, 1)

    # Вывод всех введенных данных
    stdscr.clear()
    stdscr.addstr(1, 2, "Новая задача:")
    stdscr.addstr(1, 2, f"Название: {title}")
    stdscr.addstr(2, 2, f"Описание: {description}")
    stdscr.addstr(3, 2, f"Категория: {category}")
    stdscr.addstr(4, 2, f"Дедлайн: {due_date}")
    stdscr.addstr(5, 2, f"Приоритет: {priority}")
    stdscr.addstr(6, 2, f"Статус: {'Готова' if status else 'Не готова'}")
    stdscr.addstr(8, 2, f"Подтвердить? y/n:")
    stdscr.refresh()

    key = stdscr.getch()
    if key in [ord('y'), ord('Y'), ord('н'), ord('Н')]:
        task_manager.create_task(
            title=title,
            description=description,
            category=category,
            due_date=due_date,
            priority=priority,
            is_completed=status
        )


def filter_menu(stdscr, curr_filters):
    stdscr.clear()
    curr_idx = 0
    result = dict(curr_filters)
    while True:
        stdscr.addstr(0, 1, 'Enter - подтвердить, Space - выбор')
        items = list(result.items())
        for idx, (filter_name, filter_val) in enumerate(items):
            opt_str = f"{filter_name}"
            if idx == curr_idx:
                opt_str = '>>' + opt_str

            if (filter_val and len(filter_val) > 0):
                opt_str += f' (выбрано {len(filter_val)})'
            stdscr.addstr(1 + idx + 1, 1, opt_str)

        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            curr_idx = (curr_idx - 1) % len(items)
        elif key == curses.KEY_DOWN:
            curr_idx = (curr_idx + 1) % len(items)
        elif key == ord(' '):
            fil = items[curr_idx][0]
            if fil == 'category':
                result['category'] = prompt_multy_choice(stdscr, "Категории: ", 2, 1, [i for i in Categories])
            elif fil == 'is_completed':
                result['is_completed'] = prompt_multy_choice(stdscr, "Выполнена?: ", 2, 1, [True, False])
            elif fil == 'keyword':
                result['keyword'] = prompt_string(stdscr, "Ключевые слова: ", 2, 1)

        elif key in (curses.KEY_ENTER, 10, 13):  # Enter
            return result

        stdscr.clear()


# Запуск curses приложения
curses.wrapper(main_menu)
