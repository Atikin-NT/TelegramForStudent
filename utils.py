from aiogram.dispatcher.filters.state import StatesGroup, State


class UserRegisterState(StatesGroup):
    """
    Состояние, которое отвечает за регистрацию и изменение данных пользователя
    """
    faculty = State()  # отметка, что мы спросили факультет
    direction = State()  # отметка, что мы спросили направление
    course = State()  # отметка, что мы спросили курс


class UploadFileState(StatesGroup):
    """
    Состояние отвечающее за загрузку файлов
    """
    course = State()  # отметка, что мы спросили курс
    subject = State()  # отметка, что мы спросили предмет
    wait_for_file = State()  # отметка, что пользователь следующим сообщение загрузит файл
    reloadFile = State()  # отметка, что пользователь заменяет файл [НЕ РЕАЛИЗОВАНО]


class UserFileList(StatesGroup):
    """
    Состояние, отвечающее за показ файлов
    """
    showFile = State()  # состояние, что мы показываем файл


class AdminFileListForApprove(StatesGroup):
    """
    Состояние для админов[НЕ ИСПОЛЬЗУЕТСЯ](вроде)
    """
    showFileList = State()


class FindFile(StatesGroup):
    """
    Состояние поиска файла
    """
    startFindFile = State()  # отметка, что мы спросили курс
    askSubject = State()  # отметка, что мы спросили предмет
    showFile = State()  # отметка, что мы хотим показать определенный файл
    currentFile = State()  # отметка, что мы показали определенный файл


class Admin(StatesGroup):
    """
    Состояние для админов
    """
    sendMassiveMessage = State()  # массивная рассылка [НЕ РЕАЛИЗОВАНО]
    deleteFile = State()  # удаление файла [НЕ РЕАЛИЗОВАНО]
