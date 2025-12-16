import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from aiogram_dialog import DialogManager, StartMode, setup_dialogs

from bot.api_client import BackendClient
from bot.dialogs.add_task import AddTaskSG, add_task_dialog
from bot.settings import get_settings

router = Router()


def _menu_kb() -> ReplyKeyboardMarkup:
    """Args: none. Returns: reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои задачи")],
            [KeyboardButton(text="Добавить задачу")],
        ],
        resize_keyboard=True,
    )


@router.message(Command("start"))
async def start_cmd(message: Message) -> None:
    """Args: message. Returns: None."""
    if message.from_user is None:
        return
    s = get_settings()
    client = BackendClient(base_url=s["BACKEND_BASE_URL"])
    await client.ensure_user(message.from_user.id)
    await message.answer("Готово. Выберите действие.", reply_markup=_menu_kb())


@router.message(lambda m: m.text == "Мои задачи")
async def list_tasks(message: Message) -> None:
    """Args: message. Returns: None."""
    if message.from_user is None:
        return
    s = get_settings()
    client = BackendClient(base_url=s["BACKEND_BASE_URL"])
    tasks = await client.list_tasks(message.from_user.id)

    if not tasks:
        await message.answer("Задач нет.")
        return

    parts: list[str] = []
    for t in tasks[:50]:
        parts.append(
            "\n".join(
                [
                    f"{t.title}",
                    f"Категория: {t.category_name or '-'}",
                    f"Создано: {t.created_at}",
                    f"Дедлайн: {t.due_at or '-'}",
                    f"Статус: {t.status}",
                ]
            )
        )

    await message.answer("\n\n".join(parts))


@router.message(lambda m: m.text == "Добавить задачу")
async def add_task(message: Message, dialog_manager: DialogManager) -> None:
    """Args: message, dialog_manager. Returns: None."""
    await dialog_manager.start(AddTaskSG.title, mode=StartMode.RESET_STACK)


async def main() -> None:
    """Args: none. Returns: None."""
    s = get_settings()
    while not s["BOT_TOKEN"]:
        await asyncio.sleep(5)
        s = get_settings()

    bot = Bot(token=s["BOT_TOKEN"])
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(add_task_dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
