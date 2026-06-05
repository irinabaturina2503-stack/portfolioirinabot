import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# ======================
# CONFIG — всё из .env
# ======================

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@username")
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set!")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set!")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
# NOTE: MemoryStorage — состояния хранятся в памяти.
# Для продакшена заменить на RedisStorage (одна строка).


# ======================
# STATES
# ======================

class CalcState(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()


class CustomState(StatesGroup):
    waiting_text = State()


# ======================
# HELPERS
# ======================

def fmt_username(user: types.User) -> str:
    """FIX 4: username может быть None."""
    return f"@{user.username}" if user.username else "нет username"


async def notify_admin(text: str) -> None:
    """FIX 3 (из прошлой версии): ошибка отправки не роняет бота."""
    try:
        await bot.send_message(ADMIN_ID, text)
    except Exception as e:
        logging.error("Не удалось отправить сообщение админу: %s", e)


def yes_no_kb(yes_cb: str, no_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=yes_cb),
            InlineKeyboardButton(text="Нет", callback_data=no_cb),
        ]
    ])


# ======================
# KEYBOARDS
# ======================

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Возможности", callback_data="features")],
        [InlineKeyboardButton(text="💼 Решения", callback_data="services")],
        [InlineKeyboardButton(text="🧮 Расчёт", callback_data="calc")],
        [InlineKeyboardButton(text="✍️ Свой проект", callback_data="custom")],
        [InlineKeyboardButton(
            text="👤 Написать",
            url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"
        )],
        [InlineKeyboardButton(text="📞 Оставить номер", callback_data="phone")],
    ])


def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# ======================
# START
# ======================

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "💼 Telegram-решения для бизнеса\n\n"
        "Я создаю ботов, которые:\n"
        "• продают\n"
        "• принимают заявки\n"
        "• автоматизируют процессы\n"
        "• заменяют менеджеров\n\n"
        f"📞 {ADMIN_PHONE}\n"
        f"👤 {ADMIN_USERNAME}\n\n"
        "Выберите раздел 👇"
    )
    await message.answer(text, reply_markup=main_menu())


# ======================
# MENU
# ======================

# FIX 2: state.clear() внутри back — пользователь не застрянет в FSM
@dp.callback_query(F.data == "back")
async def back_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("💼 Главное меню", reply_markup=main_menu())
    await call.answer()


@dp.callback_query(F.data == "features")
async def features(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Запись", callback_data="demo_booking")],
        [InlineKeyboardButton(text="🛍 Продажи", callback_data="demo_sales")],
        [InlineKeyboardButton(text="📊 CRM", callback_data="demo_crm")],
        [InlineKeyboardButton(text="💬 Рассылки", callback_data="demo_msg")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])
    await call.message.edit_text("🚀 Возможности\n\nВыберите демо:", reply_markup=kb)
    await call.answer()


# ======================
# DEMO
# ======================

@dp.callback_query(F.data == "demo_crm")
async def demo_crm(call: types.CallbackQuery):
    text = (
        "📊 CRM демо\n\n"
        "━━━━━━━━━━━━\n"
        "👤 Иван Петров\n"
        "🔥 статус: горячий\n"
        "💰 потенциал: 30 000 ₽\n"
        "━━━━━━━━━━━━"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Новый клиент", callback_data="noop")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="features")],
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data == "demo_sales")
async def demo_sales(call: types.CallbackQuery):
    text = "🛍 Демо-магазин\n\nТовар: Худи\nЦена: 3 500 ₽"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", callback_data="noop")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="features")],
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data == "demo_booking")
async def demo_booking(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="12 июня", callback_data="noop")],
        [InlineKeyboardButton(text="13 июня", callback_data="noop")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="features")],
    ])
    await call.message.edit_text("📅 Выберите дату:", reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data == "demo_msg")
async def demo_msg(call: types.CallbackQuery):
    await call.message.edit_text(
        "💬 Рассылки\n\nАвтоматическая отправка сообщений клиентам",
        reply_markup=back_kb()
    )
    await call.answer()


@dp.callback_query(F.data == "noop")
async def noop(call: types.CallbackQuery):
    await call.answer("Это демо-режим 😊", show_alert=False)


# ======================
# SERVICES
# ======================

@dp.callback_query(F.data == "services")
async def services(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Визитка (от 10k)", callback_data="s1")],
        [InlineKeyboardButton(text="💰 Продажи (от 25k)", callback_data="s2")],
        [InlineKeyboardButton(text="💬 Поддержка (от 20k)", callback_data="s3")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])
    await call.message.edit_text("💼 Решения\n\nВыберите пакет:", reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data == "s1")
async def s1(call: types.CallbackQuery):
    await call.message.edit_text(
        "🤖 Бот-визитка\n\n✔ услуги\n✔ контакты\n✔ навигация\n\n💰 от 10 000 ₽",
        reply_markup=back_kb()
    )
    await call.answer()


@dp.callback_query(F.data == "s2")
async def s2(call: types.CallbackQuery):
    await call.message.edit_text(
        "💰 Система продаж\n\n✔ заявки\n✔ каталог\n✔ CRM\n\n💰 от 25 000 ₽",
        reply_markup=back_kb()
    )
    await call.answer()


@dp.callback_query(F.data == "s3")
async def s3(call: types.CallbackQuery):
    await call.message.edit_text(
        "💬 Поддержка\n\n✔ ответы 24/7\n✔ маршрутизация заявок\n\n💰 от 20 000 ₽",
        reply_markup=back_kb()
    )
    await call.answer()


# ======================
# CALC — FSM
# ======================

@dp.callback_query(F.data == "calc")
async def calc_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_data({"score": 0})
    await state.set_state(CalcState.q1)
    await call.message.edit_text(
        "🧮 Нужны продажи через бот?",
        reply_markup=yes_no_kb("calc_q1_yes", "calc_q1_no")
    )
    await call.answer()


@dp.callback_query(CalcState.q1, F.data.in_({"calc_q1_yes", "calc_q1_no"}))
async def calc_q1(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data["score"] + (1 if call.data == "calc_q1_yes" else 0)
    await state.set_data({"score": score})
    await state.set_state(CalcState.q2)
    await call.message.edit_text(
        "📅 Нужна запись клиентов?",
        reply_markup=yes_no_kb("calc_q2_yes", "calc_q2_no")
    )
    await call.answer()


@dp.callback_query(CalcState.q2, F.data.in_({"calc_q2_yes", "calc_q2_no"}))
async def calc_q2(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data["score"] + (1 if call.data == "calc_q2_yes" else 0)
    await state.set_data({"score": score})
    await state.set_state(CalcState.q3)
    await call.message.edit_text(
        "📊 Нужна CRM?",
        reply_markup=yes_no_kb("calc_q3_yes", "calc_q3_no")
    )
    await call.answer()


@dp.callback_query(CalcState.q3, F.data.in_({"calc_q3_yes", "calc_q3_no"}))
async def calc_q3(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data["score"] + (2 if call.data == "calc_q3_yes" else 0)
    await state.clear()

    if score <= 1:
        price = "от 5 000 ₽"
    elif score <= 3:
        price = "от 15 000 ₽"
    else:
        price = "от 30 000 ₽"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="👤 Написать мне",
            url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"
        )],
        [InlineKeyboardButton(text="📞 Оставить номер", callback_data="phone")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back")],
    ])
    await call.message.edit_text(
        f"🧮 Результат расчёта\n\n💰 {price}\n\nДля точной оценки напишите мне 👇",
        reply_markup=kb
    )
    await call.answer()


# ======================
# CUSTOM PROJECT — FSM
# ======================

@dp.callback_query(F.data == "custom")
async def custom(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(CustomState.waiting_text)
    await call.message.edit_text(
        "✍️ Опишите ваш проект своими словами.\n\nЯ получу сообщение и отвечу вам лично.",
        reply_markup=back_kb()
    )
    await call.answer()


# FIX 3: проверяем что message.text не None и не команда
@dp.message(CustomState.waiting_text)
async def catch_custom_text(message: types.Message, state: FSMContext):
    # Игнорируем команды и пустой текст (фото, стикеры и т.д.)
    if not message.text or message.text.startswith("/"):
        await message.answer("Пожалуйста, напишите описание проекта текстом.")
        return

    await state.clear()
    await notify_admin(
        f"🔔 НОВАЯ ЗАЯВКА\n\n"
        f"👤 {message.from_user.full_name}\n"
        f"{fmt_username(message.from_user)}\n"   # FIX 4
        f"ID: {message.from_user.id}\n\n"
        f"📩 Описание:\n{message.text}"
    )
    await message.answer(
        "Спасибо! Сообщение отправлено, я свяжусь с вами 👌",
        reply_markup=main_menu()
    )


# ======================
# PHONE
# ======================

@dp.callback_query(F.data == "phone")
async def phone(call: types.CallbackQuery):
    await call.message.answer(
        "Отправьте ваш номер телефона:",
        reply_markup=contact_kb()
    )
    await call.answer()


@dp.message(F.contact)
async def contact(message: types.Message):
    await notify_admin(
        f"📞 НОВЫЙ КОНТАКТ\n\n"
        f"👤 {message.from_user.full_name}\n"
        f"{fmt_username(message.from_user)}\n"   # FIX 4
        f"ID: {message.from_user.id}\n\n"
        f"📱 Телефон: {message.contact.phone_number}"
    )
    await message.answer("Спасибо! Я свяжусь с вами 👌", reply_markup=main_menu())


# ======================
# RUN
# ======================

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
