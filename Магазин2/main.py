import sqlite3
import telebot
from telebot import types
from dotenv import dotenv_values
import datetime

config = dotenv_values('.env')
bot = telebot.TeleBot(config.get('TELEGRAM_TOKEN'))

def executeAll(req):
      connection = sqlite3.connect(config.get('DB_NAME'))
      cursor = connection.cursor()
      cursor.execute(req)
      data = cursor.fetchall()
      connection.close()
      return data

def executeOne(req):
      connection = sqlite3.connect(config.get('DB_NAME'))
      cursor = connection.cursor()
      cursor.execute(req)
      data = cursor.fetchone()
      connection.close()
      return data


print('RABOTAET')


# СТАРТОВОЕ СООБЩЕНИЕ
@bot.message_handler(commands=['start','main','hello'])
def main(message):
    user_id = message.from_user.id
    balance = 160
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
  
    # Проверка наличия пользователя в базе данных
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user_exists = cursor.fetchone()
    
    if not user_exists:
        # Добавление нового пользователя
        cursor.execute('INSERT INTO users (id, balance) VALUES (?, ?)', (user_id, balance))

    connection.commit()
    connection.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Меню✅', callback_data='menu'))
    markup.add(types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC'))
    markup.add(types.InlineKeyboardButton('История заказов', callback_data='history'))
    markup.add(types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance'))
    markup.add(types.InlineKeyboardButton('Баланс', callback_data='balance'))
    bot.send_photo(message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)


# ПОСМОТРЕТЬ БАЛАНС
@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def callback_menu(call):
   if call.data == 'balance':
        result = executeAll(f'SELECT balance FROM users WHERE id = {call.message.chat.id}')
        if result:
            balance = result[0]
            bot.send_message(call.message.chat.id, '💎💵Текущий баланс: {}'.format(balance))
        else:
            bot.send_message(call.message.chat.id, 'Пользователь не найден')

# Пополнение баланса
@bot.callback_query_handler(func=lambda call: call.data == 'addbalance')
def callback_menu(call):
   if call.data == 'addbalance':
        connection = sqlite3.connect(config.get('DB_NAME'))
        cursor = connection.cursor()
        user_id = call.from_user.id
        # Получаем баланс пользователя из базы данных
        cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
        result = cursor.fetchone()
        if result:
            balance = result[0]
            bot.send_message(call.message.chat.id, '💎💵Текущий баланс: {}'.format(balance))
            bot.send_message(call.message.chat.id, '💎💵Введите сумму для пополнения баланса💵💎:')
            bot.register_next_step_handler(call.message, process_balance_update)
        else:
            bot.send_message(call.message.chat.id, 'Пользователь не найден')

# ФУНКЦИЯ ПОПОЛНЕНИЯ
def process_balance_update(message):
    try:
        amount = int(message.text)
        user_id = message.from_user.id
        connection = sqlite3.connect(config.get('DB_NAME'))
        cursor = connection.cursor()
        # Получаем текущий баланс пользователя
        cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
        result = cursor.fetchone()
        if result:
            balance = result[0]
            if amount <= 5000 and amount > 0:
               new_balance = balance + amount
               # Обновляем баланс пользователя
               cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')
               connection.commit()
               connection.close()
               bot.send_message(message.chat.id, '💸Баланс успешно обновлен! Новый баланс: {}💸'.format(new_balance))
            else:
                bot.send_message(message.chat.id, 'Нельзя меньше 0 и нельзя больше 5000')
        else:
            connection.close()
            bot.send_message(message.chat.id, 'Пользователь не найден')
    except ValueError:
        bot.send_message(message.chat.id, 'Вводи только числа')

# ИСТОРИЯ ПОКУПОК
@bot.callback_query_handler(func=lambda call: call.data == 'history')
def callback_menu(call):
    if call.data == 'history':
        user_id = call.from_user.id
        connection = sqlite3.connect(config.get('DB_NAME'))
        cursor = connection.cursor()
        cursor.execute('SELECT * from bills WHERE user_id=?', (user_id,))
        bills = cursor.fetchall()
        info = 'Вот твоя история заказов:\n'
        for bill in bills:
            info += '💎💵Айди: {user_id}, Айди товара: {item_id}, Дата покупки: {date}\n'.format(user_id=user_id, item_id=bill[1], date=bill[2])
        cursor.close()
        connection.close()
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Назад⬅️', callback_data='back6')
        markup.add(button1)
        bot.send_message(call.message.chat.id, info, reply_markup=markup)


   
# ВОЗВРАЩЕНИЕ С ИСТОРИИ В ГЛАВ ЭКРАН
@bot.callback_query_handler(func=lambda call: call.data == 'back6')
def callback_menu(call):
   if call.data == 'back6':
     markup = types.InlineKeyboardMarkup()
     markup.add(types.InlineKeyboardButton('Меню✅', callback_data='menu'))
     markup.add(types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC'))
     markup.add(types.InlineKeyboardButton('История заказов', callback_data='history'))
     markup.add(types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance'))
     markup.add(types.InlineKeyboardButton('Баланс', callback_data='balance'))
     bot.send_photo(call.message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {call.message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)

# ОСНОВА МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def callback_menu(call):
   if call.data == 'menu':
       markup = types.InlineKeyboardMarkup()
       markup.add(types.InlineKeyboardButton('Товары', callback_data='tovar'))
       markup.add(types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit'))
       markup.add(types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC'))
       markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back2'))
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

# ИЗ МЕНЮ В ТОВАРЫ
@bot.callback_query_handler(func=lambda call: call.data == 'tovar')
def callback_tovar(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM categories")
    data = cursor.fetchall()
    connection.close()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back4'))
    for item in data:
        id, type = item
        markup.add(types.InlineKeyboardButton(type, callback_data=f'category_{id}'))

    bot.send_photo(call.message.chat.id, photo=open('photo3.png',  'rb'), caption=f"Выберите категорию товаров:", reply_markup=markup)

# ПЕРЕХОД ПОСЛЕ КАТЕГОРИЙ В КАКОЙ ТО ИЗ КАТЕГОРИЙ В ТОВАРЫ
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def callback_category(call):
       category_id = call.data.split("_")[1]  # Получаем ID категории из callback_data
       connection = sqlite3.connect(config.get('DB_NAME'))
       cursor = connection.cursor()
       query = f'''
               SELECT items.id, items.name
               FROM items
               INNER JOIN categories ON items.categories_id = categories.id
               WHERE categories.id = {category_id}
               '''
       cursor.execute(query)
       data = cursor.fetchall()
       connection.close()

       markup = types.InlineKeyboardMarkup()
       markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back5'))
       for item in data:
           item_id, item_name = item
           markup.add(types.InlineKeyboardButton(item_name, callback_data=f'item_{item_id}'))

       bot.send_photo(call.message.chat.id, photo=open('photo2.png',  'rb'), caption=f"Выберите товар:", reply_markup=markup)

# ПЕРЕХОД В ТОВАР ИЗ СПИСКА ТОВАРОВ
@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def callback_item(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    item_id = call.data.split("_")[1]  # Получаем ID товара из callback_data
    query = f'''
            SELECT name, desc, price, photo
            FROM items
            WHERE id = {item_id}
            '''
    cursor.execute(query)
    data = cursor.fetchone()
    item_name, item_desc, item_price, item_photo = data
    bot.send_photo(call.message.chat.id, photo=open(f'{item_photo}.png', 'rb'), caption=f"Название: {item_name}\nОписание: {item_desc}\nЦена: {item_price}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back6'))
    markup.add(types.InlineKeyboardButton('Купить', callback_data=f'buy_{item_id}'))
    bot.send_message(call.message.chat.id, "Для покупки нажмите кнопку ниже:", reply_markup=markup)


# ПОКУПКА ТОВАРА
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def callback_buy(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    item_id = call.data.split("_")[1]

    # Получение информации о товаре из базы данных
    item_query = '''
            SELECT name, price
            FROM items
            WHERE id = ?'''
    cursor.execute(item_query, (item_id,))
    item_data = cursor.fetchone()
    item_name, item_price_str = item_data
    item_price = int(item_price_str)

    # Получение баланса пользователя из базы данных
    balance_query = '''
            SELECT balance
            FROM users
            WHERE id = ?'''
    cursor.execute(balance_query, (user_id,))
    user_balance = cursor.fetchone()[0]

    if user_balance >= item_price:
        # Обновление баланса пользователя
        new_balance = user_balance - item_price
        update_query = '''
                   UPDATE users
                   SET balance = ?
                   WHERE id = ?'''
        cursor.execute(update_query, (new_balance, user_id))

        # Добавление информации о покупке в таблицу bills
        insert_query = '''
                   INSERT INTO bills (user_id, item_id, date)
                   VALUES (?, ?, CURRENT_TIMESTAMP)'''
        cursor.execute(insert_query, (user_id, item_id))

        connection.commit()

        bot.send_message(call.message.chat.id, 'Поздравляем с покупкой! Ваш баланс обновлен.')
    else:
        bot.send_message(call.message.chat.id, 'У вас недостаточно средств для покупки.')


# ПЕРЕХОД ИЗ ВЫБРАННОЙ КАТЕГОРИИ В КАТЕГОРИИ
@bot.callback_query_handler(func=lambda call: call.data == 'back5')
def callback_tovar(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM categories")
    data = cursor.fetchall()
    connection.close()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back4'))
    for item in data:
        id, type = item
        markup.add(types.InlineKeyboardButton(type, callback_data=f'category_{id}'))

    bot.send_photo(call.message.chat.id, photo=open('photo3.png',  'rb'), caption=f"Выберите категорию товаров:", reply_markup=markup)

# ИЗ ТОВАРОВ В МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back4')
def callback_menu(call):
   if call.data == 'back4':
       markup = types.InlineKeyboardMarkup()
       markup.add(types.InlineKeyboardButton('Товары', callback_data='tovar'))
       markup.add(types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit'))
       markup.add(types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC'))
       markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back2'))
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

# ВОЗВРАЩЕНИЕ НА ГЛАВ ЭКРАН С МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back2')
def callback_menu(call):
   if call.data == 'back2':
     markup = types.InlineKeyboardMarkup()
     markup.add(types.InlineKeyboardButton('Меню✅', callback_data='menu'))
     markup.add(types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC'))
     markup.add(types.InlineKeyboardButton('История заказов', callback_data='history'))
     markup.add(types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance'))
     markup.add(types.InlineKeyboardButton('Баланс', callback_data='balance'))
     bot.send_photo(call.message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {call.message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)

# РЕКВИЗИТЫ В КОТОРЫЕ ЗАХОДЯТ ИЗ МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'rekvizit')
def callback_menu(call):
   if call.data == 'rekvizit':
     markup = types.InlineKeyboardMarkup()
     button1 = types.InlineKeyboardButton('Donationalerts', url='https://clck.ru/374e7g')
     button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back3')
     markup.add(button1,button2)
     bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo4.png',  'rb'), caption=f'⚡💳💸 Оплату за услуги можно осуществить на карту банка <b>МИР</b>: 2202700966606930 или через <b>Donationalerts</b>',reply_markup=markup)

# ВОЗВРАЩЕНИЕ С РЕКВИЗИТОВ В МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back3')
def callback_menu(call):
   if call.data == 'back3':
       markup = types.InlineKeyboardMarkup()
       markup.add(types.InlineKeyboardButton('Товары', callback_data='tovar'))
       markup.add(types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit'))
       markup.add(types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC'))
       markup.add(types.InlineKeyboardButton('Назад⬅️', callback_data='back2'))
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

# ОТВЕТКА НА РАНДОМНЫЙ ТЕКСТ
@bot.message_handler()
def send_text(message):
    bot.send_message(message.chat.id, 'Я тебя не понимаю...')


bot.polling(none_stop=True, interval=0)







