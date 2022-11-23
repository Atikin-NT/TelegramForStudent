import psycopg2


# user ---------------------------

def insert_user(user_id, username):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (user_id, username) VALUES (%s, %s)", (user_id, username,))
    except psycopg2.IntegrityError as e:
        pass
        # if e.pgcode == "23505":
        #     send_start_menu(user_id)
        # else:
        #     send_message(user_id, "Unknown error")
    conn.commit()
    cur.close()
    conn.close()


def update_user_data(faculty, direction, course, user_id):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET faculty = %s, direction = %s, course = %s WHERE user_id = %s", (faculty, direction, course, user_id,))
    except psycopg2.IntegrityError as e:
        print(e)
    conn.commit()
    cur.close()
    conn.close()


def get_user(user_id):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    except psycopg2.IntegrityError as e:
        pass
        # if e.pgcode == "23505":
        #     send_start_menu(user_id)
        # else:
        #     send_message(user_id, "Unknown error")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records


def find_user(username):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    except psycopg2.IntegrityError as e:
        pass
        # if e.pgcode == "23505":
        #     send_start_menu(user_id)
        # else:
        #     send_message(user_id, "Unknown error")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records


def get_files_by_user(user_id, course, subject):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM files WHERE owner = %s and course = %s and subject = %s", (user_id, course, subject))
    except psycopg2.IntegrityError as e:
        pass
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records


def get_subjects():
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM subjects")
    except psycopg2.IntegrityError as e:
        pass
    records = cur.fetchall()
    cur.close()
    conn.close()
    return records


# session -------------------------

def create_new_session(user_id, command):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO session (user_id, command) VALUES (%s, %s)", (user_id, command,))
    except psycopg2.IntegrityError as e:
        pass
    conn.commit()
    cur.close()
    conn.close()


def update_session(user_id, command):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("UPDATE session set command = command || %s where user_id = %s", (command, user_id,))
    except psycopg2.IntegrityError as e:
        pass
    conn.commit()
    cur.close()
    conn.close()


def get_session(user_id):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.IntegrityError as e:
        pass
    records = cur.fetchall()
    cur.close()
    conn.close()
    print(records)
    return records


def delete_session(user_id):
    conn = psycopg2.connect("dbname=mydb user=atikin")
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM session WHERE user_id = %s", (user_id,))
    except psycopg2.IntegrityError as e:
        pass
    conn.commit()
    cur.close()
    conn.close()
