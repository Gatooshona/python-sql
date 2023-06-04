import psycopg2

my_pass = ''


def drop_table(conn):
    with conn.cursor() as cur:
        cur.execute('''
            DROP TABLE phones;        
            DROP TABLE clients;
            ''')


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clients(
            client_id SERIAL PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT);
            ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS phones(
            client_id INTEGER NOT NULL REFERENCES clients(client_id),                   
            phone_number VARCHAR(11) UNIQUE);
            ''')

        conn.commit()


def new_client(conn, client_first_name: str, client_last_name: str, client_email: str, phone=None):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO clients(first_name, last_name, email) VALUES
            (%s, %s, %s) RETURNING client_id;
        ''', (client_first_name, client_last_name, client_email))
        client_id = cur.fetchone()[0]

        if phone:
            cur.execute('''
                INSERT INTO phones VALUES (%s, %s);
            ''', (client_id, phone))


def add_phone(conn, client_id, phone: str):
    with conn.cursor() as cur:
        cur.execute('''
            INSERT INTO phones VALUES (%s, %s);
        ''', (client_id, phone))


def change_phone(conn, old_phone: str, new_phone: str):
    with conn.cursor() as cur:
        cur.execute('''
            UPDATE phones SET phone_number=%s WHERE phone_number=%s RETURNING phone_number;
        ''', (new_phone, old_phone))
        current_phone = cur.fetchone()

        if current_phone:
            print('Номер телефона изменен')
        else:
            print('Номер телефона не найден')


def change_client(conn, client_id, **data):
    with conn.cursor() as cur:
        for key, arg in data.items():
            if arg:
                sql = 'UPDATE clients SET {}=%s WHERE client_id=%s'.format(key)
                cur.execute(sql, (arg, client_id, ))
        conn.commit()


def delete_phone(conn, phone_number: str):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE FROM phones WHERE phone_number=%s RETURNING phone_number;
        ''', (phone_number, ))
        current_phone = cur.fetchone()
        if current_phone:
            print('Номер телефона удален')
        else:
            print('Такого номера не существует')


def delete_client(conn, client_id: int):
    with conn.cursor() as cur:
        cur.execute('''
            DELETE from phones WHERE client_id=%s;
        ''', (client_id,))
        cur.execute('''
            DELETE from clients WHERE client_id=%s;
        ''', (client_id, ))


def find_client(conn, first_name=None, last_name=None, email=None, phone_number=None):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT c.client_id, first_name, last_name, email, phone_number FROM clients c
            LEFT JOIN phones p ON p.client_id = c.client_id
            WHERE first_name=%s AND last_name=%s AND email=%s OR phone_number=%s;
        ''', (first_name, last_name, email, phone_number))
        print(cur.fetchall())


def main():
    while True:
        command = input('Введите команду: ').lower()
        if command == "drop_table":
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                drop_table(conn)
                print('Таблицы удалены')

        elif command == "create_db":
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                create_db(conn)
                print('Базы данных созданы')

        elif command == "new_client":
            client_first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите адрес электронной почты: ')
            client_phone = input('Введите номер телефона: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                new_client(conn, client_first_name, last_name, email, client_phone)
                print('Новый клиент добавлен')

        elif command == "add_phone":
            client_id = input('Введите id клиента: ')
            client_phone = input('Введите номер телефона: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                add_phone(conn, client_id, client_phone)
                print('Телефон добавлен')

        elif command == "change_client":
            input_id = int(input('Введите id клиента: '))
            input_last_name = input('Введите новую фамилию: ')
            input_email = input('Введите новый адрес электронной почты: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                change_client(conn, client_id=input_id, last_name=input_last_name, email=input_email)
                print('Данные о клиенте изменены')

        elif command == "change_phone":
            old_phone = input('Введите старый номер телефона: ')
            new_phone = input('Введите новый номер телефона: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                change_phone(conn, old_phone=old_phone, new_phone=new_phone)

        elif command == "delete_phone":
            client_phone = input('Введите номер телефона, который хотите удалить: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                delete_phone(conn, client_phone)

        elif command == "delete_client":
            client_id = int(input('Введите id клиента: '))
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                delete_client(conn, client_id)
                print('Клиент удален')

        elif command == "find_client":
            client_first_name = input('Введите имя: ')
            last_name = input('Введите фамилию: ')
            email = input('Введите адрес электронной почты: ')
            client_phone = input('Введите номер телефона: ')
            with psycopg2.connect(database='netology', user='postgres', password=my_pass) as conn:
                find_client(conn, client_first_name, last_name, email, client_phone)

        elif command == "q":
            print('')
            break
        else:
            print('Неверно введена команда')


main()
