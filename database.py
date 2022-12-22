import psycopg2
import json

f = open('env.json')
config = json.load(f)
f.close()
DBNAME = config["DBNAME"]
USER = config["USER"]

conn = psycopg2.connect(f"dbname={DBNAME} user={USER}")
cur = conn.cursor()

# cur.close()
# conn.close()

# user ---------------------------

def insert_user(user_id, username):
    try:
        cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username,))
    except psycopg2.Error as e:
        print("Error", e)
        return
    conn.commit()


def update_user_data(faculty, direction, course, user_id):
    try:
        cur.execute("UPDATE users SET faculty = %s, direction = %s, course = %s WHERE user_id = %s", (faculty, direction, course, user_id,))
    except psycopg2.Error as e:
        print("Error", e)
    conn.commit()


def get_user_by_id(user_id):
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


def get_user_by_username(username):
    try:
        cur.execute("SELECT * FROM users WHERE username = %s and faculty != -1 and direction != -1 and course != -1", (username,))
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


def get_all_users():
    try:
        cur.execute("SELECT user_id FROM users")
    except psycopg2.Error as e:
        print("Error", e)
    records = cur.fetchall()
    return records


# files -----------------------------

def insert_file(filename, user_id, course, subject):
    try:
        cur.execute("INSERT INTO files (filename, owner, course, subject) VALUES (%s, %s, %s, %s)", (filename, user_id, course, subject,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def get_files_by_user(user_id, course, subject):
    try:
        cur.execute("SELECT * FROM files WHERE owner = %s and course = %s and subject = %s", (user_id, course, subject))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_by_file_id(file_id):
    try:
        cur.execute("SELECT * FROM files WHERE file_id = %s", (file_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_waiting_for_admin():
    try:
        cur.execute("SELECT * FROM files WHERE admin_check = false")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def change_file_admin_status(file_id, status):
    try:
        cur.execute("UPDATE files SET admin_check = %s WHERE file_id = %s", (status, file_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def get_files_by_faculty(faculty, direction, course, subject):
    try:
        cur.execute("SELECT * FROM files WHERE owner IN (SELECT user_id FROM users WHERE faculty=%s AND direction=%s) AND course=%s AND subject=%s", (faculty, direction, course, subject,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_by_name(name):
    try:
        cur.execute(f"SELECT * FROM files WHERE filename LIKE '%{name}%'")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records



# subjects -----------------------------

def get_subjects():
    try:
        cur.execute("SELECT * FROM subjects")
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def get_files_in_profile_page(user_id):
    try:
        cur.execute("SELECT * FROM files WHERE owner = %s and admin_check = true", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records

# session -------------------------

def create_new_session(user_id, command):
    try:
        cur.execute("INSERT INTO session (user_id, command) VALUES (%s, %s)", (user_id, command,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def update_session(user_id, command):
    try:
        cur.execute("UPDATE session set command = command || %s where user_id = %s", (command, user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()


def get_session(user_id):
    try:
        cur.execute("SELECT * FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    records = cur.fetchall()
    return records


def delete_session(user_id):
    try:
        cur.execute("DELETE FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.Error as e:
        print(e)
        pass
    conn.commit()
