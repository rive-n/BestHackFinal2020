from scripts import checkForExistence, checkPermeation, getPerm, \
    uniqueLogin, checkPassAndCpPass, createNewUser, createQuery, checkForToken, \
    getTicketsAmount, allDataFromTickets
from flask import Flask, render_template, \
    request, redirect, session
from sql_filters import filtr, copyPasswordFiltr
import time


app = Flask(__name__)
app.static_url_path = '/static'
app.secret_key = 'motherhackers'
app.debug = True


@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')
        print(username, password)
        # clear session for debugging...
        session.clear()
        print(session)
        # Фильтрация от SQLinj
        if filtr(username, password) is not None:
            username, password = filtr(username, password)
            # Проверка на существование
            if checkForExistence(username, password):
                # Если логин и пароль есть в системе и пароль совпадает с паролем в БД
                if checkPermeation(username):
                    # Если юзер - админ: редирет в админку
                    if 'permit' not in session:
                        session['permit'] = {'perm': f'{getPerm(username)}'}
                        session['login'] = {'log' : f"{username}"}
                    return redirect('/login/admin')
                else:
                    # Иначе редирект на юзерский мейнпейдж
                    if 'permit' not in session:
                        session['permit'] = {'perm': f'{getPerm(username)}'}
                        session['login'] = {'log': f"{username}"}
                    return redirect('/mainPage')
    else:
        pass

    return render_template("index.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        login_username = request.form.get("Username")
        login_password = request.form.get("Password")
        cppassword = request.form.get("Copypassword")

        # Фильтруем все от скулей и бяки
        if filtr(login_username, login_password) is not None and copyPasswordFiltr(cppassword) is not None:
            login_username, login_password = filtr(login_username, login_password)
            cppassword = copyPasswordFiltr(cppassword)
            print(login_username, login_password, cppassword)
            # Проверка, что пароли совпадают
            if checkPassAndCpPass(login_password, cppassword):
                # Если логин есть в системе - возвращаем регу. Иначе - создаем юзера с не админ пермитом
                if not uniqueLogin(login_username):
                    return render_template('reg.html')
                else:
                    createNewUser(login_username, login_password)
                    return redirect('/login')
    return render_template('registration.html')


@app.route('/login/admin', methods= ['GET', 'POST'])
def adminLogin():
    if 'permit' in session:
        print(session['permit']['perm'])
        print(session)
        if session['permit']['perm'] == "True":
            if request.method == "GET":
                createQuery(session['login']['log'])
            elif request.method == 'POST':
                adminToken = request.form.get('AdminToken')
                if checkForToken(adminToken, session['login']['log']):
                    return redirect('/mainPage')
            return render_template('adminMdLogin.html')
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/mainPage', methods= ['GET', 'POST'])
def mainPage():
    if 'permit' in session:
        print(session['permit']['perm'])
        print(session)
        if session['permit']['perm'] != "None":
            if request.method == "GET":
                ticket = request.args.get('do', default="#", type=str)
                print(ticket)
                print(getTicketsAmount())
                lst = allDataFromTickets()
                print(lst[1][0])
                return render_template('newPostTemplate.html',
                                       posts = lst,
                                       user_name = session['login']['log'],
                                       user_permit = session['permit']['perm'])
        else:
            return redirect('/login')
    else:
        return redirect('/login')


@app.route('/admin/mainPage')
def adminMainPage():
    return "Chaoo"