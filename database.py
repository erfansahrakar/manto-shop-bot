"""
مدیریت دیتابیس با SQLite
"""
import sqlite3
import json
from datetime import datetime
from config import DATABASE_NAME


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """ایجاد جداول دیتابیس"""
        
        # جدول محصولات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                photo_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول پک‌ها
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS packs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        
        # جدول کاربران
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                full_name TEXT,
                phone TEXT,
                landline_phone TEXT,
                address TEXT,
                shop_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # جدول سبد خرید
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER,
                pack_id INTEGER,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(id),
                FOREIGN KEY (pack_id) REFERENCES packs(id)
            )
        """)
        
        # جدول سفارشات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items TEXT,
                total_price REAL,
                status TEXT DEFAULT 'pending',
                receipt_photo TEXT,
                shipping_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        self.conn.commit()
    
    # ==================== محصولات ====================
    
    def add_product(self, name, description, photo_id):
        """افزودن محصول جدید"""
        self.cursor.execute(
            "INSERT INTO products (name, description, photo_id) VALUES (?, ?, ?)",
            (name, description, photo_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_product(self, product_id):
        """دریافت اطلاعات یک محصول"""
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return self.cursor.fetchone()
    
    def get_all_products(self):
        """دریافت تمام محصولات"""
        self.cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def delete_product(self, product_id):
        """حذف محصول"""
        self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        self.cursor.execute("DELETE FROM packs WHERE product_id = ?", (product_id,))
        self.conn.commit()
    
    # ==================== پک‌ها ====================
    
    def add_pack(self, product_id, name, quantity, price):
        """افزودن پک به محصول"""
        self.cursor.execute(
            "INSERT INTO packs (product_id, name, quantity, price) VALUES (?, ?, ?, ?)",
            (product_id, name, quantity, price)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_packs(self, product_id):
        """دریافت پک‌های یک محصول"""
        self.cursor.execute("SELECT * FROM packs WHERE product_id = ?", (product_id,))
        return self.cursor.fetchall()
    
    def get_pack(self, pack_id):
        """دریافت اطلاعات یک پک"""
        self.cursor.execute("SELECT * FROM packs WHERE id = ?", (pack_id,))
        return self.cursor.fetchone()
    
    def delete_pack(self, pack_id):
        """حذف پک"""
        self.cursor.execute("DELETE FROM packs WHERE id = ?", (pack_id,))
        self.conn.commit()
    
    # ==================== کاربران ====================
    
    def add_user(self, user_id, username, first_name):
        """افزودن کاربر جدید"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        self.conn.commit()
    
    def update_user_info(self, user_id, phone=None, landline_phone=None, address=None, full_name=None, shop_name=None):
        """بروزرسانی اطلاعات کاربر"""
        if phone:
            self.cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        if landline_phone:
            self.cursor.execute("UPDATE users SET landline_phone = ? WHERE user_id = ?", (landline_phone, user_id))
        if address:
            self.cursor.execute("UPDATE users SET address = ? WHERE user_id = ?", (address, user_id))
        if full_name:
            self.cursor.execute("UPDATE users SET full_name = ? WHERE user_id = ?", (full_name, user_id))
        if shop_name:
            self.cursor.execute("UPDATE users SET shop_name = ? WHERE user_id = ?", (shop_name, user_id))
        self.conn.commit()
    
    def get_user(self, user_id):
        """دریافت اطلاعات کاربر"""
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    # ==================== سبد خرید ====================
    
    def add_to_cart(self, user_id, product_id, pack_id, quantity=1):
        """افزودن به سبد خرید"""
        # بررسی اگر قبلاً اضافه شده بود
        self.cursor.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ? AND pack_id = ?",
            (user_id, product_id, pack_id)
        )
        existing = self.cursor.fetchone()
        
        if existing:
            new_quantity = existing[1] + quantity
            self.cursor.execute(
                "UPDATE cart SET quantity = ? WHERE id = ?",
                (new_quantity, existing[0])
            )
        else:
            self.cursor.execute(
                "INSERT INTO cart (user_id, product_id, pack_id, quantity) VALUES (?, ?, ?, ?)",
                (user_id, product_id, pack_id, quantity)
            )
        self.conn.commit()
    
    def get_cart(self, user_id):
        """دریافت سبد خرید کاربر"""
        self.cursor.execute("""
            SELECT c.id, p.name, pk.name, pk.quantity, pk.price, c.quantity
            FROM cart c
            JOIN products p ON c.product_id = p.id
            JOIN packs pk ON c.pack_id = pk.id
            WHERE c.user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()
    
    def clear_cart(self, user_id):
        """خالی کردن سبد خرید"""
        self.cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def remove_from_cart(self, cart_id):
        """حذف آیتم از سبد"""
        self.cursor.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        self.conn.commit()
    
    # ==================== سفارشات ====================
    
    def create_order(self, user_id, items, total_price):
        """ایجاد سفارش جدید"""
        items_json = json.dumps(items, ensure_ascii=False)
        self.cursor.execute(
            "INSERT INTO orders (user_id, items, total_price) VALUES (?, ?, ?)",
            (user_id, items_json, total_price)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_order(self, order_id):
        """دریافت اطلاعات سفارش"""
        self.cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return self.cursor.fetchone()
    
    def update_order_status(self, order_id, status):
        """بروزرسانی وضعیت سفارش"""
        self.cursor.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        self.conn.commit()
    
    def add_receipt(self, order_id, photo_id):
        """افزودن رسید به سفارش"""
        self.cursor.execute(
            "UPDATE orders SET receipt_photo = ?, status = 'receipt_sent' WHERE id = ?",
            (photo_id, order_id)
        )
        self.conn.commit()
    
    def update_shipping_method(self, order_id, method):
        """بروزرسانی نحوه ارسال"""
        self.cursor.execute(
            "UPDATE orders SET shipping_method = ? WHERE id = ?",
            (method, order_id)
        )
        self.conn.commit()
    
    def get_pending_orders(self):
        """دریافت سفارشات در انتظار تایید"""
        self.cursor.execute("SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def get_waiting_payment_orders(self):
        """دریافت سفارشات در انتظار پرداخت"""
        self.cursor.execute("SELECT * FROM orders WHERE status = 'waiting_payment' ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def get_user_orders(self, user_id):
        """دریافت سفارشات یک کاربر"""
        self.cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return self.cursor.fetchall()
    
    # ==================== آمار ====================
    
    def get_statistics(self):
        """دریافت آمار کلی"""
        stats = {}
        
        # تعداد کل سفارشات
        self.cursor.execute("SELECT COUNT(*) FROM orders")
        stats['total_orders'] = self.cursor.fetchone()[0]
        
        # تعداد سفارشات امروز
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = DATE('now')")
        stats['today_orders'] = self.cursor.fetchone()[0]
        
        # درآمد کل (فقط سفارشات تایید شده)
        self.cursor.execute("SELECT SUM(total_price) FROM orders WHERE status = 'confirmed'")
        total_income = self.cursor.fetchone()[0]
        stats['total_income'] = total_income if total_income else 0
        
        # درآمد امروز
        self.cursor.execute("SELECT SUM(total_price) FROM orders WHERE status = 'confirmed' AND DATE(created_at) = DATE('now')")
        today_income = self.cursor.fetchone()[0]
        stats['today_income'] = today_income if today_income else 0
        
        # تعداد کاربران
        self.cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = self.cursor.fetchone()[0]
        
        # تعداد محصولات
        self.cursor.execute("SELECT COUNT(*) FROM products")
        stats['total_products'] = self.cursor.fetchone()[0]
        
        # تعداد سفارشات در انتظار
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        stats['pending_orders'] = self.cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """بستن اتصال"""
        self.conn.close()
