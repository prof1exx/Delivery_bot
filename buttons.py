from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# Кнопки со всеми продуктами (основное меню)
def start_buttons(products_from_db):
    # Создание пространства для кнопок
    keyboard = InlineKeyboardMarkup(row_width=2)

    # Создание несгораемых кнопок
    order = InlineKeyboardButton(text='Оформить заказ', callback_data='order')
    cart = InlineKeyboardButton(text='Корзина', callback_data='cart')

    # Создание кнопок с продуктами
    all_products = [InlineKeyboardButton(text=i[0], callback_data=i[1])
                    for i in products_from_db]

    # Объединение пространства с кнопками
    keyboard.row(order)
    keyboard.add(*all_products)
    keyboard.row(cart)

    # Возращение кнопок
    return keyboard


# Кнопки для выбора количества
def choose_product_count_buttons(plus_or_minus='', current_amount=1):
    # Создание пространства для кнопок
    keyboard = InlineKeyboardMarkup(row_width=3)

    # Несгораемая кнопка
    back = InlineKeyboardButton(text='Назад', callback_data='back')
    plus = InlineKeyboardButton(text='+', callback_data='increment')
    minus = InlineKeyboardButton(text='-', callback_data='decrement')
    count = InlineKeyboardButton(text=str(current_amount),
                                 callback_data=str(current_amount))
    add_to_cart = InlineKeyboardButton(text='Добавить в корзину',
                                       callback_data='to_cart')

    # Отслеживание: плюс или минус
    if plus_or_minus == 'increment':
        new_amount = int(current_amount) + 1

        count = InlineKeyboardButton(text=str(new_amount),
                                     callback_data=str(current_amount))

    elif plus_or_minus == 'decrement':
        if int(current_amount) > 1:
            new_amount = int(current_amount) - 1

            count = InlineKeyboardButton(text=str(new_amount),
                                         callback_data=str(current_amount))

    # Объединение кнопок с пространством
    keyboard.add(minus, count, plus)
    keyboard.row(add_to_cart)
    keyboard.row(back)

    # Возращение кнопок
    return keyboard


# Кнопка для отправки номера телефона
def phone_number_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    number = KeyboardButton('Поделиться контактом', request_contact=True)

    keyboard.add(number)

    return keyboard


# Кнопка для отправки номера локации
def location_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    location = KeyboardButton('Поделиться локация', request_location=True)

    keyboard.add(location)

    return keyboard


# Кнопки для подтверждения заказа
def get_accept_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    yes = KeyboardButton('Подтвердить')
    no = KeyboardButton('Отменить')

    keyboard.add(yes, no)

    return keyboard
