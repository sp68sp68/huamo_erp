import sqlite3
import os
import sys
from datetime import datetime
import base64
import hashlib

# 加密功能可选（Android 构建时可能不可用）
try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


ANDROID = 'android' in sys.platform or os.environ.get('ANDROID_ARGUMENT')


def _resolve_db_path(db_path):
    """解析数据库路径，Android平台使用可写目录"""
    if db_path != "huamo.db":
        return db_path
    if ANDROID:
        try:
            from jnius import autoclass
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            files_dir = context.getFilesDir().getAbsolutePath()
            return os.path.join(files_dir, 'huamo.db')
        except Exception:
            pass
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app:
                return os.path.join(app.user_data_dir, 'huamo.db')
        except Exception:
            pass
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'huamo.db')


class DatabaseManager:
    def __init__(self, db_path="huamo.db"):
        self.db_path = _resolve_db_path(db_path)
        self.connection = None
        self._init_db()

    def _get_connection(self):
        """获取数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 启用外键约束
        cursor.execute("PRAGMA foreign_keys = ON")

        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin', 'operator')) NOT NULL,
                created_at DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 创建商品表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                width REAL,
                length REAL,
                bundles INTEGER,
                bundles_num INTEGER,
                piece_w REAL,
                look TEXT,
                retail_price REAL NOT NULL,
                alert_quantity INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        ''')

        # 创建市场表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS markets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        # 创建供应商表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                supplier TEXT NOT NULL,
                address TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                contact_person TEXT DEFAULT '',
                wechat TEXT DEFAULT '',
                alipay_account TEXT DEFAULT '',
                bank_account TEXT DEFAULT '',
                date DATETIME DEFAULT (datetime('now', 'localtime'))                
            )
        ''')
        # 创建销售客户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                seller TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                contact_person TEXT NOT NULL,
                wechat TEXT NOT NULL,
                alipay_account TEXT NOT NULL,
                bank_account TEXT NOT NULL,
                date DATETIME DEFAULT (datetime('now', 'localtime'))                
            )
        ''')

        # 创建库存表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                product_name TEXT PRIMARY KEY,
                stock_quantity INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                sell_price REAL NOT NULL               
            )
        ''')
        # 创建入库单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_in_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                in_no TEXT NOT NULL,
                market TEXT,
                supplier TEXT,                                
                total_quantity INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                operator_id INTEGER,
                date DATETIME DEFAULT (datetime('now', 'localtime'))                                                               
            )
        ''')
        # 创建入库明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_in_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                in_no TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price REAL NOT NULL,
                subtotal REAL NOT NULL                                            
            )
        ''')

        # 创建销售单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_no TEXT NOT NULL,
                market TEXT NOT NULL,
                seller TEXT,
                total_quantity INTEGER NOT NULL,
                total_amount REAL NOT NULL,
                proceeds REAL DEFAULT 0,
                proceeds_method TEXT CHECK(proceeds_method IN ('现金', '微信', '支付宝')),
                discount REAL DEFAULT 0,
                deduction REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                operator_id INTEGER,
                date DATETIME DEFAULT (datetime('now', 'localtime'))                
            )
        ''')
        # 创建销售明细表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                retail_price REAL NOT NULL,
                subtotal REAL NOT NULL                                             
            )
        ''')

         # 插入默认管理员账户（仅在用户表为空时）
        cursor.execute('SELECT COUNT(*) as count FROM users')
        user_count = cursor.fetchone()['count']
        
        if user_count == 0:
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', ('admin', self._hash_password('admin'), 'admin'))

        conn.commit()

    def _hash_password(self, password):
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_user(self, username, password):
        """验证用户登录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))

        user = cursor.fetchone()
        if user and user['password_hash'] == self._hash_password(password):
            return dict(user)
        return None

    def execute_query(self, query, params=None):
        """执行查询语句"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def execute_update(self, query, params=None):
        """执行更新语句"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid

    def get_all_tables(self):
        """获取所有表名"""
        cursor = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        return tables

    def check_table_exists(self, table_name):
        """检查表是否存在"""
        cursor = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None
    # ... existing code ...

    def get_customer_balance(self, seller):
        """获取客户余款（该客户最后一次订单的balance值）"""
        cursor = self.execute_query(
            "SELECT balance FROM sales_orders WHERE seller = ? ORDER BY id DESC LIMIT 1",
            (seller,)
        )
        result = cursor.fetchone()
        return result['balance'] if result else 0

# ... existing code ...

    def generate_order_no(self):
        """生成销售单号 XS-YYYYMMDD-XXX"""
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        
        cursor = self.execute_query(
            "SELECT order_no FROM sales_orders WHERE order_no LIKE ? ORDER BY id DESC LIMIT 1",
            (f"XS-{date_str}-%",)
        )
        last_order = cursor.fetchone()
        
        if last_order:
            last_num = int(last_order['order_no'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"XS-{date_str}-{new_num:03d}"
    def generate_in_no(self):
        """生成入库单号 RK-YYYYMMDD-XXX"""
        from datetime import datetime
        stock_str = datetime.now().strftime('%Y%m%d')
        
        cursor = self.execute_query(
            "SELECT in_no FROM stock_in_orders WHERE in_no LIKE ? ORDER BY id DESC LIMIT 1",
            (f"RK-{stock_str}-%",)
        )
        last_order = cursor.fetchone()
        
        if last_order:
            last_num = int(last_order['in_no'].split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f"RK-{stock_str}-{new_num:03d}"
if __name__ == "__main__":
    # 测试数据库初始化
    print("=" * 50)
    print("开始测试数据库...")
    print("=" * 50)
    
    try:
        # 使用 huamo.db 进行测试
        db = DatabaseManager("huamo.db")
        
        # 检查所有表是否创建成功
        print("\n检查数据表:")
        tables = ['users', 'products', 'markets', 'stocks', 'sales_orders','sales_items','stock_in_orders','stock_in_items','suppliers','sellers']
        for table in tables:
            exists = db.check_table_exists(table)
            status = "[OK] 存在" if exists else "[ERR] 不存在"
            print(f"  {table}: {status}")
        
        # 获取所有表
        all_tables = db.get_all_tables()
        print(f"\n数据库中所有表: {all_tables}")
        
        # 测试用户验证
        print("\n测试用户验证:")
        user = db.verify_user("admin", "admin")
        if user:
            print(f"  用户验证成功: {user['username']}, 角色: {user['role']}")
        else:
            print("  用户验证失败")
        
        # 关闭数据库连接
        db.close()
        print("\n测试完成!")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()

#    def get_customer_balance(self, seller):
#         """获取客户余款（欠款为负数）"""
#         cursor = self.execute_query(
#             "SELECT COALESCE(SUM(balance), 0) as total_balance FROM sales_orders WHERE seller = ?",
#             (seller,)
#         )
#         result = cursor.fetchone()
#         return result['total_balance'] if result else 0

#     def generate_order_no(self):
#         """生成销售单号 XS-YYYYMMDD-XXX"""
#         from datetime import datetime
#         date_str = datetime.now().strftime('%Y%m%d')
        
#         cursor = self.execute_query(
#             "SELECT order_no FROM sales_orders WHERE order_no LIKE ? ORDER BY id DESC LIMIT 1",
#             (f"XS-{date_str}-%",)
#         )
#         last_order = cursor.fetchone()
        
#         if last_order:
#             last_num = int(last_order['order_no'].split('-')[-1])
#             new_num = last_num + 1
#         else:
#             new_num = 1
        
#         return f"XS-{date_str}-{new_num:03d}"     