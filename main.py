"""
华膜进销存系统 - 主程序
"""

import sys
import os
import platform

# 检测是否在Android平台
ANDROID = 'android' in sys.platform or os.environ.get('ANDROID_ARGUMENT')

# 禁用 logging 输出（解决 --noconsole 时的 AttributeError）
import logging
logging.basicConfig(level=logging.CRITICAL)

# 如果在打包环境中，重定向 stdout/stderr
if hasattr(sys, 'frozen'):
    class NullWriter:
        def write(self, text):
            pass
        def flush(self):
            pass
    sys.stdout = NullWriter()
    sys.stderr = NullWriter()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.core.text import LabelBase

# 注册中文字体 - 跨平台兼容
if ANDROID:
    # Android平台：使用打包的字体文件
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'msyh.ttf')
    if os.path.exists(font_path):
        LabelBase.register(name='chinese', fn_regular=font_path)
    else:
        # 如果打包字体不存在，尝试使用Android系统字体
        system_font = '/system/fonts/DroidSansFallback.ttf'
        if os.path.exists(system_font):
            LabelBase.register(name='chinese', fn_regular=system_font)
        else:
            LabelBase.register(name='chinese', fn_regular=font_path)  # 仍然注册，让Kivy处理错误
else:
    # Windows/Mac平台：使用系统字体
    LabelBase.register(name='chinese', fn_regular='C:/Windows/Fonts/msyh.ttc')

# 导入用户管理界面
from screens.user_screen import UserManagementScreen
# 导入产品管理界面
from screens.product_screen import ProductManagementScreen
# 导入市场管理界面
from screens.market_screen import MarketManagementScreen
# 导入销售开单界面
from screens.make_order_screen import MakeOrderScreen
# 导入供应商管理界面
from screens.supplier_screen import SupplierManagementScreen
# 导入销售客户管理界面
from screens.seller_screen import SellerManagementScreen
# 导入商品入库界面
from screens.stockin_screen import StockInScreen
# 导入库存管理界面
from screens.stocks_screen import StocksScreen
# 导入销售单查询界面
from screens.sellorders_screen import SellOrdersScreen
# 导入余款及收款界面
from screens.proceeds_screen import ProceedsScreen

# 设置窗口标题和大小（仅桌面平台）
if not ANDROID:
    Window.set_title('华膜进销存管理系统')
    Window.size = (1200, 800)

class LoginScreen(Screen):
    """登录界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text='华膜进销存管理系统', font_size=32, size_hint_y=None, height=60, font_name='chinese')
        layout.add_widget(title)
        
        # 用户名输入
        user_layout = BoxLayout(size_hint_y=None, height=40)
        user_layout.add_widget(Label(text='用户名:', size_hint_x=None, width=80, font_name='chinese'))
        self.username_input = TextInput(hint_text='请输入用户名', multiline=False, font_name='chinese')
        user_layout.add_widget(self.username_input)
        layout.add_widget(user_layout)
        
        # 密码输入
        pass_layout = BoxLayout(size_hint_y=None, height=40)
        pass_layout.add_widget(Label(text='密码:', size_hint_x=None, width=80, font_name='chinese'))
        self.password_input = TextInput(hint_text='请输入密码', password=True, multiline=False, font_name='chinese')
        pass_layout.add_widget(self.password_input)
        layout.add_widget(pass_layout)
        
        # 登录按钮
        login_btn = Button(text='登录', size_hint_y=None, height=50, font_name='chinese')
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        from database import DatabaseManager
        db = DatabaseManager("huamo.db")
        
        username = self.username_input.text
        password = self.password_input.text
        
        if username and password:
            user = db.verify_user(username, password)
            if user:
                print(f'登录成功: {username}')
                db.close()
                self.manager.current = 'main'
            else:
                print(f'登录失败: 用户名或密码错误')
                from kivy.uix.popup import Popup
                popup = Popup(title='登录失败', size_hint=(0.4, 0.3))
                layout = BoxLayout(orientation='vertical', padding=20)
                layout.add_widget(Label(text='用户名或密码错误！', font_name='chinese', halign='center'))
                ok_btn = Button(text='确定', size_hint_y=None, height=40, font_name='chinese')
                ok_btn.bind(on_press=lambda x: popup.dismiss())
                layout.add_widget(ok_btn)
                popup.add_widget(layout)
                popup.open()
        else:
            print('请输入用户名和密码')

class MainScreen(Screen):
    """主界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # 顶部菜单栏
        menu_bar = BoxLayout(size_hint_y=None, height=50)
        menu_items = ['销售开单','商品入库','用户管理','商品管理', '市场管理', '供应商管理', '销售客户管理', '库存管理',  '余款及收款', '实时日报', '销售单查询', '销量综合统计']
        for item in menu_items:
            btn = Button(text=item, font_name='chinese')
            btn.bind(on_press=lambda x, text=item: self.menu_click(text))
            menu_bar.add_widget(btn)
           
        
        self.layout.add_widget(menu_bar)
        
        # 内容区域 - 初始显示欢迎信息
        self.content_area = BoxLayout()
        self.welcome_label = Label(text='欢迎使用华膜进销存管理系统', font_size=24, font_name='chinese')
        self.content_area.add_widget(self.welcome_label)
        self.layout.add_widget(self.content_area)
        
        self.add_widget(self.layout)
    
    def menu_click(self, item):
        """菜单点击处理"""
        # 清除当前内容
        self.content_area.clear_widgets()
        
        if item == '用户管理':
            # 显示用户管理界面
            user_screen = UserManagementScreen()
            self.content_area.add_widget(user_screen)
        elif item == '商品管理':
            # 显示商品管理界面
            product_screen = ProductManagementScreen()
            self.content_area.add_widget(product_screen)
        elif item == '市场管理':
            # 显示市场管理界面
            market_screen = MarketManagementScreen()
            self.content_area.add_widget(market_screen)
        elif item == '销售开单':
            # 显示销售开单界面
            make_order_screen = MakeOrderScreen()
            self.content_area.add_widget(make_order_screen)
        elif item == '供应商管理':
            # 显示供应商管理界面
            supplier_screen = SupplierManagementScreen()
            self.content_area.add_widget(supplier_screen)
        elif item == '销售客户管理':
            # 显示销售客户管理界面
            seller_screen = SellerManagementScreen()
            self.content_area.add_widget(seller_screen)
        elif item == '商品入库':
            # 显示商品入库界面
            stockin_screen = StockInScreen()
            self.content_area.add_widget(stockin_screen)
        elif item == '库存管理':
            # 显示库存管理界面
            stocks_screen = StocksScreen()
            self.content_area.add_widget(stocks_screen)
        elif item == '销售单查询':
            sellorders_screen = SellOrdersScreen()
            self.content_area.add_widget(sellorders_screen)
        elif item == '余款及收款':
            proceeds_screen = ProceedsScreen()
            self.content_area.add_widget(proceeds_screen)
        else:
            # 其他功能显示提示
            label = Label(text=f'您选择了: {item}\n(功能开发中...)', font_size=24, font_name='chinese')
            self.content_area.add_widget(label)

class HuamoERP(App):
    """主应用类"""
    def build(self):
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加登录界面
        sm.add_widget(LoginScreen(name='login'))
        
        # 添加主界面
        sm.add_widget(MainScreen(name='main'))
        
        # 默认显示登录界面
        sm.current = 'login'
        
        return sm

if __name__ == '__main__':
    # 初始化数据库等操作可以在这里进行
    print("启动华膜进销存系统...")
    
    # 运行应用
    HuamoERP().run()