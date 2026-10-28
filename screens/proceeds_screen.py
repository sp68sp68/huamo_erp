"""
收款管理界面 - proceeds_screen.py
功能：
1. 生成所有销售客户的余款列表（市场、销售客户、余款、"明细"按钮、"收款"按钮）
2. 余款为0的客户不显示
3. "明细"按钮：弹出该客户欠款的销售单列表，点击销售单号可查看明细
4. "收款"按钮：弹出收款界面，提交后更新sales_orders表
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
from datetime import datetime
import sys
import os

# 添加父目录到路径以导入database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager


class ProceedsScreen(BoxLayout):
    """收款管理主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 当前选中的客户信息
        self.current_seller = None
        self.current_market = None
        self.current_balance = 0
        
        # 构建界面
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        self.clear_widgets()
        
        # 标题
        title_label = Label(
            text='客户余款及收款管理',
            font_size=20,
            font_name='chinese',
            bold=True,
            size_hint_y=None,
            height=50
        )
        self.add_widget(title_label)
        
        # 内容区域容器
        self.content_container = BoxLayout(orientation='vertical', size_hint=(1, 1))
        self.add_widget(self.content_container)
        
        # 加载余款列表
        self.load_balance_list()
    
    def load_balance_list(self):
        """加载客户余款列表（只显示余款不为0的客户）"""
        self.content_container.clear_widgets()
        
        # 查询每个客户的最新订单和余款
        query = """
            SELECT q.market, q.seller, q.balance 
            FROM sales_orders q 
            JOIN (
                SELECT seller, MAX(id) AS max_id 
                FROM sales_orders 
                GROUP BY seller
            ) latest ON q.seller = latest.seller AND q.id = latest.max_id
            WHERE q.balance != 0
            ORDER BY q.seller
        """
        
        cursor = self.db.execute_query(query)
        orders = cursor.fetchall()
        
        if not orders:
            empty_label = Label(
                text='暂无欠款记录',
                font_size=18,
                font_name='chinese',
                size_hint_y=None,
                height=40
            )
            self.content_container.add_widget(empty_label)
        else:
            # 创建滚动区域
            scroll = ScrollView(size_hint=(1, 1))
            list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
            list_container.bind(minimum_height=list_container.setter('height'))
            
            for order in orders:
                row = BoxLayout(
                    size_hint_y=None,
                    height=50,
                    spacing=10,
                    padding=[10, 5, 10, 5]
                )
                
                # 市场
                market_label = Label(
                    text=f"市场: {order['market'] or 'N/A'}",
                    font_name='chinese',
                    size_hint_x=0.15
                )
                
                # 客户
                seller_label = Label(
                    text=f"客户: {order['seller'] or 'N/A'}",
                    font_name='chinese',
                    size_hint_x=0.2
                )
                
                # 余款（根据正负显示不同颜色）
                balance = order['balance']
                balance_color = (1, 0, 0, 1) if balance < 0 else (0, 0.6, 0, 1)
                balance_label = Label(
                    text=f"余款: ¥{balance:.2f}",
                    font_name='chinese',
                    color=balance_color,
                    size_hint_x=0.2
                )
                
                # 明细按钮
                detail_btn = Button(
                    text='明细',
                    font_name='chinese',
                    size_hint_x=0.15
                )
                detail_btn.bind(on_press=lambda x, m=order['market'], s=order['seller']: self.show_order_details(m, s))
                
                # 收款按钮
                payment_btn = Button(
                    text='收款',
                    font_name='chinese',
                    size_hint_x=0.15
                )
                payment_btn.bind(on_press=lambda x, m=order['market'], s=order['seller'], b=order['balance']: self.show_payment_interface(m, s, b))
                
                row.add_widget(market_label)
                row.add_widget(seller_label)
                row.add_widget(balance_label)
                row.add_widget(detail_btn)
                row.add_widget(payment_btn)
                
                list_container.add_widget(row)
            
            scroll.add_widget(list_container)
            self.content_container.add_widget(scroll)
    
    def show_order_details(self, market, seller):
        """显示客户欠款的销售单列表"""
        popup = Popup(
            title=f'销售单明细 - {seller}',
            size_hint=(0.95, 0.85),
            auto_dismiss=True
        )
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_label = Label(
            text=f'客户: {seller} | 市场: {market}',
            font_size=16,
            font_name='chinese',
            bold=True,
            size_hint_y=None,
            height=35
        )
        layout.add_widget(title_label)
        
        # 获取该客户的所有销售单（按时间排序）
        cursor = self.db.execute_query(
            "SELECT * FROM sales_orders WHERE seller = ? ORDER BY date DESC",
            (seller,)
        )
        orders = cursor.fetchall()
        
        # 销售单列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        orders_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        orders_container.bind(minimum_height=orders_container.setter('height'))
        
        if not orders:
            empty_label = Label(
                text='暂无销售单记录',
                font_size=18,
                font_name='chinese',
                size_hint_y=None,
                height=40
            )
            orders_container.add_widget(empty_label)
        else:
            for order in orders:
                order_row = BoxLayout(
                    size_hint_y=None,
                    height=45,
                    spacing=10,
                    padding=[5, 0, 5, 0]
                )
                
                # 销售单号按钮（可点击查看明细）- 传递order_id
                order_no_btn = Button(
                    text=f"单号: {order['order_no']}",
                    font_name='chinese',
                    size_hint_x=0.2
                )
                order_no_btn.bind(on_press=lambda x, ono=order['order_no']: self.show_sale_item_detail(ono, popup))
                
                market_label = Label(
                    text=f"市场: {order['market'] or 'N/A'}",
                    font_name='chinese',
                    size_hint_x=0.1
                )
                seller_label = Label(
                    text=f"客户: {order['seller'] or 'N/A'}",
                    font_name='chinese',
                    size_hint_x=0.1
                )
                quantity_label = Label(
                    text=f"数量: {order['total_quantity']}",
                    font_name='chinese',
                    size_hint_x=0.08
                )
                amount_label = Label(
                    text=f"金额: ¥{order['total_amount']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.12
                )
                proceeds_label = Label(
                    text=f"收款: ¥{order['proceeds']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.1
                )
                method_label = Label(
                    text=f"方式: {order['proceeds_method'] or 'N/A'}",
                    font_name='chinese',
                    size_hint_x=0.1
                )
                discount_label = Label(
                    text=f"优惠: ¥{order['discount']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.08
                )
                deduction_label = Label(
                    text=f"扣除: ¥{order['deduction']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.08
                )
                balance_label = Label(
                    text=f"余额: ¥{order['balance']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.1
                )
                date_label = Label(
                    text=f"{order['date']}",
                    font_name='chinese',
                    size_hint_x=0.14
                )
                
                order_row.add_widget(order_no_btn)
                order_row.add_widget(market_label)
                order_row.add_widget(seller_label)
                order_row.add_widget(quantity_label)
                order_row.add_widget(amount_label)
                order_row.add_widget(proceeds_label)
                order_row.add_widget(method_label)
                order_row.add_widget(discount_label)
                order_row.add_widget(deduction_label)
                order_row.add_widget(balance_label)
                order_row.add_widget(date_label)
                
                orders_container.add_widget(order_row)
        
        scroll.add_widget(orders_container)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(
            text='关闭',
            size_hint_y=None,
            height=40,
            font_name='chinese'
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_sale_item_detail(self, order_no, parent_popup):
        """显示销售单的明细（商品列表）"""
        # 先获取订单信息 - 使用order_no查询
        cursor = self.db.execute_query(
            "SELECT * FROM sales_orders WHERE order_no = ?",
            (order_no,)
        )
        order = cursor.fetchone()
        
        if not order:
            return
        
        detail_popup = Popup(
            title=f'销售单明细 - {order["order_no"]}',
            size_hint=(0.8, 0.7),
            auto_dismiss=True
        )
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 订单基本信息
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        info_layout.add_widget(Label(
            text=f"单号: {order['order_no']}\n客户: {order['seller']}\n日期: {order['date']}",
            font_name='chinese',
            size_hint_x=0.5
        ))
        info_layout.add_widget(Label(
            text=f"总金额: ¥{order['total_amount']:.2f}\n收款: ¥{order['proceeds']:.2f}\n余额: ¥{order['balance']:.2f}",
            font_name='chinese',
            size_hint_x=0.5
        ))
        layout.add_widget(info_layout)
        
        # 获取销售明细 - 使用order_no（sales_items.order_id存储的是order_no）
        cursor = self.db.execute_query(
            "SELECT * FROM sales_items WHERE order_id = ? ORDER BY id",
            (order_no,)
        )
        items = cursor.fetchall()
        
        # 明细列表标题
        title_label = Label(
            text='商品明细',
            font_size=16,
            font_name='chinese',
            bold=True,
            size_hint_y=None,
            height=35
        )
        layout.add_widget(title_label)
        
        # 明细列表滚动区域
        scroll = ScrollView(size_hint=(1, 1))
        items_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        items_container.bind(minimum_height=items_container.setter('height'))
        
        if not items:
            empty_label = Label(
                text='暂无明细数据',
                font_size=18,
                font_name='chinese',
                size_hint_y=None,
                height=40
            )
            items_container.add_widget(empty_label)
        else:
            for item in items:
                item_row = BoxLayout(
                    size_hint_y=None,
                    height=40,
                    spacing=10,
                    padding=[5, 0, 5, 0]
                )
                
                product_label = Label(
                    text=f"商品: {item['product_name']}",
                    font_name='chinese',
                    size_hint_x=0.3
                )
                quantity_label = Label(
                    text=f"数量: {item['quantity']}",
                    font_name='chinese',
                    size_hint_x=0.2
                )
                price_label = Label(
                    text=f"单价: ¥{item['retail_price']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.25
                )
                subtotal_label = Label(
                    text=f"小计: ¥{item['subtotal']:.2f}",
                    font_name='chinese',
                    size_hint_x=0.25
                )
                
                item_row.add_widget(product_label)
                item_row.add_widget(quantity_label)
                item_row.add_widget(price_label)
                item_row.add_widget(subtotal_label)
                
                items_container.add_widget(item_row)
        
        scroll.add_widget(items_container)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(
            text='关闭',
            size_hint_y=None,
            height=40,
            font_name='chinese'
        )
        close_btn.bind(on_press=lambda x: detail_popup.dismiss())
        layout.add_widget(close_btn)
        
        detail_popup.add_widget(layout)
        detail_popup.open()
    
    def show_payment_interface(self, market, seller, balance):
        """显示收款界面"""
        # 保存当前客户信息
        self.current_market = market
        self.current_seller = seller
        self.current_balance = balance
        
        popup = Popup(
            title=f'收款 - {seller}',
            size_hint=(0.6, 0.7),
            auto_dismiss=False
        )
        
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 客户信息区域
        info_box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        
        market_row = BoxLayout(size_hint_y=None, height=30)
        market_row.add_widget(Label(text='市场:', font_name='chinese', size_hint_x=None, width=60))
        market_row.add_widget(Label(text=market or 'N/A', font_name='chinese', size_hint_x=1))
        info_box.add_widget(market_row)
        
        seller_row = BoxLayout(size_hint_y=None, height=30)
        seller_row.add_widget(Label(text='客户:', font_name='chinese', size_hint_x=None, width=60))
        seller_row.add_widget(Label(text=seller or 'N/A', font_name='chinese', size_hint_x=1))
        info_box.add_widget(seller_row)
        
        balance_row = BoxLayout(size_hint_y=None, height=30)
        balance_row.add_widget(Label(text='当前余款:', font_name='chinese', size_hint_x=None, width=80))
        balance_color = (1, 0, 0, 1) if balance < 0 else (0, 0.6, 0, 1)
        self.payment_balance_label = Label(
            text=f'¥{balance:.2f}',
            font_name='chinese',
            color=balance_color,
            size_hint_x=1
        )
        balance_row.add_widget(self.payment_balance_label)
        info_box.add_widget(balance_row)
        
        layout.add_widget(info_box)
        
        # 收款输入区域
        input_box = BoxLayout(orientation='vertical', size_hint_y=None, height=180, spacing=10)
        
        # 本次实收款
        proceeds_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        proceeds_row.add_widget(Label(text='本次实收款:', font_name='chinese', size_hint_x=None, width=100))
        self.proceeds_input = TextInput(
            hint_text='请输入收款金额',
            multiline=False,
            font_name='chinese',
            size_hint_x=0.5
        )
        proceeds_row.add_widget(self.proceeds_input)
        
          # 支付方式
        proceeds_row.add_widget(Label(text='支付方式:', font_name='chinese', size_hint_x=None, width=80))
        self.payment_method_spinner = Spinner(
            text='现金',
            values=('现金', '微信', '支付宝'),
            size_hint_x=0.3,
            font_name='chinese'
        )
        proceeds_row.add_widget(self.payment_method_spinner)
        
        input_box.add_widget(proceeds_row)
        
        # 优惠额
        discount_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        discount_row.add_widget(Label(text='优惠额:', font_name='chinese', size_hint_x=None, width=100))
        self.discount_input = TextInput(
            hint_text='请输入优惠金额',
            multiline=False,
            font_name='chinese',
            size_hint_x=0.5
        )
        discount_row.add_widget(self.discount_input)
        input_box.add_widget(discount_row)
        
        # 扣除额
        deduction_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        deduction_row.add_widget(Label(text='扣除额:', font_name='chinese', size_hint_x=None, width=100))
        self.deduction_input = TextInput(
            hint_text='请输入扣除金额',
            multiline=False,
            font_name='chinese',
            size_hint_x=0.5
        )
        deduction_row.add_widget(self.deduction_input)
        input_box.add_widget(deduction_row)
        
        # 最终余款显示
        final_balance_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        final_balance_row.add_widget(Label(text='最终余款:', font_name='chinese', size_hint_x=None, width=100))
        self.final_balance_label = Label(
            text=f'¥{balance:.2f}',
            font_name='chinese',
            color=balance_color,
            size_hint_x=1
        )
        final_balance_row.add_widget(self.final_balance_label)
        input_box.add_widget(final_balance_row)
        
        layout.add_widget(input_box)
        
        # 绑定输入事件，自动计算最终余款
        self.proceeds_input.bind(text=self.calculate_final_balance)
        self.discount_input.bind(text=self.calculate_final_balance)
        self.deduction_input.bind(text=self.calculate_final_balance)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        submit_btn = Button(text='确认提交', font_name='chinese')
        submit_btn.bind(on_press=lambda x: self.submit_payment(popup))
        btn_layout.add_widget(submit_btn)
        
        cancel_btn = Button(text='取消', font_name='chinese')
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(cancel_btn)
        
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
    def calculate_final_balance(self, *args):
        """计算最终余款"""
        try:
            proceeds = float(self.proceeds_input.text.strip()) if self.proceeds_input.text.strip() else 0
        except ValueError:
            proceeds = 0
        
        try:
            discount = float(self.discount_input.text.strip()) if self.discount_input.text.strip() else 0
        except ValueError:
            discount = 0
        
        try:
            deduction = float(self.deduction_input.text.strip()) if self.deduction_input.text.strip() else 0
        except ValueError:
            deduction = 0
        
        # 最终余款 = 当前余款 + 实收款 + 优惠额 - 扣除额
        # 注意：如果余款是负数（欠款），收款会减少欠款
        final_balance = self.current_balance + proceeds + discount - deduction
        
        self.final_balance_label.text = f'¥{final_balance:.2f}'
        
        # 根据余款正负设置颜色
        if final_balance < 0:
            self.final_balance_label.color = (1, 0, 0, 1)  # 红色（仍欠款）
        elif final_balance > 0:
            self.final_balance_label.color = (0, 0.6, 0, 1)  # 绿色（有结余）
        else:
            self.final_balance_label.color = (0, 0, 0, 1)  # 黑色（刚好结清）
    
    def submit_payment(self, popup):
        """提交收款数据"""
        # 验证输入
        try:
            proceeds = float(self.proceeds_input.text.strip()) if self.proceeds_input.text.strip() else 0
        except ValueError:
            self.show_message('错误', '收款金额格式不正确！')
            return
        
        try:
            discount = float(self.discount_input.text.strip()) if self.discount_input.text.strip() else 0
        except ValueError:
            self.show_message('错误', '优惠金额格式不正确！')
            return
        
        try:
            deduction = float(self.deduction_input.text.strip()) if self.deduction_input.text.strip() else 0
        except ValueError:
            self.show_message('错误', '扣除金额格式不正确！')
            return
        
        # 计算最终余款
        final_balance = self.current_balance + proceeds + discount - deduction
        
        # 生成新的订单号（用于记录收款操作）
        order_no = self.db.generate_order_no()
        
        try:
            # 插入收款记录到sales_orders表
            # 注意：这里total_quantity和total_amount设为0，因为这是纯收款操作
            self.db.execute_update(
                """INSERT INTO sales_orders 
                   (order_no, market, seller, total_quantity, total_amount, 
                    proceeds, proceeds_method, discount, deduction, balance)
                   VALUES (?, ?, ?, 0, 0, ?, ?, ?, ?, ?)""",
                (
                    order_no,
                    self.current_market,
                    self.current_seller,
                    proceeds,
                    self.payment_method_spinner.text,
                    discount,
                    deduction,
                    final_balance
                )
            )
            
            # 显示成功消息
            self.show_message('成功', f'收款记录已提交！\n订单号: {order_no}\n最终余款: ¥{final_balance:.2f}')
            
            # 关闭收款弹窗
            popup.dismiss()
            
            # 刷新余款列表
            self.load_balance_list()
            
        except Exception as e:
            self.show_message('错误', f'提交失败: {str(e)}')
            import traceback
            traceback.print_exc()
    
    def show_message(self, title, message):
        """显示消息对话框"""
        popup = Popup(title=title, size_hint=(0.4, 0.3))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        msg_label = Label(
            text=message,
            font_name='chinese',
            halign='center',
            valign='middle'
        )
        layout.add_widget(msg_label)
        
        ok_btn = Button(
            text='确定',
            size_hint_y=None,
            height=40,
            font_name='chinese'
        )
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(ok_btn)
        
        popup.add_widget(layout)
        popup.open()