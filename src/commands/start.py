from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .forms import Form
from db.db_requests.new_user import add_new_user


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.main_st)
    add_new_user_in_db(message.from_user.id)
    await message.answer(f'Добро пожаловать!\nЭто бот для отслеживания тендеров по заданным сценариям\nДля добавления нового сценария отправьте /add_script')


@router.message(Form.main_st)
async def main(message: Message, state: FSMContext):
    await message.answer('Некорректный запрос')


def add_new_user_in_db(user_id):
    add_new_user(user_id)
