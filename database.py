import psycopg2
import json


with open('env.json', 'r') as file:
    config = json.load(file)

DBNAME = config["DBNAME"]
USER = config["USER"]

conn = psycopg2.connect(f"dbname={DBNAME} user={USER} password=postgres")
cur = conn.cursor()

# cur.close()
# conn.close()


# user ---------------------------

def insert_user(user_id: int,
                username: str):
    """
    :param user_id: id в телеграме
    :param username: username в телеграме
    :return:
    """
    try:
        cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username,))
    except psycopg2.Error as e:
        print("Error", e)
        return
    conn.commit()


def update_user_data(faculty: int,
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
        cur.execute("UPDATE users SET faculty = %s, direction = %s, course = %s WHERE user_id = %s", (faculty, direction, course, user_id,))
    except psycopg2.Error as e:
        print("Error", e)
    conn.commit()


def get_user_by_id(user_id: int) -> list:
    """
    Получить пользователя по id телеграма
    :param user_id: id в телеграме
    :return: список пользователей
    """
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


def get_user_by_username(username: str) -> list:
    """
    Пользователь по username
    :param username:
    :return: список пользователей
    """
    try:
        cur.execute("SELECT * FROM users WHERE username = %s and faculty != -1 and direction != -1 and course != -1", (username,))
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


def get_all_users() -> list:
    """
    Получить список всех пользователей
    :return:
    """
    try:
        cur.execute("SELECT user_id FROM users")
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


# files -----------------------------

def insert_file(filename: str,
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
    :return: В случае успеха вернется -1, иначе id файла с таким же именем
    """
    try:
        cur.execute("SELECT file_id, filename FROM files WHERE owner = %s", (user_id,))
    except psycopg2.Error as e:
        print(e)
    records = cur.fetchall()
    for i in range(len(records)):
        if filename == records[i][1]:
            return records[i][0]

    try:
        cur.execute("INSERT INTO files (filename, owner, course, subject, direction_id) VALUES (%s, %s, %s, %s, %s)", (filename, user_id, course, subject, direction,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()
    return -1


def get_files_by_user(user_id: int,
                      course: int,
                      subject: int,
                      direction: int) -> list:
    """
    получить файл по id пользователя в телеграме
    :param user_id: id в телеграме
    :param course: курс обучения
    :param subject: id предмета
    :param direction: id направления
    :return: список файлов
    """
    try:
        cur.execute("SELECT * FROM files WHERE owner = %s and course = %s and subject = %s and direction_id = %s", (user_id, course, subject))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_by_file_id(file_id: int) -> list:
    """
    получить файл по id в БД
    :param file_id: id файла
    :return: список фалов
    """
    try:
        cur.execute("SELECT * FROM files WHERE file_id = %s", (file_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_waiting_for_admin() -> list:
    """
    Список фалов, ожидающих одобрения
    :return:
    """
    try:
        cur.execute("SELECT * FROM files WHERE admin_check = false")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def change_file_admin_status(file_id: int,
                             status: bool):
    """
    Поменять статус файла "проверено/непроверено админом"
    :param file_id: id файла в БД
    :param status: true-проверено, false-нет
    :return:
    """
    try:
        cur.execute("UPDATE files SET admin_check = %s WHERE file_id = %s", (status, file_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def get_files_by_faculty(faculty: int,
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
        # cur.execute("SELECT * FROM files WHERE owner IN (SELECT user_id FROM users WHERE faculty=%s AND direction=%s) AND course=%s AND subject=%s", (faculty, direction, course, subject,))
        cur.execute("SELECT * FROM files WHERE course=%s AND subject=%s AND direction_id=%s", (course, subject, direction))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_by_name(name: str) -> list:
    """
    Получить файл по имени
    :param name: имя файла
    :return: список файлов
    """
    name = "".join(c for c in name if c.isalnum())
    try:
        cur.execute(f"SELECT * FROM files WHERE filename LIKE '%{name}%'")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_in_profile_page(user_id: int) -> list:
    """
    Получить список файлов конкретного пользователя
    :param user_id: id в телеграме
    :return: список файлов
    """
    try:
        cur.execute("SELECT * FROM files WHERE owner = %s and admin_check = true", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def delete_file_by_file_id(file_id: int):
    """
    удалить файл по id файла в БД
    :param file_id: id файла
    :return:
    """
    try:
        cur.execute("DELETE FROM files WHERE file_id = %s", (file_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


# subjects -----------------------------

def get_subjects(course: int,
                 direction: int) -> list:
    """
    Получить список предметов по направлению и курсу
    :param course: курс обучения
    :param direction: id направения
    :return: список предметов
    """
    try:
        cur.execute("SELECT * FROM subjects WHERE sub_id = ANY (SELECT unnest(sublist) FROM subconnection WHERE course = %s AND direction_id = %s)", (course, direction,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    print(records)
    return records


# session -------------------------

def create_new_session(user_id: int,
                       command: str):
    """

    :param user_id: id в телеграме
    :param command: команда
    :return:
    """
    try:
        cur.execute("INSERT INTO session (user_id, command) VALUES (%s, %s)", (user_id, command,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def update_session(user_id: int,
                   command: str):
    """
    Добавляет к существующей сессии
    :param user_id: id в телеграме
    :param command: команда
    :return:
    """
    try:
        cur.execute("UPDATE session set command = command || %s where user_id = %s", (command, user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def get_session(user_id: int) -> list:
    """
    получить сессию по id в телеграме
    :param user_id: id в телеграме
    :return: спиок сессии
    """
    try:
        cur.execute("SELECT * FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def delete_session(user_id: int):
    """
    Удалить сессию по id в телеграме
    :param user_id: id в телеграме
    :return:
    """
    try:
        cur.execute("DELETE FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()

# direction ----------------


def get_all_directions() -> list:
    """
    Получить список всех направлений
    :return:
    """
    try:
        cur.execute("SELECT * FROM direction")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_direction_by_id(id: int) -> list:
    """
    Получить направление по id в БД
    :param id: id в БД
    :return: список направления
    """
    try:
        cur.execute("SELECT * FROM directions WHERE direction_id = %s", (id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records
