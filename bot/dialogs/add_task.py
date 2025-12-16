from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Column, Select
from aiogram_dialog.widgets.text import Const, Format

from bot.api_client import BackendClient
from bot.dateparse import parse_user_datetime
from bot.settings import get_settings


class AddTaskSG(StatesGroup):
    title = State()
    description = State()
    category = State()
    due_at = State()
    confirm = State()


@dataclass(frozen=True)
class CategoryItem:
    id: str
    name: str


def _client() -> BackendClient:
    """Args: none. Returns: backend client."""
    s = get_settings()
    return BackendClient(base_url=s["BACKEND_BASE_URL"])


async def _get_categories(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    """Args: dialog_manager, _. Returns: data for window."""
    if dialog_manager.event.from_user is None:
        return {"categories": []}
    tg_id = dialog_manager.event.from_user.id
    categories = await _client().list_categories(tg_id)
    items = [CategoryItem(id=c.id, name=c.name) for c in categories]
    return {"categories": items}


async def _on_title(message: Message, widget: Any, manager: DialogManager, value: str) -> None:
    """Args: message, widget, manager, value. Returns: None."""
    manager.dialog_data["title"] = value.strip()
    await manager.next()


async def _on_description(message: Message, widget: Any, manager: DialogManager, value: str) -> None:
    """Args: message, widget, manager, value. Returns: None."""
    raw = value.strip()
    manager.dialog_data["description"] = "" if raw == "-" else raw
    await manager.next()


async def _on_category_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
) -> None:
    """Args: callback, widget, manager, item_id. Returns: None."""
    manager.dialog_data["category_id"] = item_id
    await manager.next()


async def _on_no_category(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    """Args: callback, button, manager. Returns: None."""
    manager.dialog_data["category_id"] = None
    await manager.next()


async def _on_due_at(message: Message, widget: Any, manager: DialogManager, value: str) -> None:
    """Args: message, widget, manager, value. Returns: None."""
    parsed = parse_user_datetime(value)
    if parsed.error:
        await message.answer(parsed.error)
        return

    if parsed.value is None:
        manager.dialog_data["due_at"] = None
    else:
        manager.dialog_data["due_at"] = parsed.value

    await manager.next()


async def _confirm_data(dialog_manager: DialogManager, **_: Any) -> dict[str, Any]:
    """Args: dialog_manager, _. Returns: data for confirm window."""
    title = str(dialog_manager.dialog_data.get("title") or "")
    description = str(dialog_manager.dialog_data.get("description") or "")
    category_id = dialog_manager.dialog_data.get("category_id")
    due_at_raw = dialog_manager.dialog_data.get("due_at")
    due_at = due_at_raw if isinstance(due_at_raw, datetime) else None

    category_name = "без категории"
    if isinstance(category_id, str):
        if dialog_manager.event.from_user is not None:
            cats = await _client().list_categories(dialog_manager.event.from_user.id)
        else:
            cats = []
        for c in cats:
            if c.id == category_id:
                category_name = c.name
                break

    due_text = "-"
    if due_at is not None:
        due_text = str(due_at)

    return {
        "title": title,
        "description": description,
        "category_name": category_name,
        "due": due_text,
    }


async def _on_create(callback: CallbackQuery, button: Button, manager: DialogManager) -> None:
    """Args: callback, button, manager. Returns: None."""
    if callback.from_user is None:
        return
    tg_id = callback.from_user.id

    title = str(manager.dialog_data.get("title") or "")
    description = str(manager.dialog_data.get("description") or "")
    category_id = manager.dialog_data.get("category_id")
    due_at_raw = manager.dialog_data.get("due_at")
    due_at = due_at_raw if isinstance(due_at_raw, datetime) else None

    created = await _client().create_task(
        telegram_id=tg_id,
        title=title,
        description=description,
        category_id=(category_id if isinstance(category_id, str) else None),
        due_at_utc=due_at,
    )

    text = (
        f"Создана задача: {created.title}\n"
        f"Категория: {created.category_name or '-'}\n"
        f"Создано: {created.created_at}\n"
        f"Дедлайн: {created.due_at or '-'}"
    )

    if isinstance(callback.message, Message):
        await callback.message.answer(text)
    await manager.done()


add_task_dialog = Dialog(
    Window(
        Const("Введите заголовок задачи:"),
        TextInput(id="title", on_success=_on_title),
        Cancel(Const("Отмена")),
        state=AddTaskSG.title,
    ),
    Window(
        Const("Введите описание (или '-' чтобы пропустить):"),
        TextInput(id="desc", on_success=_on_description),
        Cancel(Const("Отмена")),
        state=AddTaskSG.description,
    ),
    Window(
        Const("Выберите категорию:"),
        Column(
            Select(
                Format("{item.name}"),
                id="cat",
                items="categories",
                item_id_getter=lambda item: item.id,
                on_click=_on_category_selected,
            ),
        ),
        Button(Const("Без категории"), id="no_cat", on_click=_on_no_category),
        Cancel(Const("Отмена")),
        getter=_get_categories,
        state=AddTaskSG.category,
    ),
    Window(
        Const("Введите due_at (YYYY-MM-DD HH:MM) или '-' чтобы пропустить:"),
        TextInput(id="due", on_success=_on_due_at),
        Cancel(Const("Отмена")),
        state=AddTaskSG.due_at,
    ),
    Window(
        Format(
            "Подтвердите создание:\n"
            "Заголовок: {title}\n"
            "Описание: {description}\n"
            "Категория: {category_name}\n"
            "Дедлайн: {due}"
        ),
        Button(Const("Создать"), id="create", on_click=_on_create),
        Cancel(Const("Отмена")),
        getter=_confirm_data,
        state=AddTaskSG.confirm,
    ),
)
