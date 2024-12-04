import pytest
from datetime import datetime, timedelta
from uuid import UUID
from classes import TaskManager, Task, Categories, Priority


@pytest.fixture
def task_manager():
    mgr = TaskManager()
    mgr.create_task(
        title="Test Task 1",
        description="Test Description 1",
        category=Categories.WORK,
        due_date=datetime.now() + timedelta(days=5),
        priority=Priority.HIGH,
        is_completed=False
    )
    return mgr


def test_create_task(task_manager):
    task = task_manager.get_tasks()[0]
    assert len(task_manager.get_tasks()) == 1
    assert isinstance(task.id, UUID)
    assert task.title == "Test Task 1"
    assert task.description == "Test Description 1"
    assert task.category == Categories.WORK
    assert task.priority == Priority.HIGH
    assert not task.is_completed


def test_update_task(task_manager):
    task = task_manager.get_tasks()[0]
    task.update(title="Updated Task", is_completed=True)
    assert task.title == "Updated Task"
    assert task.is_completed


def test_delete_task(task_manager):
    task = task_manager.get_tasks()[0]
    task_manager.delete_task(task.id)
    assert len(task_manager.get_tasks()) == 0


def test_search_task_by_keyword(task_manager):
    task = task_manager.get_tasks()[0]
    results = task_manager.search(keyword="Test")
    assert len(results) == 1
    assert results[0] == task


def test_search_task_by_category(task_manager):
    task = task_manager.get_tasks()[0]
    results = task_manager.search(category=[Categories.WORK])
    assert len(results) == 1
    assert results[0] == task


def test_search_task_by_status(task_manager):
    task = task_manager.get_tasks()[0]
    task_manager.update_task(id=task.id, is_completed=True)
    results = task_manager.search(is_completed=[True])
    assert len(results) == 1
    assert results[0].is_completed


def test_save_load(task_manager):
    task_manager.save('test.json')
    new_mgr = TaskManager()
    new_mgr.load('test.json')
    assert len(new_mgr.get_tasks()) == 1
    task = new_mgr.get_tasks()[0]
    assert task.title == "Test Task 1"
    assert task.description == "Test Description 1"
    assert task.category == Categories.WORK
    assert task.priority == Priority.HIGH
    assert not task.is_completed
