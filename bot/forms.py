from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    start = State()
    main_st = State()
    add_script = State()
    add_script_f1 = State()
    add_script_f2 = State()
