import sqlite3
import os
from flask import Flask, flash, g, render_template, request, redirect, url_for, make_response
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from FDataBase import FDataBase
from UserLogin import UserLogin

DATABASE = 'tmp/online_store.db'
DEBUG = True
SECRET_KEY = 'dsfKL5K5l2*^%)'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'online_store.db')))

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)

    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route('/load_image/<product_id>')
def load_image(product_id):
    db = get_db()
    dbase = FDataBase(db)

    product = dbase.get_product_by_id(product_id)
    img = product['pic']

    if not img:
        print("No...")
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.cursor().execute("PRAGMA foreign_keys=on")
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    data_base = connect_db()

    with app.open_resource('online_store.sql', mode='r') as f:
        data_base.cursor().executescript(f.read())
    data_base.commit()

    data_base.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


def is_png(filename):
    file_type = filename.rsplit('.', 1)[1]
    if file_type == "png" or file_type == "PNG":
        return True
    return False


log = 'log'
pas = 'pas'


@app.route('/')
def index():
    return render_template('home_page.html')


@app.route('/registration', methods=['post', 'get'])
def registration():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) == 0 or len(request.form['phone_number']) == 0 \
                or len(request.form['password']) == 0:
            flash('Вы заполнили не все поля.', category='fail')
        elif dbase.is_registration_exist(request.form['phone_number']):
            flash('Пользователь с введенным номером телефона уже существует. Попробуйте еще раз.', category='fail')
        elif len(request.form['phone_number']) != 11:
            flash('Неверная длина номера телефона (должна быть 11).', category='fail')
        else:
            try:
                phone_number = int(request.form['phone_number'])
                password = generate_password_hash(request.form['password'])
                res = dbase.add_customer(request.form['name'], phone_number, password)

                if res:
                    flash('Вы успешно зарегистрировались. Для авторизации перейдите на главную страницу и нажмите на '
                          'кнопку "Авторизация". ', category='success')
                else:
                    flash('При регистрации произошла ошибка.', category='fail')
            except ValueError:
                flash('Неправильно введен номер телефона.', category='fail')

    return render_template('registration.html')


@app.route('/login', methods=['post', 'get'])
def login():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        user = dbase.get_customer_by_phone_number(request.form['phone_number'])

        if len(request.form['phone_number']) == 0 or len(request.form['password']) == 0:
            flash('Вы заполнили не все поля.')
        elif not check_password_hash(user['password'], request.form['password']):
            flash('Неверный пароль. Попробуйте еще раз.')
        elif user:
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect(url_for('catalog'))
        else:
            flash('Вы ввели неверный логин/пароль. Попробуйте еще раз.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/catalog', methods=['post', 'get'])
@login_required
def catalog():
    db = get_db()
    dbase = FDataBase(db)

    products = dbase.get_all_products()
    if request.method == 'POST':
        res = []
        s = request.form['search'].lower()

        if len(s) != 0:
            for el in products:
                title = el['title'].lower()
                if s in title:
                    res.append(el)
            products = res

        try:
            from_price = int(request.form['from'])
            to_price = int(request.form['to'])

            if from_price < to_price:
                res = []
                for el in products:
                    if from_price <= el['price'] <= to_price:
                        res.append(el)
                products = res
        except ValueError:
            return render_template('catalog.html', products=products, customer_id=current_user.get_id())
    return render_template('catalog.html', products=products, customer_id=current_user.get_id())


@app.route('/add_to_basket/<product_id>', methods=['post', 'get'])
@login_required
def add_to_basket(product_id):
    db = get_db()
    dbase = FDataBase(db)

    product = dbase.get_product_by_id(product_id)
    customer_id = current_user.get_id()
    if request.method == 'POST':
        number = request.form['number']
        try:
            number = int(number)
            if number <= 0:
                flash('Введено некорректное количество.', category='fail')
                return render_template('add_to_basket.html', product=product)
        except ValueError:
            flash('Поле заполнено некорректно.', category='fail')
            return render_template('add_to_basket.html', product=product)

        res = dbase.add_product_in_basket(customer_id, product_id, number)
        if res:
            flash('Товар добавлен в вашу корзину!', category='success')
        else:
            flash('Заказываемый товар уже есть в вашей корзине.', category='fail')

    return render_template('add_to_basket.html', product=product)


@app.route('/choose_order_type/<product_id>')
@login_required
def choose_order_type(product_id):
    return render_template('choose_order_type.html', product_id=product_id)


@app.route('/product_order/<product_id>', methods=['post', 'get'])
@login_required
def product_order(product_id):
    db = get_db()
    dbase = FDataBase(db)

    customer_id = current_user.get_id()
    product = dbase.get_product_by_id(product_id)

    if request.method == 'POST':
        number = request.form['number']
        card_number = request.form['card_number']
        address = request.form['address']

        if len(number) == 0 or len(card_number) == 0 or len(address) == 0:
            flash('Вы заполнили не все поля.', category='fail')
            return render_template('product_order.html', product=product)
        else:
            try:
                number = int(number)
                card_number = int(card_number)

                if number <= 0:
                    flash('Введено некорректное количество.', category='fail')
                    return render_template('product_order.html', product=product)
                if card_number <= 0 or len(str(card_number)) != 16:
                    flash('Введен некорректный номер банковской карты.', category='fail')
                    return render_template('product_order.html', product=product)
            except ValueError:
                flash('Неверно заполнены поля "Количество"/"Номер банковской карты".', category='fail')
                return render_template('product_order.html', product=product)

        total_sum = product['price'] * number

        list_of_products = []
        list_of_numbers = []
        list_of_products.append(product_id)
        list_of_numbers.append(number)

        dbase.add_order(customer_id, address, 0, -1, list_of_products, list_of_numbers)
        flash(f'Вы успешно оформили заказ на сумму {total_sum} руб.', category='success')

    return render_template('product_order.html', product=product)


@app.route('/serial_product_order/<product_id>', methods=['post', 'get'])
@login_required
def serial_product_order(product_id):
    db = get_db()
    dbase = FDataBase(db)

    customer_id = current_user.get_id()
    product = dbase.get_product_by_id(product_id)

    if request.method == 'POST':
        number = request.form['number']
        card_number = request.form['card_number']
        address = request.form['address']
        try:
            day_of_week = int(request.form['day_of_week'])
        except KeyError:
            flash('Вы не указали день недели.', category='fail')
            return render_template('serial_product_order.html', product=product)

        if len(number) == 0 or len(card_number) == 0 or len(address) == 0:
            flash('Вы заполнили не все поля.', category='fail')
            return render_template('serial_product_order.html', product=product)
        else:
            try:
                number = int(number)
                card_number = int(card_number)

                if number <= 0:
                    flash('Введено некорректное количество.', category='fail')
                    return render_template('serial_product_order.html', product=product)
                if card_number <= 0 or len(str(card_number)) != 16:
                    flash('Введен некорректный номер банковской карты.', category='fail')
                    return render_template('serial_product_order.html', product=product)
            except ValueError:
                flash('Неверно заполнены поля "Количество"/"Номер банковской карты".', category='fail')
                return render_template('serial_product_order.html', product=product)

        total_sum = product['price'] * number

        list_of_products = []
        list_of_numbers = []
        list_of_products.append(product_id)
        list_of_numbers.append(number)

        dbase.add_order(customer_id, address, 1, day_of_week, list_of_products, list_of_numbers)
        flash(f'Вы успешно оформили серийный заказ на сумму {total_sum} руб.', category='success')
    return render_template('serial_product_order.html', product=product)


@app.route('/customer_basket', methods=['post', 'get'])
@login_required
def customer_basket():
    db = get_db()
    dbase = FDataBase(db)

    customer_id = current_user.get_id()
    products = dbase.get_products_in_customer_basket(customer_id)
    total_sum = 0
    for el in products:
        total_sum += el['price'] * el['number']
    if request.method == 'POST':
        customer_id = current_user.get_id()
        product_id = request.form['delete']
        dbase.delete_product_from_basket(customer_id, product_id)
        return redirect(url_for('customer_basket'))
    return render_template('customer_basket.html', products=products, total_sum=total_sum)


@app.route('/customer_basket_order', methods=['post', 'get'])
@login_required
def customer_basket_order():
    db = get_db()
    dbase = FDataBase(db)

    customer_id = current_user.get_id()
    products = dbase.get_products_in_customer_basket(customer_id)
    total_sum = 0
    for el in products:
        total_sum += el['price'] * el['number']

    if request.method == 'POST':
        card_number = request.form['card_number']
        address = request.form['address']

        if len(card_number) == 0 or len(address) == 0:
            flash('Вы заполнили не все поля.', category='fail')
        else:
            try:
                card_number = int(card_number)

                if card_number <= 0 or len(str(card_number)) != 16:
                    flash('Введен некорректный номер банковской карты.', category='fail')
                    return render_template('customer_basket_order.html', products=products)

                list_of_products = []
                list_of_numbers = []
                for i in range(len(products)):
                    list_of_products.append(products[i]['id'])
                    list_of_numbers.append(products[i]['number'])

                dbase.add_order(customer_id, address, 0, -1, list_of_products, list_of_numbers)
                dbase.delete_customer_basket(customer_id)
                flash(f'Вы успешно заказали товары из корзины на сумму {total_sum} руб.', category='success')
            except ValueError:
                flash('Неверно заполнено поле "Номер банковской карты".', category='fail')
                return render_template('customer_basket_order.html', products=products)

    return render_template('customer_basket_order.html', products=products, total_sum=total_sum)


@app.route('/customer_orders', methods=['post', 'get'])
@login_required
def customer_orders():
    db = get_db()
    dbase = FDataBase(db)

    customer_id = current_user.get_id()
    orders = dbase.get_customer_orders(customer_id)

    orders_products = []
    for el in orders:
        order_products = dbase.get_order_products(el['id'])
        orders_products.append(order_products)

    return render_template('customer_orders.html', orders=orders, orders_products=orders_products)


@app.route('/admin_login', methods=['post', 'get'])
def admin_login():
    if request.method == "POST":
        if request.form['login'] == log and request.form['password'] == pas:
            return redirect(url_for('admin_home_page'))
        elif len(request.form['login']) == 0 or len(request.form['password']) == 0:
            flash('Вы заполнили не все поля.')
        else:
            flash('Вы ввели неверный логин/пароль. Попробуйте еще раз.')

    return render_template('admin_login.html')


@app.route('/admin_home_page')
def admin_home_page():
    return render_template('admin_home_page.html')


@app.route('/admin_customers', methods=['post', 'get'])
def admin_customers():
    db = get_db()
    dbase = FDataBase(db)

    customers = dbase.get_all_customers()

    if request.method == 'POST':
        customer_id = request.form['delete']
        dbase.delete_customer(customer_id)
        return redirect(url_for('admin_customers'))
    return render_template('admin_customers.html', customers=customers)


@app.route('/admin_products', methods=['post', 'get'])
def admin_products():
    db = get_db()
    dbase = FDataBase(db)

    products = dbase.get_all_products()

    if request.method == 'POST':
        product_id = request.form['delete']
        dbase.delete_product(product_id)
        return redirect(url_for('admin_products'))

    return render_template('admin_products.html', products=products)


@app.route('/admin_products/price_change/<product_id>', methods=['post', 'get'])
def product_price_change(product_id):
    db = get_db()
    dbase = FDataBase(db)

    product = dbase.get_product_by_id(product_id)
    if request.method == 'POST':
        new_price = request.form['price']
        dbase.change_product_price(product_id, new_price)
        return redirect(url_for('admin_products', product_id=product_id))
    return render_template('admin_product_price_change.html', product=product)


@app.route('/admin_products/description_change/<product_id>', methods=['post', 'get'])
def product_description_change(product_id):
    db = get_db()
    dbase = FDataBase(db)

    product = dbase.get_product_by_id(product_id)
    if request.method == 'POST':
        new_description = request.form['description']
        dbase.change_product_description(product_id, new_description)
        return redirect(url_for('admin_products', product_id=product_id))
    return render_template('admin_product_description_change.html', product=product)


@app.route('/admin_add_product', methods=['post', 'get'])
def admin_add_product():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        file = request.files['file']

        if len(title) == 0 or len(price) == 0 or len(description) == 0:
            flash('Вы заполнили не все поля.', category='fail')
            return render_template('admin_add_product.html')

        if not file:
            file = app.open_resource(app.root_path + url_for('static', filename='images/no-image.png'), "rb")
            file.filename = 'no-image.png'

        try:
            price = int(price)
            if price <= 0:
                flash('Некорректная цена.', category='fail')
                return render_template('admin_add_product.html')
        except ValueError:
            flash('Неверно заполнено поле "Цена".', category='fail')
            return render_template('admin_add_product.html')

        if file and is_png(file.filename):
            try:
                img = file.read()
                dbase.add_product(title, price, description, img)
                flash('Продукт добавлен!', category='success')
            except FileExistsError:
                flash('Указанного файла не существует.', category='fail')
            except FileNotFoundError:
                flash('Файл не найден.', category='fail')
            except:
                flash('Not work')
    return render_template('admin_add_product.html')


@app.route('/admin_orders')
def admin_orders():
    db = get_db()
    dbase = FDataBase(db)

    orders = dbase.get_all_orders()

    customers = []
    for el in orders:
        customer = dbase.get_customer_by_id(el['customer_id'])
        customers.append(customer)

    return render_template('admin_orders.html', orders=orders, customers=customers)


@app.route('/admin_orders/status_change/<order_id>', methods=['post', 'get'])
def admin_order_status_change(order_id):
    db = get_db()
    dbase = FDataBase(db)

    order = dbase.get_order(order_id)
    customer = dbase.get_customer_by_id(order['customer_id'])

    if request.method == 'POST':
        try:
            new_status = int(request.form['status'])
            if new_status not in range(0, 3):
                flash('Вы ввели некорректное число.', category='fail')
                return render_template('admin_order_status_change.html', order=order, customer=customer)
            dbase.change_order_status(order_id, new_status)
            flash('Статус успешно изменен', category='success')
        except ValueError:
            flash('Необходимо ввести число.', category='fail')
            return render_template('admin_order_status_change.html', order=order, customer=customer)

    return render_template('admin_order_status_change.html', order=order, customer=customer)


if __name__ == '__main__':
    app.run(debug=True)
