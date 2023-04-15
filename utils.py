from aiogram.dispatcher.filters.state import StatesGroup, State


class UserRegisterState(StatesGroup):
    faculty = State()
    direction = State()
    course = State()


class UploadFileState(StatesGroup):
    startUploadFile = State()


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
