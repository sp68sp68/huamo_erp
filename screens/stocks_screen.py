"""
库存管理界面
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from datetime import datetime, timedelta
import sys
import os

# 添加父目录到路径以导入database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager


class DateSelector(Button):
    """日期选择按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = None
        self.bind(on_release=self.show_date_picker)
    
    def show_date_picker(self, instance):
        """显示日期选择器"""
        popup = Popup(title='选择日期', size_hint=(0.4, 0.5), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 年份选择
        year_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        year_layout.add_widget(Label(text='年:', font_name='chinese', size_hint_x=None, width=40))
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 5, current_year + 6)]
        self.year_spinner = Spinner(text=str(current_year), values=years, font_name='chinese')
        year_layout.add_widget(self.year_spinner)
        layout.add_widget(year_layout)
        
        # 月份选择
        month_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        month_layout.add_widget(Label(text='月:', font_name='chinese', size_hint_x=None, width=40))
        months = ['{:02d}'.format(m) for m in range(1, 13)]
        self.month_spinner = Spinner(text='{:02d}'.format(datetime.now().month), values=months, font_name='chinese')
        month_layout.add_widget(self.month_spinner)
        layout.add_widget(month_layout)
        
        # 日期选择
        day_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        day_layout.add_widget(Label(text='日:', font_name='chinese', size_hint_x=None, width=40))
        days = ['{:02d}'.format(d) for d in range(1, 32)]
        self.day_spinner = Spinner(text='{:02d}'.format(datetime.now().day), values=days, font_name='chinese')
        day_layout.add_widget(self.day_spinner)
        layout.add_widget(day_layout)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        confirm_btn = Button(text='确定', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def confirm(instance):
            try:
                year = int(self.year_spinner.text)
                month = int(self.month_spinner.text)
                day = int(self.day_spinner.text)
                
                # 验证日期有效性
                selected_date = datetime(year, month, day)
                date_str = selected_date.strftime('%Y-%m-%d')
                self.text = date_str
                self.selected_date = date_str
                popup.dismiss()
            except ValueError as e:
                error_popup = Popup(title='错误', size_hint=(0.4, 0.3))
                error_layout = BoxLayout(orientation='vertical', padding=20)
                error_layout.add_widget(Label(text=f'日期无效: {e}', font_name='chinese'))
                close_btn = Button(text='关闭', font_name='chinese', size_hint_y=None, height=40)
                close_btn.bind(on_press=lambda x: error_popup.dismiss())
                error_layout.add_widget(close_btn)
                error_popup.add_widget(error_layout)
                error_popup.open()
        
        confirm_btn.bind(on_press=confirm)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()


class StocksScreen(BoxLayout):
    """库存管理主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 构建界面
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        self.clear_widgets()
        
        # 顶部标签页切换按钮
        tab_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.tab_summary_btn = Button(text='库存总览', font_name='chinese')
        self.tab_summary_btn.bind(on_press=lambda x: self.show_tab('summary'))
        
        self.tab_stockin_btn = Button(text='入库列表', font_name='chinese')
        self.tab_stockin_btn.bind(on_press=lambda x: self.show_tab('stockin'))
        
        self.tab_stocks_btn = Button(text='库存列表', font_name='chinese')
        self.tab_stocks_btn.bind(on_press=lambda x: self.show_tab('stocks'))
        
        tab_bar.add_widget(self.tab_summary_btn)
        tab_bar.add_widget(self.tab_stockin_btn)
        tab_bar.add_widget(self.tab_stocks_btn)
        
        self.add_widget(tab_bar)
        
        # 内容区域容器
        self.content_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.content_container)
        
        # 默认显示库存总览
        self.show_tab('summary')
    
    def show_tab(self, tab_name):
        """切换标签页"""
        self.content_container.clear_widgets()
        
        if tab_name == 'summary':
            self.show_summary_tab()
        elif tab_name == 'stockin':
            self.show_stockin_tab()
        elif tab_name == 'stocks':
            self.show_stocks_tab()
    
    def show_summary_tab(self):
        """显示库存总览标签页"""
        # 计算库存统计数据
        cursor = self.db.execute_query("""
            SELECT 
                SUM(stock_quantity) as total_quantity,
                SUM(stock_quantity * cost_price) as total_amount,
                SUM(stock_quantity * sell_price) as total_value
            FROM stocks
        """)
        result = cursor.fetchone()
        
        total_quantity = result['total_quantity'] if result['total_quantity'] else 0
        total_amount = result['total_amount'] if result['total_amount'] else 0.0
        total_value = result['total_value'] if result['total_value'] else 0.0
        
        # 创建统计信息显示区域
        stats_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=20, padding=[20, 10, 20, 10])
        
        # 库存总数量
        quantity_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        quantity_label = Label(text='库存总数量', font_size=18, font_name='chinese', size_hint_y=None, height=40)
        quantity_value = Label(text=str(total_quantity), font_size=24, font_name='chinese', bold=True, size_hint_y=None, height=60)
        quantity_box.add_widget(quantity_label)
        quantity_box.add_widget(quantity_value)
        
        # 库存总金额
        amount_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        amount_label = Label(text='库存总金额', font_size=18, font_name='chinese', size_hint_y=None, height=40)
        amount_value = Label(text=f'¥{total_amount:.2f}', font_size=24, font_name='chinese', bold=True, size_hint_y=None, height=60)
        amount_box.add_widget(amount_label)
        amount_box.add_widget(amount_value)
        
        # 库存总价值
        value_box = BoxLayout(orientation='vertical', size_hint_x=0.33)
        value_label = Label(text='库存总价值', font_size=18, font_name='chinese', size_hint_y=None, height=40)
        value_value = Label(text=f'¥{total_value:.2f}', font_size=24, font_name='chinese', bold=True, size_hint_y=None, height=60)
        value_box.add_widget(value_label)
        value_box.add_widget(value_value)
        
        stats_layout.add_widget(quantity_box)
        stats_layout.add_widget(amount_box)
        stats_layout.add_widget(value_box)
        
        self.content_container.add_widget(stats_layout)
        
        # 空白区域占位
        spacer = Label(text='', size_hint=(1, 1))
        self.content_container.add_widget(spacer)
    
    def show_stockin_tab(self):
        """显示入库列表标签页"""
        # 时段选择区域
        filter_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10, padding=[5, 5, 5, 5])
        
        filter_layout.add_widget(Label(text='选择时段:', font_name='chinese', size_hint_x=None, width=80))
        
        # 开始日期选择按钮
        self.start_date_btn = DateSelector(text='选择开始日期', font_name='chinese', size_hint_x=None, width=150)
        filter_layout.add_widget(self.start_date_btn)
        
        filter_layout.add_widget(Label(text='至', font_name='chinese', size_hint_x=None, width=30))
        
        # 结束日期选择按钮
        self.end_date_btn = DateSelector(text='选择结束日期', font_name='chinese', size_hint_x=None, width=150)
        filter_layout.add_widget(self.end_date_btn)
        
        # 查询按钮
        query_btn = Button(text='查询', font_name='chinese', size_hint_x=None, width=80)
        filter_layout.add_widget(query_btn)
        
        # 重置按钮
        reset_btn = Button(text='重置', font_name='chinese', size_hint_x=None, width=80)
        filter_layout.add_widget(reset_btn)
        
        self.content_container.add_widget(filter_layout)
        
        # 入库单列表标题
        title_label = Label(text='入库单列表', font_size=18, font_name='chinese', bold=True, size_hint_y=None, height=40)
        self.content_container.add_widget(title_label)
        
        # 入库单列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        self.stockin_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.stockin_list_container.bind(minimum_height=self.stockin_list_container.setter('height'))
        
        # 加载入库单列表
        self.load_stockin_orders('', '')
        
        scroll.add_widget(self.stockin_list_container)
        self.content_container.add_widget(scroll)
        
        # 绑定查询和重置按钮
        def do_query(instance):
            start_date = self.start_date_btn.selected_date if self.start_date_btn.selected_date else ''
            end_date = self.end_date_btn.selected_date if self.end_date_btn.selected_date else ''
            self.load_stockin_orders(start_date, end_date)
        
        def do_reset(instance):
            self.start_date_btn.text = '选择开始日期'
            self.start_date_btn.selected_date = None
            self.end_date_btn.text = '选择结束日期'
            self.end_date_btn.selected_date = None
            self.load_stockin_orders('', '')
        
        query_btn.bind(on_press=do_query)
        reset_btn.bind(on_press=do_reset)
    
    def load_stockin_orders(self, start_date='', end_date=''):
        """加载入库单列表"""
        self.stockin_list_container.clear_widgets()
        
        # 构建查询语句
        query = "SELECT * FROM stock_in_orders"
        params = []
        
        if start_date and end_date:
            query += " WHERE date >= ? AND date <= ?"
            params = [start_date, end_date]
        elif start_date:
            query += " WHERE date >= ?"
            params = [start_date]
        elif end_date:
            query += " WHERE date <= ?"
            params = [end_date]
        
        query += " ORDER BY date DESC"
        
        cursor = self.db.execute_query(query, params if params else None)
        orders = cursor.fetchall()
        
        if not orders:
            empty_label = Label(text='暂无入库记录', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.stockin_list_container.add_widget(empty_label)
        else:
            for order in orders:
                order_row = BoxLayout(size_hint_y=None, height=45, spacing=10, padding=[5, 0, 5, 0])
                
                in_no_btn = Button(text=f"入库单号: {order['in_no']}", font_name='chinese', size_hint_x=0.25)
                market_label = Label(text=f"市场: {order['market'] or 'N/A'}", font_name='chinese', size_hint_x=0.15)
                supplier_label = Label(text=f"供应商: {order['supplier'] or 'N/A'}", font_name='chinese', size_hint_x=0.2)
                quantity_label = Label(text=f"数量: {order['total_quantity']}", font_name='chinese', size_hint_x=0.15)
                amount_label = Label(text=f"金额: ¥{order['total_amount']:.2f}", font_name='chinese', size_hint_x=0.15)
                date_label = Label(text=f"日期: {order['date']}", font_name='chinese', size_hint_x=0.1)
                
                # 创建点击处理函数
                def create_click_handler(oid):
                    def handler(instance):
                        self.show_stockin_items(oid)
                    return handler
                
                in_no_btn.bind(on_press=create_click_handler(order['in_no']))
                
                order_row.add_widget(in_no_btn)
                order_row.add_widget(market_label)
                order_row.add_widget(supplier_label)
                order_row.add_widget(quantity_label)
                order_row.add_widget(amount_label)
                order_row.add_widget(date_label)
                
                self.stockin_list_container.add_widget(order_row)
    
    def show_stockin_items(self, in_no):
        """显示入库单明细"""
        popup = Popup(title=f'入库单明细 - {in_no}', size_hint=(0.9, 0.8), auto_dismiss=True)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 获取入库单明细
        cursor = self.db.execute_query("SELECT * FROM stock_in_items WHERE in_no = ? ORDER BY id", (in_no,))
        items = cursor.fetchall()
        
        # 明细列表标题
        title_label = Label(text='入库明细', font_size=16, font_name='chinese', bold=True, size_hint_y=None, height=35)
        layout.add_widget(title_label)
        
        # 明细列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        items_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        items_container.bind(minimum_height=items_container.setter('height'))
        
        if not items:
            empty_label = Label(text='暂无明细数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            items_container.add_widget(empty_label)
        else:
            for item in items:
                item_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                product_label = Label(text=f"商品: {item['product_name']}", font_name='chinese', size_hint_x=0.3)
                quantity_label = Label(text=f"数量: {item['quantity']}", font_name='chinese', size_hint_x=0.2)
                price_label = Label(text=f"单价: ¥{item['cost_price']:.2f}", font_name='chinese', size_hint_x=0.25)
                subtotal_label = Label(text=f"小计: ¥{item['subtotal']:.2f}", font_name='chinese', size_hint_x=0.25)
                
                item_row.add_widget(product_label)
                item_row.add_widget(quantity_label)
                item_row.add_widget(price_label)
                item_row.add_widget(subtotal_label)
                
                items_container.add_widget(item_row)
        
        scroll.add_widget(items_container)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_stocks_tab(self):
        """显示库存列表标签页"""
        # 库存列表标题
        title_label = Label(text='库存列表', font_size=18, font_name='chinese', bold=True, size_hint_y=None, height=40)
        self.content_container.add_widget(title_label)
        
        # 库存列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        stocks_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        stocks_container.bind(minimum_height=stocks_container.setter('height'))
        
        # 获取所有库存数据
        cursor = self.db.execute_query("SELECT * FROM stocks ORDER BY product_name")
        stocks = cursor.fetchall()
        
        if not stocks:
            empty_label = Label(text='暂无库存数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            stocks_container.add_widget(empty_label)
        else:
            for stock in stocks:
                stock_row = BoxLayout(size_hint_y=None, height=45, spacing=10, padding=[5, 0, 5, 0])
                
                product_label = Label(text=f"商品: {stock['product_name']}", font_name='chinese', size_hint_x=0.25)
                quantity_label = Label(text=f"库存: {stock['stock_quantity']}", font_name='chinese', size_hint_x=0.15)
                cost_price_label = Label(text=f"成本价: ¥{stock['cost_price']:.2f}", font_name='chinese', size_hint_x=0.2)
                sell_price_label = Label(text=f"售价: ¥{stock['sell_price']:.2f}", font_name='chinese', size_hint_x=0.2)
                amount_label = Label(text=f"库存金额: ¥{stock['stock_quantity'] * stock['cost_price']:.2f}", font_name='chinese', size_hint_x=0.2)
                
                stock_row.add_widget(product_label)
                stock_row.add_widget(quantity_label)
                stock_row.add_widget(cost_price_label)
                stock_row.add_widget(sell_price_label)
                stock_row.add_widget(amount_label)
                
                stocks_container.add_widget(stock_row)
        
        scroll.add_widget(stocks_container)
        self.content_container.add_widget(scroll)