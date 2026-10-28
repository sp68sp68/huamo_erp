"""
商品入库界面
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.core.text import LabelBase
import sys
import os

# 添加父目录到路径以导入database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager

class CustomDropDown(DropDown):
    """自定义下拉菜单，支持中文字体"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def add_item(self, text, callback, font_name='chinese'):
        """添加下拉项"""
        btn = Button(text=text, font_name=font_name, size_hint_y=None, height=35)
        btn.bind(on_release=lambda btn: self.select(btn.text))
        self.add_widget(btn)

class CustomDropDown(DropDown):
    """自定义下拉菜单，支持中文字体"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = kwargs.get('font_name', 'chinese')
    
    def add_item(self, text, callback):
        """添加下拉项"""
        btn = Button(text=text, font_name=self.font_name, size_hint_y=None, height=35)
        btn.bind(on_release=lambda btn: self.select(btn.text))
        self.add_widget(btn)


class StockInScreen(BoxLayout):
    """商品入库主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 存储已添加的商品列表
        self.order_items = []
        
        # 当前选定的市场和客户
        self.selected_market = None
        self.selected_supplier = None
        
        # 构建界面
        self.build_ui()
    
    def build_ui(self):
        """构建用户界面"""
        self.clear_widgets()
        
        # 顶部信息区域
        top_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=10)
        
        # 左侧：选择市场和供应商
        left_panel = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=5)
        
        # 市场选择 - 使用 Button + DropDown
        market_layout = BoxLayout(size_hint_y=None, height=35)
        market_layout.add_widget(Label(text='市场:', font_name='chinese', size_hint_x=None, width=60))
        self.market_btn = Button(text='请选择市场', font_name='chinese', size_hint_x=1)
        self.market_dropdown = CustomDropDown()
        self.market_dropdown.bind(on_select=lambda instance, x: self.on_market_selected(x))
        self.market_btn.bind(on_release=self.show_market_dropdown)
        market_layout.add_widget(self.market_btn)
        left_panel.add_widget(market_layout)
        
        # 供应商选择
        supplier_layout = BoxLayout(size_hint_y=None, height=35)
        supplier_layout.add_widget(Label(text='供应商:', font_name='chinese', size_hint_x=None, width=80))
        self.supplier_btn = Button(text='请先选择市场', font_name='chinese', size_hint_x=1)
        self.supplier_dropdown = CustomDropDown()
        self.supplier_dropdown.bind(on_select=lambda instance, x: self.on_supplier_selected(x))
        self.supplier_btn.bind(on_release=self.show_supplier_dropdown)
        supplier_layout.add_widget(self.supplier_btn)
        left_panel.add_widget(supplier_layout)
        
        # 商品选择
        product_layout = BoxLayout(size_hint_y=None, height=35)
        product_layout.add_widget(Label(text='商品:', font_name='chinese', size_hint_x=None, width=60))
        self.product_btn = Button(text='请选择商品', font_name='chinese', size_hint_x=1)
        self.product_dropdown = CustomDropDown()
        self.product_dropdown.bind(on_select=lambda instance, x: self.on_product_selected(x))
        self.product_btn.bind(on_release=self.show_product_dropdown)
        product_layout.add_widget(self.product_btn)
        left_panel.add_widget(product_layout)
                        
        top_info.add_widget(left_panel)
        
        # 右侧：商品选择和添加
        right_panel = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=5)      
                
        # 价格输入
        price_layout = BoxLayout(size_hint_y=None, height=35, spacing=5)
        price_layout.add_widget(Label(text='价格:', font_name='chinese', size_hint_x=None, width=60))
        self.price_input = TextInput(hint_text='价格', multiline=False, font_name='chinese', size_hint_x=0.4)
        price_layout.add_widget(self.price_input)
        right_panel.add_widget(price_layout)
        
        # 数量输入和添加按钮
        add_layout = BoxLayout(size_hint_y=None, height=35, spacing=5)
        add_layout.add_widget(Label(text='数量:', font_name='chinese', size_hint_x=None, width=60))
        self.quantity_input = TextInput(hint_text='数量', multiline=False, font_name='chinese', size_hint_x=0.4)
        add_layout.add_widget(self.quantity_input)
        
        add_btn = Button(text='添加商品', font_name='chinese', size_hint_x=0.3)
        add_btn.bind(on_press=self.add_product_to_order)
        add_layout.add_widget(add_btn)
        
        right_panel.add_widget(add_layout)
        
        top_info.add_widget(right_panel)
        
        self.add_widget(top_info)
        
        # 商品列表区域
        list_label = Label(text='已添加商品列表', size_hint_y=None, height=30, font_name='chinese')
        self.add_widget(list_label)
        
        scroll = ScrollView(size_hint=(1, 1))
        self.items_container = GridLayout(cols=5, size_hint_y=None, spacing=5, padding=[5, 5, 5, 5])
        self.items_container.bind(minimum_height=self.items_container.setter('height'))
        
        # 表头 - 使用固定高度
        header_height = 35
        header_font_size = 14
        self.items_container.add_widget(Label(text='商品名称', font_name='chinese', size_hint_x=0.3, font_size=header_font_size, height=header_height, size_hint_y=None))
        self.items_container.add_widget(Label(text='单价', font_name='chinese', size_hint_x=0.2, font_size=header_font_size, height=header_height, size_hint_y=None))
        self.items_container.add_widget(Label(text='数量', font_name='chinese', size_hint_x=0.2, font_size=header_font_size, height=header_height, size_hint_y=None))
        self.items_container.add_widget(Label(text='小计', font_name='chinese', size_hint_x=0.2, font_size=header_font_size, height=header_height, size_hint_y=None))
        self.items_container.add_widget(Label(text='操作', font_name='chinese', size_hint_x=0.1, font_size=header_font_size, height=header_height, size_hint_y=None))
        
        scroll.add_widget(self.items_container)
        self.add_widget(scroll)
        
        # 底部结算区域
        bottom_panel = BoxLayout(orientation='vertical', size_hint_y=None, height=200, spacing=5)
        
        # 总计显示
        total_layout = BoxLayout(size_hint_y=None, height=35)
        total_layout.add_widget(Label(text='总数量:', font_name='chinese', size_hint_x=None, width=80))
        self.total_quantity_label = Label(text='0', font_name='chinese', size_hint_x=0.2)
        total_layout.add_widget(self.total_quantity_label)
        total_layout.add_widget(Label(text='总金额:', font_name='chinese', size_hint_x=None, width=80))
        self.total_amount_label = Label(text='¥0.00', font_name='chinese', size_hint_x=0.2)
        total_layout.add_widget(self.total_amount_label)
        bottom_panel.add_widget(total_layout)
                        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        submit_btn = Button(text='确认提交', font_name='chinese')
        submit_btn.bind(on_press=self.submit_order)
        btn_layout.add_widget(submit_btn)
        
        cancel_btn = Button(text='取消', font_name='chinese')
        cancel_btn.bind(on_press=self.cancel_order)
        btn_layout.add_widget(cancel_btn)
        
        bottom_panel.add_widget(btn_layout)
        
        self.add_widget(bottom_panel)
        
        # 加载初始数据
        self.load_markets()
        self.load_products()
            
    def show_market_dropdown(self, instance):
        """显示市场下拉菜单"""
        print(f"DEBUG: 点击市场按钮")
        self.market_dropdown.open(instance)
    
    def show_supplier_dropdown(self, instance):
        """显示客户下拉菜单"""
        print(f"DEBUG: 点击供应商按钮")
        self.supplier_dropdown.open(instance)
    
    def show_product_dropdown(self, instance):
        """显示商品下拉菜单"""
        print(f"DEBUG: 点击商品按钮")
        self.product_dropdown.open(instance)
    
    def on_product_selected(self, text):
        """商品选择事件"""
        print(f"DEBUG: 商品选择触发 - text='{text}'")
        self.product_btn.text = text
              
    
    def load_markets(self):
        """加载市场列表"""
        try:
            cursor = self.db.execute_query("SELECT market FROM markets ORDER BY market")
            rows = cursor.fetchall()
            markets = [row['market'] for row in rows]
            print(f"DEBUG: 加载到 {len(markets)} 个市场: {markets}")
            
            # 清空并重新添加下拉项
            self.market_dropdown.clear_widgets()
            self.market_dropdown.add_item('请选择市场', lambda x: None)
            
            for market in markets:
                self.market_dropdown.add_item(market, lambda x: None)
                
        except Exception as e:
            print(f"ERROR: 加载市场失败: {e}")
            import traceback
            traceback.print_exc()
    
    def load_products(self):
        """加载商品列表"""
        try:
            cursor = self.db.execute_query("SELECT product_name FROM products ORDER BY product_name")
            rows = cursor.fetchall()
            products = [row['product_name'] for row in rows]
            print(f"DEBUG: 加载到 {len(products)} 个商品")
            
            # 清空并重新添加下拉项
            self.product_dropdown.clear_widgets()
            self.product_dropdown.add_item('请选择商品', lambda x: None)
            
            for product in products:
                self.product_dropdown.add_item(product, lambda x: None)
                
        except Exception as e:
            print(f"ERROR: 加载商品失败: {e}")
            import traceback
            traceback.print_exc()
    
    def on_market_selected(self, text):
        """市场选择事件"""
        print(f"DEBUG: 市场选择触发 - text='{text}'")
        self.market_btn.text = text
        
        if text == '请选择市场':
            self.selected_market = None
            self.supplier_btn.text = '请先选择市场'
            self.supplier_dropdown.clear_widgets()
            self.supplier_dropdown.add_item('请先选择市场', lambda x: None)
            self.selected_supplier = None            
            return
        
        self.selected_market = text
        print(f"DEBUG: 已选择市场: {self.selected_market}")
        
        # 加载该市场的客户
        try:
            cursor = self.db.execute_query(
                "SELECT supplier FROM suppliers WHERE market = ? ORDER BY supplier",
                (text,)
            )
            rows = cursor.fetchall()
            suppliers = [row['supplier'] for row in rows]
            print(f"DEBUG: 市场 '{text}' 下有 {len(suppliers)} 个供应商: {suppliers}")
            
            # 清空并重新添加下拉项
            self.supplier_dropdown.clear_widgets()
            
            if suppliers:
                self.supplier_dropdown.add_item('请选择客户', lambda x: None)
                for supplier in suppliers:
                    self.supplier_dropdown.add_item(supplier, lambda x: None)
                self.supplier_btn.text = '请选择供应商'
            else:
                self.supplier_dropdown.add_item('该市场暂无客户', lambda x: None)
                self.supplier_btn.text = '该市场暂无客户'
                
        except Exception as e:
            print(f"ERROR: 加载客户失败: {e}")
            import traceback
            traceback.print_exc()
        
        self.selected_supplier = None
            
    def on_supplier_selected(self, text):
        """供应商选择事件"""
        print(f"DEBUG: 供应商选择触发 - text='{text}'")
        self.supplier_btn.text = text
        
        if text in ['请先选择市场', '该市场暂无客户', '请选择客户', '请选择供应商']:
            self.selected_supplier = None            
            return
        
        self.selected_supplier = text
        print(f"DEBUG: 已选择供应商: {self.selected_supplier}")
        
    
    
    
    def add_product_to_order(self, instance):
        """添加商品到订单"""
        product_name = self.product_btn.text
        quantity_text = self.quantity_input.text.strip()
        price_text = self.price_input.text.strip()
        
        if not price_text:
            self.show_message('错误', '请输入价格！')
            return
        
        if product_name in ['请选择商品', '']:
            self.show_message('错误', '请选择商品！')
            return
        
        if not quantity_text:
            self.show_message('错误', '请输入数量！')
            return
        
        try:
            quantity = int(quantity_text)
        except ValueError:
            self.show_message('错误', '数量必须是整数！')
            return
        
        
        subtotal = float(price_text) * quantity
        
        # 添加到列表
        self.order_items.append({
            'product_name': product_name,
            'quantity': quantity,
            'retail_price': float(price_text),
            'subtotal': subtotal
        })
        
        # 刷新显示
        self.refresh_items_list()
        self.calculate_totals()
        
        # 清空数量输入
        self.quantity_input.text = ''
        self.price_input.text = ''
    
    def refresh_items_list(self):
        """刷新商品列表显示"""
        # 清除旧的项目（保留表头）
        while len(self.items_container.children) > 5:
            self.items_container.remove_widget(self.items_container.children[0])
        
        # 倒序显示（最新添加的在上面）
        for i, item in enumerate(reversed(self.order_items)):
            original_index = len(self.order_items) - 1 - i
            
            name_label = Label(text=item['product_name'], font_name='chinese', size_hint_x=0.3, height=35, size_hint_y=None)
            price_label = Label(text=f"¥{item['retail_price']:.2f}", font_name='chinese', size_hint_x=0.2, height=35, size_hint_y=None)
            qty_label = Label(text=str(item['quantity']), font_name='chinese', size_hint_x=0.2, height=35, size_hint_y=None)
            subtotal_label = Label(text=f"¥{item['subtotal']:.2f}", font_name='chinese', size_hint_x=0.2, height=35, size_hint_y=None)
            
            delete_btn = Button(text='删除', font_name='chinese', size_hint_x=0.1, height=35, size_hint_y=None)
            delete_btn.bind(on_press=lambda x, idx=original_index: self.remove_item(idx))
            
            self.items_container.add_widget(name_label)
            self.items_container.add_widget(price_label)
            self.items_container.add_widget(qty_label)
            self.items_container.add_widget(subtotal_label)
            self.items_container.add_widget(delete_btn)
    
    def remove_item(self, index):
        """删除商品项"""
        if 0 <= index < len(self.order_items):
            self.order_items.pop(index)
            self.refresh_items_list()
            self.calculate_totals()
    
    def calculate_totals(self):
        """计算总计"""
        total_quantity = sum(item['quantity'] for item in self.order_items)
        total_amount = sum(item['subtotal'] for item in self.order_items)
        
        self.total_quantity_label.text = str(total_quantity)
        self.total_amount_label.text = f'¥{total_amount:.2f}'
           
    def cancel_order(self, instance):
        """取消订单"""
        confirm_popup = Popup(title='确认取消', size_hint=(0.4, 0.3))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        msg_label = Label(text='确定要取消当前订单吗？\n所有已添加的商品将被清空。', font_name='chinese', halign='center')
        layout.add_widget(msg_label)
        
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        confirm_btn = Button(text='确认', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def do_cancel(instance):
            self.reset_form()
            confirm_popup.dismiss()
        
        confirm_btn.bind(on_press=do_cancel)
        cancel_btn.bind(on_press=lambda x: confirm_popup.dismiss())
        
        btn_row.add_widget(confirm_btn)
        btn_row.add_widget(cancel_btn)
        layout.add_widget(btn_row)
        
        confirm_popup.add_widget(layout)
        confirm_popup.open()
    
    def submit_order(self, instance):
        """提交订单"""
        # 验证必填项
        if not self.selected_market:
            self.show_message('错误', '请选择市场！')
            return
        
        if not self.selected_supplier:
            return
            self.show_message('错误', '请选择供应商！')
            return
        
        if not self.order_items:
            self.show_message('错误', '请至少添加一个商品！')
            return
        
        try:
            # 生成订单号
            order_no = self.db.generate_in_no()
            
            # 计算总计
            total_quantity = sum(item['quantity'] for item in self.order_items)
            total_amount = sum(item['subtotal'] for item in self.order_items)
                       
            # 插入销售单
            self.db.execute_update(
                """INSERT INTO stock_in_orders 
                   (in_no, market, supplier, total_quantity, total_amount)
                   VALUES (?, ?, ?, ?, ?)""",
                (order_no, self.selected_market, self.selected_supplier, 
                 total_quantity, total_amount)
            )
            # 获取订单ID
            cursor = self.db.execute_query(
                "SELECT in_no FROM stock_in_orders WHERE in_no = ?",
                (order_no,)
            )
            order_id = cursor.fetchone()['in_no']
            
            # 插入进货明细并更新库存
            for item in self.order_items:
                # 插入明细
                self.db.execute_update(
                    """INSERT INTO stock_in_items 
                       (in_no, product_name, quantity, cost_price, subtotal)
                       VALUES (?, ?, ?, ?, ?)""",
                    (order_id, item['product_name'], item['quantity'], 
                     item['retail_price'], item['subtotal'])
                )
                
                # 更新库存
                cursor = self.db.execute_query(
                    "SELECT product_name FROM stocks WHERE product_name = ?",
                    (item['product_name'],)
                )
                stock_name = cursor.fetchone()
                if stock_name:
                    self.db.execute_update(
                    """UPDATE stocks 
                       SET stock_quantity = stock_quantity + ? , cost_price = ? 
                       WHERE product_name = ?""",
                    (item['quantity'], item['retail_price'], item['product_name'])
                )
                else:
                    cursor = self.db.execute_query(
                    "SELECT retail_price FROM products WHERE product_name = ?",
                    (item['product_name'],)
                    )
                    retail_price = cursor.fetchone()['retail_price']
                    self.db.execute_update(
                        """INSERT INTO stocks (product_name, stock_quantity, cost_price, sell_price) 
                           VALUES (?, ?, ?, ?)""",
                        (item['product_name'], item['quantity'], item['retail_price'], retail_price)
                    )
            
            self.show_message('成功', f'订单 {order_no} 提交成功！')
            
            # 重置界面
            self.reset_form()
            
        except Exception as e:
            self.show_message('错误', f'提交失败: {str(e)}')
            import traceback
            traceback.print_exc()
    
    def reset_form(self):
        """重置表单"""
        self.order_items = []
        self.selected_market = None
        self.selected_supplier = None
        
        self.market_btn.text = '请选择市场'
        self.supplier_btn.text = '请先选择市场'
        self.supplier_dropdown.clear_widgets()
        self.supplier_dropdown.add_item('请先选择市场', lambda x: None)
        self.product_btn.text = '请选择商品'
        self.price_input.text = ''        
        self.quantity_input.text = ''
        
        
        self.total_quantity_label.text = '0'
        self.total_amount_label.text = '0'
        
        self.refresh_items_list()
        self.load_markets()
        self.load_products()
    
    def show_message(self, title, message):
        """显示消息对话框"""
        popup = Popup(title=title, size_hint=(0.4, 0.3))
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        msg_label = Label(text=message, font_name='chinese', halign='center', valign='middle')
        layout.add_widget(msg_label)
        
        ok_btn = Button(text='确定', size_hint_y=None, height=40, font_name='chinese')
        ok_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(ok_btn)
        
        popup.add_widget(layout)
        popup.open()