import sqlite3
from telebot import TeleBot, types

TOKEN = 'YOUR TOKEN'
bot = TeleBot(TOKEN)
conn = sqlite3.connect('YOUR_DATABASE', check_same_thread=False)
cursor = conn.cursor()


greeting = 'Привет! Это реферальный бот. Твой идентификатор: {}'


# Handle the /start command
@bot.message_handler(commands=['start'])
def handle_start(message):
    referrer_id = None
    if len(message.text.split()) > 1:
        referrer_id = int(message.text.split()[1])

    if referrer_id:
        cursor.execute('INSERT INTO referrals (user_id, referrer_id) VALUES (?, ?)',
                       (message.chat.id, referrer_id))
        conn.commit()

    bot.send_message(message.chat.id, greeting.format(message.chat.id))


# Handle the /help command
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, 'Я могу выполнить следующие команды:\n'
                                      '/start - начать работу с ботом и получить свой идентификатор\n'
                                      '/stats - получить статистику по реферальным ссылкам\n'
                                      '/set_greeting - установить текст приветствия\n'
                                      '/feedback - оставить отзыв\n'
                                      '/help - получить справку по командам\n\n'
                                      'Если у тебя возникли какие-то вопросы или проблемы, '
                                      'обратись к разработчику бота - @matveysofie')


@bot.message_handler(commands=['stats24'])
def handle_stats(message):
    cursor.execute('SELECT COUNT(*) FROM referrals '
                   'WHERE created_at >= datetime("now", "-1 day")')
    today_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM referrals')
    total_count = cursor.fetchone()[0]

    bot.send_message(message.chat.id, 'Статистика за последниe 24 часа')


# Handle the /stats command
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    today_button = types.InlineKeyboardButton(text='За сегодня', callback_data='stats_today')
    total_button = types.InlineKeyboardButton(text='Общая статистика', callback_data='stats_total')
    keyboard.add(today_button, total_button)

    bot.send_message(message.chat.id, 'Выбери, какую статистику ты хочешь получить:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('stats_'))
def handle_stats_callback(call):
    if call.data == 'stats_today':
        cursor.execute('SELECT COUNT(*) FROM referrals '
                       'WHERE created_at >= datetime("now", "-1 day")')
        count = cursor.fetchone()[0]
        text = 'За последние 24 часа бот был запущен {} раз.'.format(count)
    else:
        cursor.execute('SELECT COUNT(*) FROM referrals')
        count = cursor.fetchone()[0]
        text = 'Общее количество запусков бота: {}.'.format(count)

    bot.send_message(call.message.chat.id, text)


# TODO : [] - Finish the feedback logic
# @bot.message_handler(commands=['feedback'])
# def handle_feedback(message):
#     bot.send_message(message.chat.id, 'Оставьте ваш отзыв о работе бота:')
#     bot.register_next_step_handler(message, save_feedback)
#
#
# def save_feedback(message):
#     cursor.execute('INSERT INTO feedback (user_id, message) VALUES (?, ?)', (message.chat.id, message.text))
#     conn.commit()
#     bot.send_message(message.chat.id, 'Спасибо за ваш отзыв! Он был успешно сохранен.')


@bot.message_handler(commands=['set_greeting'])
def handle_set_greeting(message):
    bot.send_message(message.chat.id, 'Введите новый текст приветствия')
    bot.register_next_step_handler(message, set_greeting)


def set_greeting(message):
    global greeting
    greeting = message.text
    bot.send_message(message.chat.id, 'Новое приветствие установлено\n{}'.format(greeting))

# TODO : [] - Finish the logic of changing the greeting
# @bot.message_handler(commands=['set_greeting'])
# def handle_set_greeting(message):
#     bot.send_message(message.chat.id,
#                      'Отправь мне текст приветствия или текстовый файл, который я буду использовать в качестве приветственного сообщения.')
#
#     bot.register_next_step_handler(message, set_greeting)
#
#
# def set_greeting(message):
#     if message.text and message.text.strip():
#         cursor.execute('UPDATE users SET greeting_text=? WHERE user_id=?', (message.text, message.chat.id))
#         conn.commit()
#         bot.send_message(message.chat.id, 'Теперь я буду использовать этот текст в качестве приветственного сообщения.')
#     elif message.document and message.document.mime_type.startswith('text'):
#         cursor.execute('UPDATE users SET greeting_text=? WHERE user_id=?', (message.text, message.chat.id))
#         conn.commit()
#         bot.send_message(message.chat.id, 'Теперь я буду использовать этот текст в качестве приветственного сообщения.')
#
#
# def get_greeting_message(user_id, bot):
#     cursor.execute('SELECT greeting_text FROM users WHERE user_id=?', (user_id,))
#     row = cursor.fetchone()
#     if row and row[0]:
#         return row[0]
#     else:
#         greeting_message = bot.bot_data['greeting_messages'].get(user_id)
#         if greeting_message:
#             if isinstance(greeting_message, str):
#                 return greeting_message
#             elif isinstance(greeting_message, dict):
#                 if greeting_message['type'] == 'text':
#                     return bot.send_message(chat_id=user_id, text=greeting_message['content'])
#                 elif greeting_message['type'] == 'document':
#                     return bot.send_document(chat_id=user_id, document=greeting_message['content'])
#         else:
#             return None


bot.polling()
