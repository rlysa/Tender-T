from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from db.db_models.db_connector import get_admins, get_users_with_access
from db.db_models.loader import change_access


router = Router()

messages_id = {}


@router.message(Command('get_access'))
async def cmd_get_access(message: Message):
    if message.from_user.id in get_users_with_access():
        await message.answer(f'У вас уже есть доступ')
        return
    await message.answer(f'Ваша заявка отправлена администратору. Ожидайте!')
    bot = message.bot
    for admin in get_admins():
        msg = await bot.send_message(admin, f'Запрос доступа к сценариям от пользователя: @{message.from_user.username}',
                               reply_markup=InlineKeyboardMarkup(
                                   inline_keyboard=[
                                       [
                                           InlineKeyboardButton(text='Одобрить', callback_data=f'approve_access_{message.from_user.id}'),
                                           InlineKeyboardButton(text='Отклонить', callback_data=f'reject_access_{message.from_user.id}')
                                       ]
                                   ]
                               )
                               )
        messages_id[admin] = msg.message_id


@router.callback_query(lambda c: c.data.startswith(('approve_access', 'reject_access')))
async def handle_admin_decision_access(callback: CallbackQuery):
    action, what, user_id = callback.data.split('_')
    user_id = int(user_id)
    username = callback.message.text.split('@')[1].split(' ')[0]
    bot = callback.message.bot
    if action == 'approve':
        for admin in get_admins():
            await bot.edit_message_text(
                chat_id=admin,
                message_id=messages_id[admin],
                text=f'Запрос доступа пользователя @{username} одобрен',
                reply_markup=None
            )
        change_access_in_db(user_id)
        await bot.send_message(user_id, text='Запрос доступа одобрен')
    else:
        await bot.send_message(user_id, text='Запрос доступа отклонен администратором')
        for admin in get_admins():
            await bot.edit_message_text(
                chat_id=admin,
                message_id=messages_id[admin],
                text=f'Запрос доступа пользователя @{username} отклонен',
                reply_markup=None
            )
    await callback.answer()


def change_access_in_db(user_id):
    change_access(user_id)
