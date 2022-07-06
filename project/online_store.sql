CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    pic BLOB
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number INTEGER NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS baskets (
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    PRIMARY KEY (customer_id, product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    formation_date DATE NOT NULL,
    address TEXT NOT NULL,         -- адрес доставки
    is_serial INTEGER NOT NULL,    -- 0 - обычный заказ, 1 - серийный
    status INTEGER NOT NULL,       -- 0 - в процессе отправки (для серийных заказов), 1 - отправлено, 2 - доставлено
    day_of_the_week INTEGER,       -- день недели, в который будет доставляться заказ (понедельник - 0, воскресенье - 6)
                                         -- -1 - для обычного заказа
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_products (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    number INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
