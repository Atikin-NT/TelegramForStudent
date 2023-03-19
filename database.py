import logging

import psycopg2
import json


with open('env.json', 'r') as file:
    config = json.load(file)

DBNAME = config["DBNAME"]
USER = config["USER"]

# conn = psycopg2.connect(f"dbname={DBNAME} user={USER}")
# cur = conn.cursor()

# cur.close()
# conn.close()


class DataBase:
    def __init__(self):
        self.conn = psycopg2.connect(f"dbname={DBNAME} user={USER}")
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    # user ---------------------------
    def insert_user(self,
                    user_id: int,
                    username: str):
        """
        :param user_id: id в телеграме
        :param username: username в телеграме
        :return:
        """
        try:
            self.cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username,))
        except psycopg2.Error as e:
            logging.error(e)
            return
        self.conn.commit()
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
        try:
            self.cur.execute("UPDATE users SET faculty = %s, direction = %s, course = %s WHERE user_id = %s", (faculty, direction, course, user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return
        self.conn.commit()
    def get_user_by_id(self, user_id: int) -> list:
        """
        Получить пользователя по id телеграма
        :param user_id: id в телеграме
        :return: список пользователей
        """
        try:
            self.cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_user_by_username(self, username: str) -> list:
        """
        Пользователь по username
        :param username:
        :return: список пользователей
        """
        try:
            self.cur.execute("SELECT * FROM users WHERE username = %s and faculty != -1 and direction != -1 and course != -1", (username,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_all_users(self) -> list:
        """
        Получить список всех пользователей
        :return:
        """
        try:
            self.cur.execute("SELECT user_id FROM users")
        except psycopg2.Error as e:
            logging.error(e)
        records = self.cur.fetchall()
        return records
    # files -----------------------------
    def insert_file(self,
                    filename: str,
                    user_id: int,
                    course: int,
                    subject: int,
                    direction: int) -> int:
        """
        :param filename: имя файла
        :param user_id: id в телеграме
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: Если произошла ошибка в запросах, то ответ будет -2. В случае успеха вернется -1, иначе id файла с
        таким же именем
        """
        try:
            self.cur.execute("SELECT file_id, filename FROM files WHERE owner = %s", (user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return -2
        records = self.cur.fetchall()
        for i in range(len(records)):
            if filename == records[i][1]:
                return records[i][0]

        try:
            self.cur.execute("INSERT INTO files (filename, owner, course, subject, direction_id) VALUES (%s, %s, %s, %s, %s)", (filename, user_id, course, subject, direction,))
        except psycopg2.Error as e:
            logging.error(e)
            return -2
        self.conn.commit()
        return -1
    def get_files_by_user(self,
                          user_id: int,
                          course: int,
                          subject: int,
                          direction: int) -> list:
        """
        Получить файл по id пользователя в телеграме
        :param user_id: id в телеграме
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: список файлов
        """
        try:
            self.cur.execute("SELECT * FROM files WHERE owner = %s and course = %s and subject = %s and direction_id = %s", (user_id, course, subject))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_files_by_file_id(self, file_id: int) -> list:
        """
        Получить файл по id в БД
        :param file_id: id файла
        :return: список фалов
        """
        try:
            self.cur.execute("SELECT * FROM files WHERE file_id = %s", (file_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_files_waiting_for_admin(self) -> list:
        """
        Список фалов, ожидающих одобрения
        :return:
        """
        try:
            self.cur.execute("SELECT * FROM files WHERE admin_check = false")
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def change_file_admin_status(self,
                                 file_id: int,
                                 status: bool):
        """
        Поменять статус файла "проверено/непроверено админом"
        :param file_id: id файла в БД
        :param status: true-проверено, false-нет
        :return:
        """
        try:
            self.cur.execute("UPDATE files SET admin_check = %s WHERE file_id = %s", (status, file_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return
        self.conn.commit()
    def get_files_by_faculty(self,
                             faculty: int,
                             course: int,
                             subject: int,
                             direction: int) -> list:
        """
        Список предметов по направлению
        :param faculty: id факультета
        :param course: курс обучения
        :param subject: id предмета
        :param direction: id направления
        :return: список предметов
        """
        try:
            self.cur.execute("SELECT * FROM files WHERE course=%s AND subject=%s AND direction_id=%s", (course, subject, direction))
        except psycopg2.Error as e:
            logging.error(e)
            pass
        records = self.cur.fetchall()
        return records
    def get_files_by_name(self, name: str) -> list:
        """
        Получить файл по имени
        :param name: имя файла
        :return: список файлов
        """
        name = "".join(c for c in name if c.isalnum())
        try:
            self.cur.execute(f"SELECT * FROM files WHERE filename LIKE '%{name}%'")
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_files_in_profile_page(self, user_id: int) -> list:
        """
        Получить список файлов конкретного пользователя
        :param user_id: id в телеграме
        :return: список файлов
        """
        try:
            self.cur.execute("SELECT * FROM files WHERE owner = %s and admin_check = true", (user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def delete_file_by_file_id(self, file_id: int):
        """
        Удалить файл по id файла в БД
        :param file_id: id файла
        :return:
        """
        try:
            self.cur.execute("DELETE FROM files WHERE file_id = %s", (file_id,))
        except psycopg2.Error as e:
            print(e)
            pass
        self.conn.commit()
    # subjects -----------------------------
    def get_subjects(self,
                     course: int,
                     direction: int) -> list:
        """
        Получить список предметов по направлению и курсу
        :param course: курс обучения
        :param direction: id направения
        :return: список предметов
        """
        try:
            self.cur.execute("SELECT * FROM subjects WHERE sub_id = ANY (SELECT unnest(sublist) FROM subconnection WHERE course = %s AND direction_id = %s)", (course, direction,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    # session -------------------------
    def create_new_session(self,
                           user_id: int,
                           command: str):
        """
        :param user_id: id в телеграме
        :param command: команда
        :return:
        """
        try:
            self.cur.execute("INSERT INTO session (user_id, command) VALUES (%s, %s)", (user_id, command,))
        except psycopg2.Error as e:
            logging.error(e)
            return
        self.conn.commit()
    def update_session(self,
                       user_id: int,
                       command: str):
        """
        Добавляет к существующей сессии
        :param user_id: id в телеграме
        :param command: команда
        :return:
        """
        try:
            self.cur.execute("UPDATE session set command = command || %s where user_id = %s", (command, user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return
        self.conn.commit()
    def get_session(self, user_id: int) -> list:
        """
        Получить сессию по id в телеграме
        :param user_id: id в телеграме
        :return: спиок сессии
        """
        try:
            self.cur.execute("SELECT * FROM session WHERE user_id = %s", (user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def delete_session(self, user_id: int):
        """
        Удалить сессию по id в телеграме
        :param user_id: id в телеграме
        :return:
        """
        try:
            self.cur.execute("DELETE FROM session WHERE user_id = %s", (user_id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        self.conn.commit()
    # direction ----------------
    def get_all_directions(self) -> list:
        """
        Получить список всех направлений
        :return:
        """
        try:
            self.cur.execute("SELECT * FROM direction")
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records
    def get_direction_by_id(self, id: int) -> list:
        """
        Получить направление по id в БД
        :param id: id в БД
        :return: список направления
        """
        try:
            self.cur.execute("SELECT * FROM directions WHERE direction_id = %s", (id,))
        except psycopg2.Error as e:
            logging.error(e)
            return []
        records = self.cur.fetchall()
        return records


db = DataBase()
