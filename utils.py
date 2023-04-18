from aiogram.dispatcher.filters.state import StatesGroup, State


class UserRegisterState(StatesGroup):
    faculty = State()
    direction = State()
    course = State()


class UploadFileState(StatesGroup):
    course = State()
    subject = State()
    wait_for_file = State()
    reloadFile = State()


class UserFileList(StatesGroup):
    showFile = State()


class AdminFileListForApprove(StatesGroup):
    showFileList = State()


class FindFile(StatesGroup):
    startFindFile = State()
    askSubject = State()
    showFile = State()
    currentFile = State()


class Admin(StatesGroup):
    sendMassiveMessage = State()
