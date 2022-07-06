import sqlite3
import datetime


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def add_product(self, title, price, description, pic):
        try:
            binary = sqlite3.Binary(pic)
            self.__cur.execute("INSERT INTO products VALUES(NULL, ?, ?, ?, ?)", (title, price, description, binary))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При добавлении товара в БД произошла ошибка")
            print(str(e))
            return False
        return True

    def add_customer(self, name, phone_number, password):
        try:
            self.__cur.execute("INSERT INTO customers VALUES(NULL, ?, ?, ?)", (name, phone_number, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При добавлении заказчика в БД произошла ошибка")
            print(str(e))
            return False
        return True

    def add_product_in_basket(self, customer_id, product_id, number):
        try:
            self.__cur.execute("INSERT INTO baskets VALUES(?, ?, ?)", (customer_id, product_id, number))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При добавлении товара в корзину произошла ошибка")
            print(str(e))
            return False
        return True

    def add_order(self, customer_id, address, is_serial, day_of_the_week, list_of_products, list_of_numbers):
        date = datetime.date.today()
        if is_serial:
            status = 0
        else:
            status = 1
        try:
            self.__cur.execute("INSERT INTO orders VALUES(NULL, ?, ?, ?, ?, ?, ?)", (customer_id,
                                                                                     date, address, is_serial,
                                                                                     status, day_of_the_week))
            self.__db.commit()
            order_id = self.__cur.lastrowid
        except sqlite3.Error as e:
            print("При добавлении заказа в БД произошла ошибка")
            print(str(e))
            return False
        for i in range(len(list_of_numbers)):
            self.add_order_product(order_id, list_of_products[i], list_of_numbers[i])
        return True

    def add_order_product(self, order_id, product_id, number):
        try:
            self.__cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = self.__cur.fetchone()
            price = product['price']
            self.__cur.execute("INSERT INTO order_products VALUES(?, ?, ?, ?)", (order_id, product_id, price, number))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При добавлении заказанного товара в БД произошла ошибка")
            print(str(e))
            return False
        return True

    def get_product_by_id(self, product_id):
        try:
            self.__cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Товар не найден")
                return False
        except sqlite3.Error as e:
            print("Ошибка чтения из БД")
            print(str(e))
            return False
        return res

    def get_product_by_title(self, title):
        try:
            self.__cur.execute("SELECT * FROM products WHERE title = ?", (title,))
            res = self.__cur.fetchone()
            if not res:
                print("Товар не найден")
                return False
        except sqlite3.Error as e:
            print("Ошибка чтения из БД")
            print(str(e))
            return False
        return res

    def get_all_products(self):
        try:
            self.__cur.execute("SELECT * FROM products")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД" + str(e))

        return False

    def get_customer_by_id(self, customer_id):
        try:
            self.__cur.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return False

    def get_customer_by_phone_number(self, phone_number):
        try:
            self.__cur.execute(f"SELECT * FROM customers WHERE phone_number = ?", (phone_number,))
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return False

    def get_all_customers(self):
        try:
            self.__cur.execute("SELECT * FROM customers")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return False

    def get_order(self, order_id):
        try:
            self.__cur.execute("SELECT * FROM orders WHERE id=?", (order_id,))
            res = self.__cur.fetchone()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return False

    def get_all_orders(self):
        try:
            self.__cur.execute("SELECT * FROM orders")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return False

    def get_customer_orders(self, customer_id):
        try:
            self.__cur.execute("SELECT * FROM orders WHERE customer_id=?", (customer_id,))
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

        return False

    def get_order_products(self, order_id):
        try:
            self.__cur.execute("SELECT p.title, op.number "
                               "FROM order_products op JOIN products p "
                               "ON op.product_id = p.id AND op.order_id = ? ", (order_id,))
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

        return False

    def get_products_in_customer_basket(self, customer_id):
        try:
            self.__cur.execute("SELECT p.id, p.title, b.number "
                               "FROM baskets b JOIN products p "
                               "ON b.product_id = p.id AND b.customer_id = ? ", (customer_id,))
            res = self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД" + str(e))
            return False
        return res

    def is_registration_exist(self, phone_number):
        try:
            self.__cur.execute(f"SELECT * FROM customers WHERE phone_number = ?", (phone_number,))
            res = self.__cur.fetchall()
            if res:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

    def delete_product(self, product_id):
        try:
            self.__cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении товара из БД произошла ошибка")
            print(str(e))
            return False
        return True

    def delete_customer(self, customer_id):
        try:
            self.__cur.execute("DELETE FROM baskets WHERE customer_id = ?", (customer_id,))
            self.__db.commit()
            self.__cur.execute("SELECT * FROM orders WHERE customer_id = ?", (customer_id,))
            orders_id = self.__cur.fetchall()
            for el in orders_id:
                self.__cur.execute("DELETE FROM order_products WHERE order_id = ?", (el['id'],))
                self.__db.commit()
            self.__cur.execute("DELETE FROM orders WHERE customer_id = ?", (customer_id,))
            self.__db.commit()
            self.__cur.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении пользователя из БД произошла ошибка")
            print(str(e))
            return False
        return True

    def delete_product_from_basket(self, customer_id, product_id):
        try:
            self.__cur.execute("DELETE FROM baskets WHERE customer_id = ? AND product_id = ?", (customer_id,
                                                                                                product_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении товара из корзины произошла ошибка")
            print(str(e))
            return False
        return True

    def delete_customer_basket(self, customer_id):
        try:
            self.__cur.execute("DELETE FROM baskets WHERE customer_id = ?", (customer_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении корзины произошла ошибка")
            print(str(e))
            return False
        return True

    def delete_order(self, order_id):
        try:
            self.__cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении заказа из БД произошла ошибка")
            print(str(e))
            return False
        return True

    def delete_order_product(self, order_id, product_id):
        try:
            self.__cur.execute("DELETE FROM order_products WHERE order_id = ? AND product_id = ?",
                               (order_id, product_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При удалении товара из заказа произошла ошибка")
            print(str(e))
            return False
        return True

    def change_product_price(self, product_id, price):
        try:
            self.__cur.execute("UPDATE products SET price = ? WHERE id = ?", (price, product_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При модификации произошла ошибка" + str(e))
            return False
        return True

    def change_product_description(self, product_id, description):
        try:
            self.__cur.execute("UPDATE products SET description = ? WHERE id = ?", (description, product_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При модификации произошла ошибка" + str(e))
            return False
        return True

    def change_order_status(self, order_id, status):
        try:
            self.__cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("При модификации произошла ошибка" + str(e))
            return False
        return True
