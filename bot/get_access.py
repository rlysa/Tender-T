from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from db.db_models.loader import change_access
from config import ADMIN


router = Router()


@router.message(Command('get_access'))
async def cmd_get_access(message: Message, state: FSMContext):
    await message.answer(f'Ваша заявка отправлена администратору. Ожидайте!')
    bot = message.bot
    await bot.send_message(ADMIN, f'Запрос доступа к сценариям от пользователя: @{message.from_user.username}',
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [
                                       InlineKeyboardButton(text='Одобрить', callback_data=f'approve_access_{message.from_user.id}'),
                                       InlineKeyboardButton(text='Отклонить', callback_data=f'reject_access_{message.from_user.id}')
                                   ]
                               ]
                           )
                           )


@router.callback_query(lambda c: c.data.startswith(('approve_access', 'reject_access')))
async def handle_admin_decision_access(callback: CallbackQuery):
    action, what, user_id = callback.data.split('_')
    user_id = int(user_id)
    username = callback.message.text.split('@')[1].split(' ')[0]
    bot = callback.message.bot
    if action == 'approve':
        await callback.message.edit_text(f'Запрос доступа пользователя @{username} одобрен', reply_markup=None)
        change_access_in_db(user_id)
        await bot.send_message(user_id, text='Запрос доступа одобрен')
    else:
        await bot.send_message(user_id, text='Запрос доступа отклонен администратором')
        await callback.message.edit_text(f'Запрос доступа пользователя @{username} отклонен', reply_markup=None)
    await callback.answer()


def change_access_in_db(user_id):
    change_access(user_id)
