from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .forms import Form


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.main_st)
    await message.answer(f'Добро пожаловать!\nЭто бот для отслеживания тендеров по заданным сценариям\nДля добавления сценария отправьте /add_scenario')


@router.message(Form.main_st)
async def main(message: Message, state: FSMContext):
    await message.answer('Некорректный запрос')
