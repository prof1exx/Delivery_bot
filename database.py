import sqlite3
from datetime import datetime

# Создание подключения
connection = sqlite3.connect('delivery.db')
# Переводчик/исполнитель
sql = connection.cursor()

# Создание таблицы для пользователей
sql.execute('CREATE TABLE IF NOT EXISTS users'
            '(tg_id INTEGER, name TEXT, phone_number TEXT, address TEXT, reg_date DATETIME);')

# Создание таблицы для склада
sql.execute('CREATE TABLE IF NOT EXISTS products'
            '(pr_id INTEGER PRIMARY KEY AUTOINCREMENT , pr_name TEXT,'
            'pr_price REAL, pr_quantity INTEGER, pr_des TEXT, pr_photo TEXT, reg_date DATETIME);')

# Создание таблицы для корзины
sql.execute('CREATE TABLE IF NOT EXISTS user_cart'
            '(user_id INTEGER, user_product TEXT, quantity INTEGER, total_for_product REAL);')


def register_user(tg_id, name, phone_number, address):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Добавление в базу пользователя
    sql.execute('INSERT INTO users'
                '(tg_id, name, phone_number, address, reg_date)'
                'VALUES (?, ?, ?, ?, ?);',
                (tg_id, name, phone_number, address, datetime.now()))

    # Записывание обновлений
    connection.commit()


# Проверка пользователя на наличие в бд
def check_user(user_id):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    checker = sql.execute('SELECT tg_id FROM users '
                          'WHERE tg_id=?;', (user_id,))

    return checker.fetchone()


def add_product_to_store(pr_name, pr_count, pr_price, pr_des, pr_photo):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Добавление в базу пользователя
    sql.execute('INSERT INTO products'
                '(pr_name, pr_price, pr_quantity, pr_des, pr_photo, reg_date)'
                'VALUES (?, ?, ?, ?, ?, ?);',
                (pr_name, pr_price, pr_count, pr_des, pr_photo, datetime.now()))

    # Записывание обновлений
    connection.commit()


# Удаление продуктов из склада
def delete_products_from_store():
    pass


# Удаление продукта из склада
def delete_product_from_store():
    pass


def get_pr_name_id():
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Получение всех продуктов из базы -> (name, id)
    products = sql.execute('SELECT pr_name, pr_id, pr_quantity FROM products').fetchall()

    # Сортировка только того, что осталось на складе
    sorted_product = [(i[0], i[1]) for i in products if i if i[2] > 0]

    # Чистый список продуктов [(name, id), ... , (name, id)]
    return sorted_product


def get_pr_id():
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Получение всех продуктов из базы -> (name, id)
    products = sql.execute('SELECT pr_name, pr_id, pr_quantity FROM products').fetchall()

    # Сортировка только того, что осталось на складе
    sorted_product = [i[1] for i in products if i if i[2] > 0]

    # Чистый список продуктов [(name, id), ... , (name, id)]
    return sorted_product


# Получение информации про определенный продукт (через pr_id) -> (photo, des, price)
def get_exact_product(pr_id):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    exact_product = sql.execute('SELECT pr_photo, pr_des, pr_price '
                                'FROM products WHERE pr_id=?;',
                                (pr_id,)).fetchone()

    return exact_product


# Добавление продуктов в корзину пользователя
def add_product_to_cart(user_id, product, quantity):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Получить цену продукта из базы
    product_price = get_exact_product(product)[2]

    sql.execute('INSERT INTO user_cart'
                '(user_id, user_product, quantity, total_for_product)'
                'VALUES (?, ?, ?, ?);',
                (user_id, product, quantity, quantity * product_price))

    # Записывание обновлений
    connection.commit()


# Удаление продукта из корзины
def delete_exact_product_from_cart(pr_id, user_id):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    # Удалить продукт из корзины через pr_id
    sql.execute('DELETE FROM user_cart WHERE user_products=? AND user_id=?;',
                (pr_id, user_id))

    # Записывание обновлений
    connection.commit()


# Вывод корзины пользователя через
# (user_id) ->
# [(product, quantity, total_for_pr), (prod)]
# ...
# [(product, quantity, total_for_pr), (prod)]
def get_exact_user_cart(user_id):
    # Создание подключения
    connection = sqlite3.connect('delivery.db')
    # Переводчик/исполнитель
    sql = connection.cursor()

    user_cart = sql.execute('SELECT products.pr_name, user_cart.quantity, user_cart.total_for_product '
                            'FROM user_cart '
                            'INNER JOIN products ON products.pr_id=user_cart.user_product '
                            'WHERE user_id=?;',
                            (user_id,)).fetchall()

    return user_cart
