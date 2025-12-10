from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db.db_models.loader import add_new_user
from db.db_models.db_connector import is_new, get_admins
from config import ADMIN_USERNAME


router = Router()

messages_id = {}


@router.message(Command('start'))
async def cmd_start(message: Message):
    if not is_new(message.from_user.id):
        await message.answer(f'Добро пожаловать!\nЭто бот для отслеживания тендеров по заданным сценариям')
        return
    await message.answer(f'Добро пожаловать!\nЭто бот для отслеживания тендеров по заданным сценариям\nВаша заявка отправлена администратору. Ожидайте!')
    bot = message.bot
    for admin in get_admins():
        msg = await bot.send_message(admin, f'Новый пользователь: @{message.from_user.username}',
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(text='Одобрить', callback_data=f'approve_start_{message.from_user.id}'),
                                           InlineKeyboardButton(text='Отклонить', callback_data=f'reject_start_{message.from_user.id}')
                                       ]
                                   ]
                               )
                               )
        messages_id[admin] = msg.message_id



@router.callback_query(lambda c: c.data.startswith(('approve_start', 'reject_start')))
async def handle_admin_decision(callback: CallbackQuery):
    action, what, user_id = callback.data.split('_')
    user_id = int(user_id)
    username = callback.message.text.split('@')[1].split(' ')[0]
    bot = callback.message.bot
    if action == 'approve':
        add_new_user_in_db(user_id)
        for admin in get_admins():
            await bot.edit_message_text(
                chat_id=admin,
                message_id=messages_id[admin],
                text=f'Заявка пользователя @{username} одобрена',
                reply_markup=None
            )
        await bot.send_message(user_id, text='Заявка одобрена')
        await bot.send_message(user_id, text=f'Для получения доступа к сценариям отправьте /get_access')
    else:
        await bot.send_message(user_id, text='Заявка отклонена администратором')
        for admin in get_admins():
            await bot.edit_message_text(
                chat_id=admin,
                message_id=messages_id[admin],
                text=f'Заявка пользователя @{username} отклонена',
                reply_markup=None
            )
    await callback.answer()


def add_new_user_in_db(user_id):
    add_new_user(user_id)


@router.message(Command('help'))
async def cmd_start(message: Message):
    if message.from_user.id in get_admins():
        await message.answer(f'Это бот для отслеживания тендеров по заданным сценариям\n\nКаждые три часа осуществляется поиск по заданному сценарию\n\n/add_script - создание сценария\n/run_scripts - ручной запуск сценариев\n/get_db - получение бд\n\nПо любым вопросом обращаться к @{ADMIN_USERNAME}')
