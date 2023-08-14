import telebot
import buttons
import database
from geopy.geocoders import Nominatim
from telebot.types import ReplyKeyboardRemove

# Создание подключение к боту
bot = telebot.TeleBot('6247779047:AAEwOkv1eM6bdd6vhk57rsH0HD2sjb13JbQ')
geolocator = Nominatim(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/114.0.0.0 Safari/537.36')
# Словарь для временных данных
users = {}


# database.add_product_to_store('Яблоки',
#                               7,
#                               7000,
#                               'Самые вкусные',
#                               'https://catherineasquithgallery.com/uploads/posts/2023-02'
#                               '/1676632876_catherineasquithgallery-com-p-fon-s-zelenimi-yablokami-83.jpg')


# Обработка команды старт
@bot.message_handler(commands=['start'])
def start_message(message):
    # Получение айди пользователя
    user_id = message.from_user.id

    # Проверка пользователя на наличие в бд
    checker = database.check_user(user_id)

    # Если пользователь есть в базе
    if checker:
        # Получение актуального списка продуктов
        products = database.get_pr_name_id()

        # Отправление сообщения с меню
        bot.send_message(user_id,
                         'Выберите пункт меню',
                         reply_markup=buttons.start_buttons(products))

    elif not checker:
        bot.send_message(user_id, 'Привет!\nОтправь своё имя.')

        # Переход на этап получения имени
        bot.register_next_step_handler(message, get_name)


# Этап получения имени
def get_name(message):
    # Получение айди пользователя
    user_id = message.from_user.id

    # Сохранение имя в переменную
    username = message.text

    # Отправление ответа
    bot.send_message(user_id,
                     'Теперь отправьте свой номер телефона',
                     reply_markup=buttons.phone_number_button())

    # Переход на этап получения номера телефона
    bot.register_next_step_handler(message, get_number, username)


# Этап получения номера
def get_number(message, name):
    # Получение айди пользователя
    user_id = message.from_user.id

    # Проверка: отправил ли пользователь свой контакт
    if message.contact:
        # Сохраним контакт
        phone_number = message.contact.phone_number

        # Сохранение его в базе
        database.register_user(user_id, name, phone_number, 'Not yet')

        # Открывание меню
        products = database.get_pr_name_id()
        bot.send_message(user_id,
                         'Выберите пункт меню',
                         reply_markup=buttons.start_buttons(products))

    elif not message.contact:
        bot.send_message(user_id,
                         'Отправьте контакт используя кнопку',
                         reply_markup=buttons.phone_number_button())

        # Обратно на этап получения номера телефона
        bot.register_next_step_handler(message, get_number, name)


# Обработчик выбора количества
@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def get_user_product_count(call):
    # Получение айди пользователя
    user_id = call.message.chat.id

    # Если пользователь нажал на +
    if call.data == 'increment':
        actual_count = users[user_id]['pr_count']

        users[user_id]['pr_count'] += 1
        # Меняем значение кнопки
        bot.edit_message_reply_markup(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=buttons.choose_product_count_buttons
                                      ('increment', actual_count))

    elif call.data == 'decrement':
        actual_count = users[user_id]['pr_count']

        users[user_id]['pr_count'] -= 1
        # Меняем значение кнопки
        bot.edit_message_reply_markup(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=buttons.choose_product_count_buttons
                                      ('decrement', actual_count))

    elif call.data == 'back':
        # Обнуляем
        users[user_id]['pr_count'] = 0

        # Получаем меню
        products = database.get_pr_name_id()

        # Меняем на меню
        bot.edit_message_text('Выберите пункт меню',
                              user_id,
                              call.message.message_id,
                              reply_markup=buttons.start_buttons(products))

    elif call.data == 'to_cart':
        # Получение данные
        product_count = users[user_id]['pr_count']
        user_product = users[user_id]['pr_name']

        # Добавление в бд корзину пользователя
        database.add_product_to_cart(user_id, user_product, product_count)

        # Получаем обратно меню
        products = database.get_pr_name_id()

        # Меняем на меню
        bot.edit_message_text('Продукт добавлен в корзину.\nЧто-нибудь еще?',
                              user_id,
                              call.message.message_id,
                              reply_markup=buttons.start_buttons(products))


# Обработчик кнопок (Оформить заказ, корзина)
@bot.callback_query_handler(lambda call: call.data in ['order', 'cart'])
def start_buttons_handle(call):
    user_id = call.message.chat.id
    message_id = call.message.message_id

    # Если нажал на кнопку: Оформить заказ
    if call.data == 'order':
        # Удалим сообщение с верхними кнопками
        bot.delete_message(user_id, message_id)

        # Поменяем текст на 'Отправьте локацию'
        bot.send_message(user_id,
                         'Отправьте локацию',
                         reply_markup=buttons.location_button())

        # Переход на сохранение локации
        bot.register_next_step_handler(call.message, get_location)


# Функция сохранения локации пользователя:
def get_location(message):
    user_id = message.from_user.id

    # Отправил ли локацию
    if message.location:
        # Сохранить в переменную координаты
        latitude = message.location.latitude
        longitude = message.location.longitude

        # Преобразуем координаты на нормальный адрес
        address = geolocator.reverse((latitude, longitude)).address

        # Запрос подтверждения заказа
        user_cart = database.get_exact_user_cart(user_id)

        bot.send_message(user_id,
                         'Ваша корзина',
                         reply_markup=buttons.get_accept_buttons())

        # Переход на этап подтверждения
        bot.register_next_step_handler(message, get_accept, address)


# Функция сохранения статуса заказа
def get_accept(message, address):
    pass


# Обработчик выбора товара
@bot.callback_query_handler(lambda call: int(call.data) in database.get_pr_id())
def get_user_product(call):
    # Получение айди пользователя
    user_id = call.message.chat.id

    # Сохранение продукта во временный словарь
    # call.data — значение нажатой инлайн кнопки
    users[user_id] = {'pr_name': call.data, 'pr_count': 1}

    # Сохранение айди сообщения
    message_id = call.message.message_id

    # Поменять кнопки на выбор количества
    bot.edit_message_text('Выберите количество',
                          chat_id=user_id,
                          message_id=message_id,
                          reply_markup=buttons.choose_product_count_buttons())


# Запуск бота
bot.polling()
