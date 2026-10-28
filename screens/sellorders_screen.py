"""
销售单查询界面
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


class SellOrdersScreen(BoxLayout):
    """销售单查询界面"""
    
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
        
        # # 顶部标签页切换按钮
        # tab_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        # self.tab_summary_btn = Button(text='库存总览', font_name='chinese')
        # self.tab_summary_btn.bind(on_press=lambda x: self.show_tab('summary'))
        
        # self.tab_stockin_btn = Button(text='入库列表', font_name='chinese')
        # self.tab_stockin_btn.bind(on_press=lambda x: self.show_tab('stockin'))
        
        # self.tab_stocks_btn = Button(text='库存列表', font_name='chinese')
        # self.tab_stocks_btn.bind(on_press=lambda x: self.show_tab('stocks'))
        
        # tab_bar.add_widget(self.tab_summary_btn)
        # tab_bar.add_widget(self.tab_stockin_btn)
        # tab_bar.add_widget(self.tab_stocks_btn)
        
        # self.add_widget(tab_bar)
        
        # 内容区域容器
        self.content_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.content_container)
        
        # 默认显示库存总览
        self.show_sellorders_tab()
    
    # def show_tab(self, tab_name):
    #     """切换标签页"""
    #     self.content_container.clear_widgets()
        
    #     if tab_name == 'summary':
    #         self.show_summary_tab()
    #     elif tab_name == 'stockin':
    #         self.show_stockin_tab()
    #     elif tab_name == 'stocks':
    #         self.show_stocks_tab()
    
    
    
    def show_sellorders_tab(self):
        """显示销售单列表标签页"""
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
        
        # # 销售单列表标题
        # title_label = Label(text='销售单列表', font_size=18, font_name='chinese', bold=True, size_hint_y=None, height=40)
        # self.content_container.add_widget(title_label)
        
        # 销售单列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        self.sellorders_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.sellorders_list_container.bind(minimum_height=self.sellorders_list_container.setter('height'))
        
        # 加载销售单列表
        self.load_sellorders('', '')
        
        scroll.add_widget(self.sellorders_list_container)
        self.content_container.add_widget(scroll)
        
        # 绑定查询和重置按钮
        def do_query(instance):
            start_date = self.start_date_btn.selected_date if self.start_date_btn.selected_date else ''
            end_date = self.end_date_btn.selected_date if self.end_date_btn.selected_date else ''
            self.load_sellorders(start_date, end_date)
        
        def do_reset(instance):
            self.start_date_btn.text = '选择开始日期'
            self.start_date_btn.selected_date = None
            self.end_date_btn.text = '选择结束日期'
            self.end_date_btn.selected_date = None
            self.load_sellorders('', '')
        
        query_btn.bind(on_press=do_query)
        reset_btn.bind(on_press=do_reset)
    
    def load_sellorders(self, start_date='', end_date=''):
        """加载销售单列表"""
        self.sellorders_list_container.clear_widgets()
        
        # 构建查询语句
        query = "SELECT * FROM sales_orders"
        params = []
        conditions = []
        
        if start_date and end_date:
            conditions.append("date >= ? AND date <= ?")
            params = [start_date, end_date]
        elif start_date:
            conditions.append("date >= ?")
            params = [start_date]
        elif end_date:
            conditions.append("date <= ?")
            params = [end_date]
        
         # 如果没有指定日期范围，默认显示今天的记录
        if not conditions:
            conditions.append("date(date) = date('now')")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date DESC"
        
        cursor = self.db.execute_query(query, params if params else None)
        orders = cursor.fetchall()
        
        if not orders:
            empty_label = Label(text='暂无销售单记录', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.sellorders_list_container.add_widget(empty_label)
        else:
            for order in orders:
                order_row = BoxLayout(size_hint_y=None, height=45, spacing=10, padding=[5, 0, 5, 0])
                
                order_no_btn = Button(text=f"销售单号: {order['order_no']}", font_name='chinese', size_hint_x=0.3)
                market_label = Label(text=f"市场: {order['market'] or 'N/A'}", font_name='chinese', size_hint_x=0.10)
                seller_label = Label(text=f"客户: {order['seller'] or 'N/A'}", font_name='chinese', size_hint_x=0.1)
                total_quantity_label = Label(text=f"数量: {order['total_quantity']}", font_name='chinese', size_hint_x=0.10)
                total_amount_label = Label(text=f"金额: ¥{order['total_amount']:.2f}", font_name='chinese', size_hint_x=0.15)
                proceeds_label = Label(text=f"收款: ¥{order['proceeds']:.2f}", font_name='chinese', size_hint_x=0.15)
                proceeds_method_label = Label(text=f"收款方式: {order['proceeds_method'] or 'N/A'}", font_name='chinese', size_hint_x=0.15)
                discount_label = Label(text=f"优惠: ¥{order['discount']:.2f}", font_name='chinese', size_hint_x=0.1)
                deduction_label = Label(text=f"扣款: ¥{order['deduction']:.2f}", font_name='chinese', size_hint_x=0.1)
                balance_label = Label(text=f"余额: ¥{order['balance']:.2f}", font_name='chinese', size_hint_x=0.1)
                date_label = Label(text=f"日期: {order['date']}", font_name='chinese', size_hint_x=0.2)
                
                # 创建点击处理函数
                def create_click_handler(oid):
                    def handler(instance):
                        self.show_sellorders_items(oid)
                    return handler
                
                order_no_btn.bind(on_press=create_click_handler(order['order_no']))
                
                order_row.add_widget(order_no_btn)
                order_row.add_widget(market_label)
                order_row.add_widget(seller_label)
                order_row.add_widget(total_quantity_label)
                order_row.add_widget(total_amount_label)
                order_row.add_widget(proceeds_label)
                order_row.add_widget(proceeds_method_label)
                order_row.add_widget(discount_label)
                order_row.add_widget(deduction_label)
                order_row.add_widget(balance_label)
                order_row.add_widget(date_label)
                
                self.sellorders_list_container.add_widget(order_row)
    
    def show_sellorders_items(self, order_no):
        """显示销售单明细"""
        popup = Popup(title=f'销售单明细 - {order_no}', size_hint=(0.9, 0.8), auto_dismiss=True)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 获取销售单明细
        cursor = self.db.execute_query("SELECT * FROM sales_items WHERE order_id = ? ORDER BY id", (order_no,))
        items = cursor.fetchall()
        
        # 明细列表标题
        title_label = Label(text='销售单明细', font_size=16, font_name='chinese', bold=True, size_hint_y=None, height=35)
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
                price_label = Label(text=f"单价: ¥{item['retail_price']:.2f}", font_name='chinese', size_hint_x=0.25)
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
    
    