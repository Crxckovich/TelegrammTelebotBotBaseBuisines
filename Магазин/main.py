import sqlite3
import telebot
from telebot import types
from dotenv import dotenv_values
import datetime

config = dotenv_values('.env')
bot = telebot.TeleBot(config.get('TELEGRAM_TOKEN'))


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
    button1 = types.InlineKeyboardButton('Меню✅', callback_data='menu')
    button2 = types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC')
    button3 = types.InlineKeyboardButton('История заказов', callback_data='history')
    button4 = types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance')
    markup.add(button1,button2,button3,button4)
    bot.send_photo(message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)

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
     button1 = types.InlineKeyboardButton('Меню✅', callback_data='menu')
     button2 = types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC')
     button3 = types.InlineKeyboardButton('История заказов', callback_data='history')
     button4 = types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance')
     markup.add(button1,button2,button3,button4)
     bot.send_photo(call.message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {call.message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)

# ОСНОВА МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def callback_menu(call):
   if call.data == 'menu':
       markup = types.InlineKeyboardMarkup()
       button1 = types.InlineKeyboardButton('Назад⬅️', callback_data='back1')
       button2 = types.InlineKeyboardButton('Товары', callback_data='tovar')
       button3 = types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit')
       button4 = types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC')
       markup.add(button1,button2,button3,button4)
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

# ВОЗВРАЩЕНИЕ НА ГЛАВ ЭКРАН С МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back1')
def callback_menu(call):
   if call.data == 'back1':
     markup = types.InlineKeyboardMarkup()
     button1 = types.InlineKeyboardButton('Меню✅', callback_data='menu')
     button2 = types.InlineKeyboardButton('НАШИ ОТЗЫВЫ💬📊', url='https://clck.ru/374VdC')
     button3 = types.InlineKeyboardButton('История заказов', callback_data='history')
     button4 = types.InlineKeyboardButton('Пополнить баланс', callback_data='addbalance')
     markup.add(button1,button2,button3,button4)
     bot.send_photo(call.message.chat.id, parse_mode= 'html',  photo=open('photo.png',  'rb'), caption=f'<b>Привет</b>, {call.message.chat.first_name}!\n<b>Я БОТ Магазина РЕЙЛ | Дизайн и оформление. Я являюсь как навигатором в этом канале так и помощником в ваших покупках</b> 😇',reply_markup=markup)

# СПИСОК ТОВАРОВ ИДЕТ ПОСЛЕ МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'tovar')
def callback_menu(call):
       if call.data == 'tovar':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Шапки🧢', callback_data='hat')
          button2 = types.InlineKeyboardButton('Аватарки👤', callback_data='ava')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back2')
          markup.add(button1,button2,button3)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Список товаров📃🛍️',reply_markup=markup)

# ИЗ ТОВАРОВ В АВАТАРКИ
@bot.callback_query_handler(func=lambda call: call.data == 'ava')
def callback_menu(call):
       if call.data == 'ava':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('👤 Аватар Минимализм', callback_data='AvaMIN')
          button2 = types.InlineKeyboardButton('👤 Аватар 3D', callback_data='Ava3D')
          button4 = types.InlineKeyboardButton('👤 Аватар ВК', callback_data='AvaVK')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back4')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ АВАТАРОК В АВАТАРКУ ВКОНТАКТЕ
@bot.callback_query_handler(func=lambda call: call.data == 'AvaVK')
def callback_menu(call):
       if call.data == 'AvaVK':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyAvaVK')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back12')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo12.png',  'rb'), caption=f'👤 Аватар Вконтакте – 650 рублей',reply_markup=markup)

# КОД ПОКУПКИ АВАТАРКИ ВКОНТАКТЕ
@bot.callback_query_handler(func=lambda call: call.data == 'buyAvaVK')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        cursor.execute(f'SELECT price FROM items WHERE id = 3 AND categories_id = 2')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 3
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')

# ИЗ АВАТАРКИ ВКОНТАКТЕ В АВАТАРКИ
@bot.callback_query_handler(func=lambda call: call.data == 'back12')
def callback_menu(call):
       if call.data == 'back12':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('👤 Аватар Минимализм', callback_data='AvaMIN')
          button2 = types.InlineKeyboardButton('👤 Аватар 3D', callback_data='Ava3D')
          button4 = types.InlineKeyboardButton('👤 Аватар ВК', callback_data='AvaVK')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back4')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ АВАТАРОК В АВАТАРКУ 3D
@bot.callback_query_handler(func=lambda call: call.data == 'Ava3D')
def callback_menu(call):
       if call.data == 'Ava3D':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyAva3D')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back11')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo11.png',  'rb'), caption=f'👤 Аватар 3D – 427 рублей',reply_markup=markup)

# КОД ПОКУПКИ АВАТАРКИ 3D
@bot.callback_query_handler(func=lambda call: call.data == 'buyAva3D')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        cursor.execute(f'SELECT price FROM items WHERE id = 2 AND categories_id = 2')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 2
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')

# ИЗ АВАТАРКИ 3D В АВАТАРКИ
@bot.callback_query_handler(func=lambda call: call.data == 'back11')
def callback_menu(call):
       if call.data == 'back11':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('👤 Аватар Минимализм', callback_data='AvaMIN')
          button2 = types.InlineKeyboardButton('👤 Аватар 3D', callback_data='Ava3D')
          button4 = types.InlineKeyboardButton('👤 Аватар ВК', callback_data='AvaVK')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back4')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ ТОВАРОВ В ШАПКИ
@bot.callback_query_handler(func=lambda call: call.data == 'hat')
def callback_menu(call):
       if call.data == 'hat':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Минимализм Шапка🎩', callback_data='HatMIN')
          button2 = types.InlineKeyboardButton('Шапка 2D⛑️', callback_data='Hat2D')
          button3 = types.InlineKeyboardButton('Шапка 3D🧢', callback_data='Hat3D')
          button4 = types.InlineKeyboardButton('Назад⬅️', callback_data='back7')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ ШАПОК В ШАПКУ 2D
@bot.callback_query_handler(func=lambda call: call.data == 'Hat2D')
def callback_menu(call):
       if call.data == 'Hat2D':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyHat2D')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back10')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo10.png',  'rb'), caption=f'🌅 Шапка 2D – 780 рублей 💎ХИТ💎',reply_markup=markup)

# КОД ПОКУПКИ ШАПКИ 2D
@bot.callback_query_handler(func=lambda call: call.data == 'buyHat2D')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        cursor.execute(f'SELECT price FROM items WHERE id = 6 AND categories_id = 1')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 6
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')
          
# ИЗ МИНИМАЛИЗМ ШАПКИ В ШАПКИ
@bot.callback_query_handler(func=lambda call: call.data == 'back10')
def callback_menu(call):
       if call.data == 'back10':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Минимализм Шапка🎩', callback_data='HatMIN')
          button2 = types.InlineKeyboardButton('Шапка 2D⛑️', callback_data='Hat2D')
          button3 = types.InlineKeyboardButton('Шапка 3D🧢', callback_data='Hat3D')
          button4 = types.InlineKeyboardButton('Назад⬅️', callback_data='back7')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ ШАПОК В МИНИМАЛИЗМ ШАПКУ
@bot.callback_query_handler(func=lambda call: call.data == 'HatMIN')
def callback_menu(call):
       if call.data == 'HatMIN':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyHatMIN')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back9')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo9.png',  'rb'), caption=f'🖼️ Шапка Минимализм – 353 рублей.✅',reply_markup=markup)

# КОД ПОКУПКИ МИНИМАЛИЗМ ШАПКИ
@bot.callback_query_handler(func=lambda call: call.data == 'buyHatMIN')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        cursor.execute(f'SELECT price FROM items WHERE id = 7 AND categories_id = 1')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 7
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')

# ИЗ МИНИМАЛИЗМ ШАПКИ В ШАПКИ
@bot.callback_query_handler(func=lambda call: call.data == 'back9')
def callback_menu(call):
       if call.data == 'back9':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Минимализм Шапка🎩', callback_data='HatMIN')
          button2 = types.InlineKeyboardButton('Шапка 2D⛑️', callback_data='Hat2D')
          button3 = types.InlineKeyboardButton('Шапка 3D🧢', callback_data='Hat3D')
          button4 = types.InlineKeyboardButton('Назад⬅️', callback_data='back7')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ ШАПОК В ТОВАРЫ
@bot.callback_query_handler(func=lambda call: call.data == 'back7')
def callback_menu(call):
       if call.data == 'back7':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Шапки🧢', callback_data='hat')
          button2 = types.InlineKeyboardButton('Аватарки👤', callback_data='ava')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back2')
          markup.add(button1,button2,button3)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Список товаров📃🛍️',reply_markup=markup)

# ИЗ ШАПОК В ШАПКУ 3D
@bot.callback_query_handler(func=lambda call: call.data == 'Hat3D')
def callback_menu(call):
       if call.data == 'Hat3D':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyHat3D')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back8')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo8.png',  'rb'), caption=f'🌌 Шапка 3D – 980 рублей',reply_markup=markup)

# ИЗ ШАПКИ 3D В ШАПКИ
@bot.callback_query_handler(func=lambda call: call.data == 'back8')
def callback_menu(call):
       if call.data == 'back8':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Минимализм Шапка🎩', callback_data='HatMIN')
          button2 = types.InlineKeyboardButton('Шапка 2D⛑️', callback_data='Hat2D')
          button3 = types.InlineKeyboardButton('Шапка 3D🧢', callback_data='Hat3D')
          button4 = types.InlineKeyboardButton('Назад⬅️', callback_data='back7')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# КОД ПОКУПКИ ШАПКИ 3D
@bot.callback_query_handler(func=lambda call: call.data == 'buyHat3D')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        cursor.execute(f'SELECT price FROM items WHERE id = 5 AND categories_id = 1')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 5
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')




# ИЗ АВАТАРОК В АВАТАРКА МИНИМАЛЬНАЯ
@bot.callback_query_handler(func=lambda call: call.data == 'AvaMIN')
def callback_menu(call):
       if call.data == 'AvaMIN':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Купить❇️', callback_data='buyAvaMIN')
          button2 = types.InlineKeyboardButton('Назад⬅️', callback_data='back5')
          markup.add(button1,button2)
          bot.send_photo(call.message.chat.id,  photo=open('photo6.png',  'rb'), caption=f'👤 Аватар Минимализм – 99 рублей.',reply_markup=markup)

# КОД ПОКУПКИ МИНИМАЛЬНОЙ АВАТАРКИ
@bot.callback_query_handler(func=lambda call: call.data == 'buyAvaMIN')
def callback_menu(call):
    connection = sqlite3.connect(config.get('DB_NAME'))
    cursor = connection.cursor()
    user_id = call.from_user.id
    # Получаем баланс пользователя из базы данных
    cursor.execute(f'SELECT balance FROM users WHERE id = {user_id}')
    result = cursor.fetchone()
    if result:
        balance = result[0]
        # Получаем цену предмета AvaMIN из базы данных
        cursor.execute(f'SELECT price FROM items WHERE id = 1 AND categories_id = 2')
        item_price = cursor.fetchone()
        if item_price:
            item_price = item_price[0]
            if balance >= item_price:
                # обновляем баланс пользователя
                new_balance = balance - item_price
                cursor.execute(f'UPDATE users SET balance = {new_balance} WHERE id = {user_id}')

                # Добавляем чек
                item_id = 1  # id предмета AvaMIN
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO bills (user_id, item_id, date) VALUES (?, ?, ?)', (user_id, item_id, date))
                connection.commit()
                # отправляем сообщение об успешной покупке
                bot.send_message(call.message.chat.id, 'Покупка успешно выполнена!')
            else:
                # отправляем сообщение о нехватке средств
                bot.send_message(call.message.chat.id, 'Недостаточно средств')
        else:
            # отправляем сообщение об ошибке
            bot.send_message(call.message.chat.id, 'Не удалось получить цену предмета')
    else:
        bot.send_message(call.message.chat.id, 'Пользователь не найден')

# ИЗ МИН АВАТАРА В ВЫБОР АВАТАРОК
@bot.callback_query_handler(func=lambda call: call.data == 'back5')
def callback_menu(call):
       if call.data == 'back5':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('👤 Аватар Минимализм', callback_data='AvaMIN')
          button2 = types.InlineKeyboardButton('👤 Аватар 3D', callback_data='Ava3D')
          button4 = types.InlineKeyboardButton('👤 Аватар ВК', callback_data='AvaVK')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back4')
          markup.add(button1,button2,button3,button4)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Выбор аватарок👤',reply_markup=markup)

# ИЗ АВАТАРОК В ТОВАРЫ
@bot.callback_query_handler(func=lambda call: call.data == 'back4')
def callback_menu(call):
       if call.data == 'back4':
          markup = types.InlineKeyboardMarkup()
          button1 = types.InlineKeyboardButton('Шапки🧢', callback_data='hat')
          button2 = types.InlineKeyboardButton('Аватарки👤', callback_data='ava')
          button3 = types.InlineKeyboardButton('Назад⬅️', callback_data='back2')
          markup.add(button1,button2,button3)
          bot.send_photo(call.message.chat.id,  photo=open('photo3.png',  'rb'), caption=f'Список товаров📃🛍️',reply_markup=markup)

# ВОЗВРАЩЕНИЕ С ТОВАРОВ В МЕНЮ
@bot.callback_query_handler(func=lambda call: call.data == 'back2')
def callback_menu(call):
   if call.data == 'back2':
       markup = types.InlineKeyboardMarkup()
       button1 = types.InlineKeyboardButton('Назад⬅️', callback_data='back1')
       button2 = types.InlineKeyboardButton('Товары', callback_data='tovar')
       button3 = types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit')
       button4 = types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC')
       markup.add(button1,button2,button3,button4)
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

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
       button1 = types.InlineKeyboardButton('Назад⬅️', callback_data='back1')
       button2 = types.InlineKeyboardButton('Товары', callback_data='tovar')
       button3 = types.InlineKeyboardButton('Реквизиты', callback_data='rekvizit')
       button4 = types.InlineKeyboardButton('Портфолио📊', url='https://clck.ru/374VdC')
       markup.add(button1,button2,button3,button4)
       bot.send_photo(call.message.chat.id,parse_mode= 'html',  photo=open('photo2.png',  'rb'), caption=f'Вот наше меню. Выберите что вы желаете посмотреть. Советуем перед началом посмотреть 📛<b>ПРАВИЛА</b>📛 и наше портфолио. <b>ПЕРЕД ПОКУПКОЙ ЗАЙДИТЕ В РЕКВИЗИТЫ!</b>',reply_markup=markup)

# ОТВЕТКА НА РАНДОМНЫЙ ТЕКСТ
@bot.message_handler()
def send_text(message):
    bot.send_message(message.chat.id, 'Я тебя не понимаю...')


bot.polling(none_stop=True, interval=0)







