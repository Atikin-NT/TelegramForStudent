import logging
import psycopg2
import psycopg2.extras
import json 
import os


class DataBase:
    def __init__(self, dbname, user, password=None):
        self.conn = psycopg2.connect(f"dbname={dbname} user={user} password={password}")
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def __del__(self):
        self.cur.close()
        self.conn.close()
    def _execute(self, command: str) -> list | None:
        try:
            self.cur.execute(command)
            records = self.cur.fetchall()
            if len(records) == 0:
                return None
            return records
        except psycopg2.Error as e:
            logging.warning(e)
        self.conn.commit()
        return None

    # user ---------------------------
    def insert_user(self,
                    user_id: int,
                    username: str):
        """
        :param user_id: id в телеграме
        :param username: username в телеграме
        :return:
        """
        statement = f"INSERT INTO users (user_id, username) VALUES ({user_id}, '{username}')"
        self._execute(statement)
    def update_user_data(self,
                         faculty: int,
                         direction: int,
                         course: int,
                         user_id: int):
        """
        :param faculty: id факультета
        :param direction: id направления
        :param course: курс обучения
        :param user_id: id в телеграме
        :return:
        """
        statement = f"UPDATE users SET faculty = {faculty}, direction = {direction}, course = {course} WHERE user_id = {user_id}"
        self._execute(statement)
    def get_user_by_id(self, user_id: int) -> list | None:
        """
        Получить пользователя по id телеграма

        :param user_id: id в телеграме
        :return: список пользователей или None, если произошла ошибка или пользователь не найден
        """
        statement = f"SELECT * FROM users WHERE user_id = {user_id}"
        return self._execute(statement)
    def get_user_by_username(self, username: str) -> list | None:
        """
        Пользователь по username

        :param username:
        :return: список пользователей или None, если произошла ошибка или пользователь не найден
        """
        statement = f"SELECT * FROM users WHERE username = {username} and faculty != -1 and direction != -1 and course != -1"
        return self._execute(statement)
    def get_all_users(self) -> list | None:
        """
        Получить список всех пользователей

        :return: список пользователей или None, если произошла ошибка или пользовательей нет
        """
        statement = "SELECT user_id FROM users"
        return self._execute(statement)
    # files -----------------------------
    def insert_file(self,
                    filename: str,
                    user_id: int,
                    course: int,
                    subject: int,
                    direction: int) -> int | None:
        """
        :param filename: имя файла
        :param user_id: id в телеграме
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: Если найден файл с таким же названием, то вернется id этого файла из нашел базы, иначе - None
        """
        statement = f"SELECT file_id, filename FROM files WHERE owner = {user_id}"
        owner_files = self._execute(statement)
        if owner_files is not None:
            for i in range(len(owner_files)):
                if filename == owner_files[i][1]:
                    return owner_files[i][0]

        statement = f"INSERT INTO files (filename, owner, course, subject, direction_id) VALUES ('{filename}', " \
                    f"{user_id}, {course}, {subject}, {direction})"
        res = self._execute(statement)
    def get_files_by_user(self,
                          user_id: int,
                          course: int,
                          subject: int,
                          direction: int) -> list | None:
        """
        Получить файл по id пользователя в телеграме

        :param user_id: id в телеграме
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: список файлов или None, если произошла ошибка или файла нет
        """
        statement = f"SELECT * FROM files WHERE owner = {user_id} and course = {course} and subject = {subject}"
        return self._execute(statement)
    def get_files_by_file_id(self, file_id: int) -> list | None:
        """
        Получить файл по id в БД

        :param file_id: id файла
        :return: список фалов или None, если произошла ошибка или файла нет
        """
        statement = f"SELECT * FROM files WHERE file_id = {file_id}"
        return self._execute(statement)
    def get_files_waiting_for_admin(self) -> list | None:
        """
        Список фалов, ожидающих одобрения

        :return: список фалов или None, если произошла ошибка или файла нет
        """
        statement = "SELECT * FROM files WHERE admin_check = false"
        return self._execute(statement)
    def change_file_admin_status(self,
                                 file_id: int,
                                 status: bool):
        """
        Поменять статус файла "проверено/непроверено админом"

        :param file_id: id файла в БД
        :param status: true-проверено, false-нет
        :return:
        """
        statement = f"UPDATE files SET admin_check = {status} WHERE file_id = {file_id}"
        self._execute(statement)
    def get_files_by_faculty(self,
                             faculty: int,
                             course: int,
                             subject: int,
                             direction: int) -> list | None:
        """
        Список предметов по направлению

        :param faculty: id факультета
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: список предметов или None, если произошла ошибка или файлов не найдено
        """
        statement = f"SELECT * FROM files WHERE course={course} AND subject={subject} AND direction_id={direction}"
        return self._execute(statement)
    def get_files_by_name(self, name: str) -> list | None:
        """
        Получить файл по имени

        :param name: имя файла
        :return: список файлов или None, если произошла ошибка или файлов не найдено
        """
        name = "".join(c for c in name if c.isalnum())
        statement = f"SELECT * FROM files WHERE filename LIKE '%{name}%'"
        return self._execute(statement)
    def get_files_in_profile_page(self, user_id: int) -> list | None:
        """
        Получить список файлов конкретного пользователя

        :param user_id: id в телеграме
        :return: список файлов или None, если произошла ошибка или файлов не найдено
        """
        statement = f"SELECT * FROM files WHERE owner = {user_id} and admin_check = true"
        return self._execute(statement)
    def delete_file_by_file_id(self, file_id: int):
        """
        Удалить файл по id файла в БД

        :param file_id: id файла
        :return:
        """
        statement = f"DELETE FROM files WHERE file_id = {file_id}"
        self._execute(statement)
    # subjects -----------------------------
    def get_subjects(self,
                     course: int,
                     direction: int) -> list | None:
        """
        Получить список предметов по направлению и курсу

        :param course: курс обучения
        :param direction: id направения
        :return: список предметов или None, если произошла ошибка или предметов не найдено
        """
        statement = f"SELECT * FROM subjects WHERE sub_id = ANY (SELECT unnest(sublist) FROM subconnection WHERE " \
                    f"course = {course} AND direction_id = {direction})"
        return self._execute(statement)
    # session -------------------------
    def create_new_session(self,
                           user_id: int,
                           command: str):
        """
        :param user_id: id в телеграме
        :param command: команда
        :return:
        """
        statement = f"INSERT INTO session (user_id, command) VALUES ({user_id}, {command})"
        self._execute(statement)
    def update_session(self,
                       user_id: int,
                       command: str):
        """
        Добавляет к существующей сессии

        :param user_id: id в телеграме
        :param command: команда
        :return:
        """
        statement = f"UPDATE session set command = command || '{command}' where user_id = {user_id}"
        self._execute(statement)
    def get_session(self, user_id: int) -> list | None:
        """
        Получить сессию по id в телеграме

        :param user_id: id в телеграме
        :return: спиок сессии или None, если произошла ошибка или сессия не найдена
        """
        statement = f"SELECT * FROM session WHERE user_id = {user_id}"
        return self._execute(statement)
    def delete_session(self, user_id: int):
        """
        Удалить сессию по id в телеграме

        :param user_id: id в телеграме
        :return:
        """
        statement = f"DELETE FROM session WHERE user_id = {user_id}"
        self._execute(statement)
    # direction ----------------
    def get_all_directions(self) -> list | None:
        """
        Получить список всех направлений

        :return: список направлений или None, если произошла ошибка или направлений не найдена
        """
        statement = "SELECT * FROM direction"
        return self._execute(statement)
    def get_direction_by_id(self, id: int) -> list | None:
        """
        Получить направление по id в БД
        
        :param id: id в БД
        :return: список направления или None, если произошла ошибка или направления не найдена
        """
        statement = f"SELECT * FROM directions WHERE direction_id = {id}"
        return self._execute(statement)

    def update_download_counter(self, file_id):
        statement = f"UPDATE files SET download_counter = download_counter + 1 WHERE file_id = {file_id}"
        self._execute(statement)


directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "env.json")
with open(new_path, 'r') as file:
    config = json.load(file)

DBNAME = config["DBNAME"]
USER = config["USER"]
PASSWORD = config["PASSWORD"]

db = DataBase(DBNAME, USER, PASSWORD)
