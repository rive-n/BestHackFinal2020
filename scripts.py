from database import curs, conn
import os

def checkForExistence(username, password):
    curs.execute("""
    SELECT login FROM logins where login = '{}'
    """.format(str(username)))
    data = curs.fetchall()
    print(data)
    if len(data) > 0:
        # pass_check проверка пароля
        if checkPassword(password, username):
            return True
        else:
            return False
    else:
        return False


def checkPassword(password, username):
    curs.execute("""
    SELECT password FROM logins WHERE login = '{}'
    """.format(str(username)))
    chk_password = curs.fetchall()
    if len(chk_password) > 0:
        if str(chk_password[0][0]) == str(password):
            return True
        else:
            return False


def checkPermeation(username):
    curs.execute("""
    SELECT permeation FROM logins where login = '{}'
    """.format(username))
    perm = curs.fetchall()

    # Проверка на админа
    if len(perm) > 0:
        # Распаршиваю кортеж чтоб выудить бул значение
        if perm[0][0]:
            return True
            # Если админ - возвращаем тру
        else:
            return False


def getPerm(username):
    curs.execute("""
    SELECT permeation FROM logins where login = '{}'
    """.format(username))
    perm = curs.fetchall()
    if len(perm) > 0:
        return perm[0][0]
    else:
        return None


# ------------------------------------------------------------------------------------------------
# user side. Admin side upper


def uniqueLogin(username):
    curs.execute("""
    SELECT login FROM logins where login = '{}'
    """.format(username))
    copy = len(curs.fetchall())
    print(str(copy) + " IS COPY")
    if copy > 0:
        return False
    else:
        return True


def checkPassAndCpPass(password, cppass):
    if password == cppass:
        return True
    else:
        return False


def createNewUser(username, password):
    curs.execute("""
    INSERT INTO logins VALUES ('{}', '{}', '{}')
    """.format(username, password, False))
    conn.commit()


# ------------------------------------------------------------------------------------------------
# bot sending secure md5 token (key)


def createQuery(username):
    curs.execute("""
    UPDATE logins SET requiretoken = True WHERE login = '{}' and permeation = '{}'
    """.format(username, True))
    conn.commit()


def checkForToken(token, username):
    curs.execute("""
    SELECT admintoken FROM privatetokens WHERE telegram_id = (SELECT logins.telegram_id FROM logins where requiretoken = True)
    """)
    token_ = curs.fetchall()
    print(token_[0][0])
    if len(token_) > 0:
        if str(token) == str(token_[0][0]):
            curs.execute("""
            UPDATE logins SET requiretoken = False WHERE login = '{}' and permeation = '{}'
            """.format(username, True))
            return True
    else:
        return False


# ------------------------------------------------------------------------------------------------
# hardcoding time...
# server be like c:/../besthack2020finals/storage

def getTicketsAmount():
    curs.execute("""
    SELECT amount FROM tickets_amount
    """)
    amount = curs.fetchall()
    return str(amount[0][0])


def allDataFromTickets():
    curs.execute("""
    SELECT * FROM tickets_info
    """)
    ticketInfo = curs.fetchall()
    return ticketInfo