from aiogram.dispatcher.filters.state import StatesGroup, State


class UserRegisterState(StatesGroup):
    faculty = State()
    direction = State()
    course = State()
