# -*- coding: utf-8 -*-
import os
import time
import telebot
import difflib
import hashlib, random
from flask import Flask, request
from telegram_bot.database import curs, conn
from telebot import apihelper, types
from telegram_bot.read_file import fdata, ans_for_q, phr_answ

apihelper.proxy = {}
TOKEN = '-'


bot = telebot.TeleBot(TOKEN)


def logInChat(user_id):
    curs.execute("""
    INSERT INTO telegram_bot VALUES ('{}', '{}', {}, {})
    """.format(user_id, None, False, True))
    conn.commit()


def userInDatabase(user_id):
    curs.execute("""
    SELECT username FROM telegram_bot where username like '{}'
    """.format(user_id))
    data = curs.fetchall()
    # Если юзер зареган в боте - тру, иначе фолс. Проверка на антиспам бота
    if len(data) > 0:
        return True
    else:
        return False


def botStarted(user_id):
    curs.execute("""
        select chat_started from telegram_bot where username like '{}'
        """.format(user_id))

    data = curs.fetchall()

    try:
        if len(data) > 0 :
            if data[0][0] != "None":
                if data[0][0]:
                    return True
                else:
                    return False
            else:
                return False
    except Exception:
        bot.send_message(user_id, "I can't understand you. Try to start me...")
        return False


def chatInState(used_id, chat_state):
    curs.execute("""
    select chat_state from telegram_bot where username like '{}'
    """.format(used_id))
    data = curs.fetchall()
    # Если чат в стейте - Тру. Иначе Фолс. Проверка на то, чтоб бот не спамил
    if chat_state == data[0][0]:
        return True
    else:
        return False


def setChatInState(user_id, chat_state):
    curs.execute("""
                UPDATE telegram_bot set chat_state = '{}' WHERE username = '{}'
                """.format(chat_state, user_id))
    conn.commit()


def telebotStartButtons(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='questions'))
    markup.add(types.InlineKeyboardButton(text='Задать свой вопрос', callback_data='answer_question'))
    markup.add(types.InlineKeyboardButton(text='Подать заявку', callback_data='apply'))
    markup.add(types.InlineKeyboardButton(text='Админ токен', callback_data='aToken'))
    bot.send_message(message.chat.id, text="Пожалуйста, укажите что Вам нужно :)", reply_markup=markup)


def telebotNewTicketButtons(message):
    ticketMarkup = types.InlineKeyboardMarkup()
    ticketMarkup.add(types.InlineKeyboardButton(text='Составить тикет', callback_data='ticket_true'))
    ticketMarkup.add(types.InlineKeyboardButton(text='Главное меню', callback_data='ticket_false'))
    bot.send_message(message.chat.id, text="Так как бот не в силе ответить на данный вопрос, вы "
                                           "можете составить тикет по этому поводу: ", reply_markup=ticketMarkup)


@bot.callback_query_handler(func=lambda call: True)
def botQueryHandler(call):
    if botStarted(call.message.chat.id):
        bot.answer_callback_query(callback_query_id=call.id, text='Обрабатываю данные.')
        answer = ''
        if call.data == 'questions':
            answer = "Вывожу список вопросов и ответов на них :)"
        elif call.data == 'answer_question':
            answer = "Прошу, задайте Ваш вопрос и я постараюсь на него ответить :)"
        elif call.data == 'apply':
            answer = "Введите ваше ФИО и заявку на рассмотрение: "
        elif call.data == 'ticket_true':
            answer = "Перенаправляю на составление тикета"
        elif call.data == 'ticket_false':
            answer = 'Перенаправляю в главное меню :)'
        elif call.data == 'aToken':
            curs.execute("""
            SELECT telegram_id FROM logins WHERE requiretoken = True
            """)
            dt = curs.fetchall()
            print(dt)

            if str(call.from_user.id) in str(dt):
                genToken = generateToken()
                answer = f"Here is your Token for admin lk: {genToken}"
                if alreadyExist(str(call.from_user.id)) is not None:
                    curs.execute("""
                    UPDATE privatetokens SET admintoken = '{}' WHERE telegram_id = '{}'
                    """.format(genToken, str(call.from_user.id)))
                    conn.commit()
                else:
                    curs.execute("""
                    INSERT INTO privatetokens VALUES ('{}', '{}')
                    """.format(genToken, str(call.from_user.id)))
                    conn.commit()
            else:
                answer = "You have no admin perms :("

        else:
            answer = "Chose any button please."

        setChatInState(call.message.chat.id, call.data)
        bot.send_message(call.message.chat.id, answer)

        if call.data == 'answer_question':
            curs.execute("""
                            UPDATE telegram_bot set question_ans = '{}' WHERE username = '{}'
                            """.format(True, call.message.chat.id))
            conn.commit()

        elif call.data == 'questions':
            bot.send_message(call.message.chat.id, ans_for_q)
            setChatInState(call.message.chat.id, 'questions')
        elif call.data == 'apply':
            curs.execute("""
                                        UPDATE telegram_bot set request = '{}' WHERE username = '{}'
                                        """.format(True, call.message.chat.id))
            conn.commit()
            bot.send_message(call.message.chat.id, """
                        Правила составления тикета:
                        Первая строка - Ваше ФИО. 
                        Желательно далее пропустить строку. 
                        Начиная с 3тьей: основная суть Вашего обращения.
                        """)
            setChatInState(call.message.chat.id, 'questions')
        elif call.data == 'ticket_false':
            telebotStartButtons(call.message)
    else:
        bot.send_message(call.message.chat.id, 'Cant understand you. Try: /start')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def answerQuestionFunc(message):
    data = None
    if botStarted(message.from_user.id):
        # Проверка на галочку при вопросе
        curs.execute("""
        SELECT question_ans FROM telegram_bot WHERE username = '{}'
        """.format(message.from_user.id))
        data = curs.fetchall()
        if len(data) > 0:
            if data[0][0] is not False:
                if data[0][0]:
                    curs.execute("""
                                            UPDATE telegram_bot set question_ans = '{}' WHERE username = '{}'
                                            """.format(False, message.from_user.id))
                    conn.commit()
                    bot.send_message(message.chat.id, "I've got your question: " + message.text)
                    print(readFromScratch(message.text))
                    if readFromScratch(message.text) is not None:
                        bot.send_message(message.chat.id, phr_answ.splitlines()[readFromScratch(message.text)])
                        telebotStartButtons(message)
                    else:
                        bot.send_message(message.chat.id, "Простите, я не могу ответить на этот вопрос..")
                        telebotNewTicketButtons(message)

        # Проверка на галочку на создании тикета (пишу в 7 утра прив)
        curs.execute("""
        SELECT request from telegram_bot WHERE username = '{}'
        """.format(message.from_user.id))
        ticket_create = curs.fetchall()
        if len(ticket_create) > 0:
            if ticket_create[0][0] is not False:
                if ticket_create[0][0]:
                    curs.execute("""
                    UPDATE telegram_bot SET request = '{}' WHERE username = '{}'
                    """.format(False, message.from_user.id))
                    conn.commit()
                    bot.send_message(message.chat.id, "I've got your ticket: \n" + message.text)
                    createTicketFile(message.from_user.id, message.text)
                    telebotStartButtons(message)

    elif str(message.text).lower() == '/start' or str(message.text).lower() == '!start' and data is not True:
        # print(message.from_user.id)
        if not userInDatabase(message.from_user.id):
            logInChat(message.from_user.id)

        if not chatInState(message.from_user.id, 'start'):
            setChatInState(message.from_user.id, 'start')
            bot.send_message(message.chat.id, """
                        Вас приветствует бот-помощник. Позвольте узнать - чем я могу вам помочь?
                        (Тут должны появиться кнопки. Необходимо выбрать нужную опцию).
                        """)

        telebotStartButtons(message)
    else:
        bot.send_message(message.from_user.id, 'Cant understand you. Try: /start')


def readFromScratch(message_text):
    print(fdata.splitlines())
    for word in fdata.splitlines():
        if float(difflib.SequenceMatcher(None, str(message_text).lower(), word.lower()).ratio()) > 0.85:
            return fdata.splitlines().index(word)
    else:
        return None


def generateToken():
    token = hashlib.md5(bytes(random.getrandbits(8)))
    return str(token.hexdigest())


def alreadyExist(tg_id):
    curs.execute("""
    SELECT admintoken FROM privatetokens WHERE telegram_id = '{}'
    """.format(str(tg_id)))
    data = curs.fetchall()
    if len(data) > 0:
        return data[0][0]
    else:
        return None


def createTicketFile(user_id, ticket):
    os.chdir(r'C:\Users\Riven\PycharmProjects\best_hack_2020_finals\storage')
    filename = hashlib.md5(bytes(str(random.getrandbits(8))+ str(user_id), 'UTF-8'))
    with open(f"{str(filename.hexdigest())}.txt",'w') as file:
        file.write(str(ticket))
        file.close()

    dbAddTicketPath(user_id, filename)


def dbAddTicketPath(user_id, filename):
    '''
    if len(compare) > 0:
        curs.execute("""
        UPDATE tickets_info SET ticket_name = '{}', ticket_time ='{}' WHERE ticket_from = '{}'
        """.format(r'\best_hack_2020_finals\storage'+'\\'+str(user_id),str(time.ctime()), user_id))
        conn.commit()
        curs.execute("""
                UPDATE tickets_amount SET amount = (SELECT amount FROM tickets_amount) + 1
                """)
        conn.commit()
    '''
    curs.execute("""
    INSERT INTO tickets_info VALUES ('{}', '{}', '{}')
    """.format(r'\best_hack_2020_finals\storage'+'\\'+str(filename.hexdigest()), str(time.ctime()), user_id))
    conn.commit()
    curs.execute("""
    UPDATE tickets_amount SET amount = (SELECT amount FROM tickets_amount) + 1
    """)
    conn.commit()


bot.polling(none_stop=True)

