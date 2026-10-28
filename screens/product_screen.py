"""
产品管理界面
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
import sys
import os

# 添加父目录到路径以导入database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager


class ProductManagementScreen(BoxLayout):
    """产品管理主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 顶部按钮区域
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='添加产品', font_name='chinese')
        add_btn.bind(on_press=self.show_add_product)
        top_bar.add_widget(add_btn)
        
        modify_btn = Button(text='修改产品', font_name='chinese')
        modify_btn.bind(on_press=self.show_modify_product)
        top_bar.add_widget(modify_btn)
        
        delete_btn = Button(text='删除产品', font_name='chinese')
        delete_btn.bind(on_press=self.show_delete_product)
        top_bar.add_widget(delete_btn)        
                
        self.add_widget(top_bar)
        
        # 产品列表显示区域
        self.load_product_list()
    
    def load_product_list(self):
        """加载产品列表"""
        # 清除旧的列表
        if hasattr(self, 'product_scroll'):
            self.remove_widget(self.product_scroll)
        
        # 创建滚动视图
        scroll = ScrollView(size_hint=(1, 1))
        self.product_scroll = scroll
        
        self.product_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.product_list_container.bind(minimum_height=self.product_list_container.setter('height'))
        
        # 获取所有产品
        cursor = self.db.execute_query("SELECT * FROM products ORDER BY id")
        products = cursor.fetchall()      
                
        if not products:
            empty_label = Label(text='暂无产品数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.product_list_container.add_widget(empty_label)
        else:
            for product in products:
                product_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                product_name_label = Label(text=f"产品名: {product['product_name']}", font_name='chinese', size_hint_x=0.3)
                width_label = Label(text=f"宽度: {product['width']}", font_name='chinese', size_hint_x=0.3)
                length_label = Label(text=f"长度: {product['length']}", font_name='chinese', size_hint_x=0.3)
                bundles_label = Label(text=f"扎量: {product['bundles']}", font_name='chinese', size_hint_x=0.3)
                bundles_num_label = Label(text=f"扎数: {product['bundles_num']}", font_name='chinese', size_hint_x=0.3)                
                piece_w_label = Label(text=f"件数: {product['piece_w']}", font_name='chinese', size_hint_x=0.3)                
                look_label = Label(text=f"件数: {product['look']}", font_name='chinese', size_hint_x=0.3)             
                retail_price_label = Label(text=f"价格: {product['retail_price']}", font_name='chinese', size_hint_x=0.3)
                alert_quantity_label = Label(text=f"警戒量: {product['alert_quantity']}", font_name='chinese', size_hint_x=0.3)
                
                product_row.add_widget(product_name_label)
                product_row.add_widget(width_label)
                product_row.add_widget(length_label)
                product_row.add_widget(bundles_label)
                product_row.add_widget(bundles_num_label)
                product_row.add_widget(piece_w_label)
                product_row.add_widget(look_label)
                product_row.add_widget(retail_price_label)
                product_row.add_widget(alert_quantity_label)
                                
                self.product_list_container.add_widget(product_row)
        
        scroll.add_widget(self.product_list_container)
        self.add_widget(scroll)
    
    def show_add_product(self, instance):
        """显示添加产品对话框"""
        popup = Popup(title='添加产品 ', size_hint=(0.6, 0.7), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 产品名输入
        product_name_layout = BoxLayout(size_hint_y=None, height=40)
        product_name_layout.add_widget(Label(text='产品名:', font_name='chinese', size_hint_x=None, width=80))
        product_name_input = TextInput(hint_text='请输入产品名', multiline=False, font_name='chinese')
        product_name_layout.add_widget(product_name_input)
        layout.add_widget(product_name_layout)
        # 宽度输入
        width_layout = BoxLayout(size_hint_y=None, height=40)
        width_layout.add_widget(Label(text='宽度:', font_name='chinese', size_hint_x=None, width=80))
        width_input = TextInput(hint_text='请输入宽度', multiline=False, font_name='chinese')
        width_layout.add_widget(width_input)
        layout.add_widget(width_layout)
        # 长度输入
        length_layout = BoxLayout(size_hint_y=None, height=40)
        length_layout.add_widget(Label(text='长度:', font_name='chinese', size_hint_x=None, width=80))
        length_input = TextInput(hint_text='请输入长度', multiline=False, font_name='chinese')
        length_layout.add_widget(length_input)
        layout.add_widget(length_layout)
        
        # 扎量输入
        bundles_num_layout = BoxLayout(size_hint_y=None, height=40)
        bundles_num_layout.add_widget(Label(text='扎量:', font_name='chinese', size_hint_x=None, width=80))
        bundles_num_input = TextInput(hint_text='请输入扎量', multiline=False, font_name='chinese')
        bundles_num_layout.add_widget(bundles_num_input)
        layout.add_widget(bundles_num_layout)
        
        # 扎数输入
        bundles_layout = BoxLayout(size_hint_y=None, height=40)
        bundles_layout.add_widget(Label(text='扎数:', font_name='chinese', size_hint_x=None, width=80))
        bundles_input = TextInput(hint_text='请输入扎数', multiline=False, font_name='chinese')
        bundles_layout.add_widget(bundles_input)
        layout.add_widget(bundles_layout)      
        
        
        # 外观输入
        look_layout = BoxLayout(size_hint_y=None, height=40)
        look_layout.add_widget(Label(text='外观:', font_name='chinese', size_hint_x=None, width=80))
        look_input = TextInput(hint_text='请输入外观', multiline=False, font_name='chinese')
        look_layout.add_widget(look_input)
        layout.add_widget(look_layout)
        
        # 件重输入
        piece_w_layout = BoxLayout(size_hint_y=None, height=40)
        piece_w_layout.add_widget(Label(text='件重:', font_name='chinese', size_hint_x=None, width=80))
        piece_w_input = TextInput(hint_text='请输入件重', multiline=False, font_name='chinese')
        piece_w_layout.add_widget(piece_w_input)
        layout.add_widget(piece_w_layout)
        
        
        # 警戒数量输入
        alert_quantity_layout = BoxLayout(size_hint_y=None, height=40)
        alert_quantity_layout.add_widget(Label(text='警戒数量:', font_name='chinese', size_hint_x=None, width=80))
        alert_quantity_input = TextInput(hint_text='请输入警戒数量', multiline=False, font_name='chinese')
        alert_quantity_layout.add_widget(alert_quantity_input)
        layout.add_widget(alert_quantity_layout)
        
        
        # 零售价格输入
        retail_price_layout = BoxLayout(size_hint_y=None, height=40)
        retail_price_layout.add_widget(Label(text='零售价格:', font_name='chinese', size_hint_x=None, width=80))
        retail_price_input = TextInput(hint_text='请输入零售价格', multiline=False, font_name='chinese')
        retail_price_layout.add_widget(retail_price_input)
        layout.add_widget(retail_price_layout)
        
        # 按钮区域
        submit_btn = Button(text='提交', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def submit_add(instance):
            product_name = product_name_input.text.strip()
            product_width = width_input.text.strip()
            product_length = length_input.text.strip()
            product_bundles = bundles_input.text.strip()
            product_bundles_num = bundles_num_input.text.strip()
            product_piece_w = piece_w_input.text.strip()
            product_look = look_input.text.strip()
            product_retail_price = retail_price_input.text.strip()
            product_alert_quantity = alert_quantity_input.text.strip()
            
            if not product_name:
                self.show_message('错误', '产品名不能为空！')
                return
            
            try:                               
                self.db.execute_update(
                    "INSERT INTO products (product_name, width, length, bundles, bundles_num, piece_w, look, retail_price, alert_quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (product_name, product_width, product_length, product_bundles, product_bundles_num, product_piece_w, product_look, product_retail_price, product_alert_quantity)
                )
                self.show_message('成功', f'产品 {product_name} 添加成功！')
                popup.dismiss()
                self.load_product_list()
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    self.show_message('错误', f'产品名 {product_name} 已存在！')
                else:
                    self.show_message('错误', f'添加失败: {str(e)}')
        
        submit_btn.bind(on_press=submit_add)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10) 
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_modify_product(self, instance):
        """显示修改产品界面"""
        popup = Popup(title='修改产品', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 产品列表
        scroll = ScrollView(size_hint=(1, 1))
        product_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        product_grid.bind(minimum_height=product_grid.setter('height'))
        
        # 获取所有产品
        cursor = self.db.execute_query("SELECT * FROM products ORDER BY id")  
        products = cursor.fetchall()
        
        # ... existing code ...

        if not products:
            empty_label = Label(text='暂无产品数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            product_grid.add_widget(empty_label)
        else:
            for product in products:
                product_row = BoxLayout(size_hint_y=None, height=40, spacing=5, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"ID: {product['id']} | 产品名: {product['product_name']} | 宽度: {product['width']} | 长度: {product['length']} | 扎数: {product['bundles']} | 扎量: {product['bundles_num']} | 件重: {product['piece_w']} | 外观: {product['look']} | 零售价格: {product['retail_price']} | 警戒数量: {product['alert_quantity']}",
                    font_name='chinese',
                    size_hint_x=0.7
                )
                
                modify_btn = Button(text='修改', font_name='chinese', size_hint_x=0.3)
                
                def create_modify_handler(mid, pname, pwidth, plength, pbundles, pbundles_num, plook, ppiece_w, pprice, palert):
                    def handler(instance):
                        # 打开修改对话框
                        modify_popup = Popup(title='修改产品', size_hint=(0.8, 0.9), auto_dismiss=False)
                        modify_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
                        
                        # 标题
                        title_label = Label(text=f'修改产品: {pname}', font_size=18, font_name='chinese', size_hint_y=None, height=30)
                        modify_layout.add_widget(title_label)
                        
                        # 产品名输入（禁用）
                        product_name_layout = BoxLayout(size_hint_y=None, height=40)
                        product_name_layout.add_widget(Label(text='产品名:', font_name='chinese', size_hint_x=None, width=80))
                        product_name_input = TextInput(text=pname, multiline=False, font_name='chinese', disabled=True)
                        product_name_layout.add_widget(product_name_input)
                        modify_layout.add_widget(product_name_layout)
                        
                        # 宽度输入
                        width_layout = BoxLayout(size_hint_y=None, height=40)
                        width_layout.add_widget(Label(text='宽度:', font_name='chinese', size_hint_x=None, width=80))
                        width_input = TextInput(text=str(pwidth) if pwidth else '', multiline=False, font_name='chinese')
                        width_layout.add_widget(width_input)
                        modify_layout.add_widget(width_layout)
                        
                        # 长度输入
                        length_layout = BoxLayout(size_hint_y=None, height=40)
                        length_layout.add_widget(Label(text='长度:', font_name='chinese', size_hint_x=None, width=80))
                        length_input = TextInput(text=str(plength) if plength else '', multiline=False, font_name='chinese')
                        length_layout.add_widget(length_input)
                        modify_layout.add_widget(length_layout)

                        # 扎量输入
                        bundles_num_layout = BoxLayout(size_hint_y=None, height=40)
                        bundles_num_layout.add_widget(Label(text='扎量:', font_name='chinese', size_hint_x=None, width=80))
                        bundles_num_input = TextInput(text=str(pbundles_num) if pbundles_num else '', multiline=False, font_name='chinese')
                        bundles_num_layout.add_widget(bundles_num_input)
                        modify_layout.add_widget(bundles_num_layout)
        
                        # 扎数输入
                        bundles_layout = BoxLayout(size_hint_y=None, height=40)
                        bundles_layout.add_widget(Label(text='扎数:', font_name='chinese', size_hint_x=None, width=80))
                        bundles_input = TextInput(text=str(pbundles) if pbundles else '', multiline=False, font_name='chinese')
                        bundles_layout.add_widget(bundles_input)
                        modify_layout.add_widget(bundles_layout)      
        
                        # 外观输入
                        look_layout = BoxLayout(size_hint_y=None, height=40)
                        look_layout.add_widget(Label(text='外观:', font_name='chinese', size_hint_x=None, width=80))
                        look_input = TextInput(text=plook if plook else '', multiline=False, font_name='chinese')
                        look_layout.add_widget(look_input)
                        modify_layout.add_widget(look_layout)
        
                        # 件重输入
                        piece_w_layout = BoxLayout(size_hint_y=None, height=40)
                        piece_w_layout.add_widget(Label(text='件重:', font_name='chinese', size_hint_x=None, width=80))
                        piece_w_input = TextInput(text=str(ppiece_w) if ppiece_w else '', multiline=False, font_name='chinese')
                        piece_w_layout.add_widget(piece_w_input)
                        modify_layout.add_widget(piece_w_layout)
                            
                        # 警戒数量输入
                        alert_quantity_layout = BoxLayout(size_hint_y=None, height=40)
                        alert_quantity_layout.add_widget(Label(text='警戒数量:', font_name='chinese', size_hint_x=None, width=80))
                        alert_quantity_input = TextInput(text=str(palert) if palert else '0', multiline=False, font_name='chinese')
                        alert_quantity_layout.add_widget(alert_quantity_input)
                        modify_layout.add_widget(alert_quantity_layout)
                        
                        # 零售价格输入
                        retail_price_layout = BoxLayout(size_hint_y=None, height=40)
                        retail_price_layout.add_widget(Label(text='零售价格:', font_name='chinese', size_hint_x=None, width=80))
                        retail_price_input = TextInput(text=str(pprice) if pprice else '0', multiline=False, font_name='chinese')
                        retail_price_layout.add_widget(retail_price_input)
                        modify_layout.add_widget(retail_price_layout)
                        
                        # 按钮
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        save_btn = Button(text='保存', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_save(instance):
                            try:
                                product_width = float(width_input.text.strip()) if width_input.text.strip() else None
                                product_length = float(length_input.text.strip()) if length_input.text.strip() else None
                                product_bundles = int(bundles_input.text.strip()) if bundles_input.text.strip() else None
                                product_bundles_num = int(bundles_num_input.text.strip()) if bundles_num_input.text.strip() else None
                                product_piece_w = float(piece_w_input.text.strip()) if piece_w_input.text.strip() else None
                                product_retail_price = float(retail_price_input.text.strip()) if retail_price_input.text.strip() else 0
                                product_alert_quantity = int(alert_quantity_input.text.strip()) if alert_quantity_input.text.strip() else 0
                                product_look = look_input.text.strip()
                                
                                self.db.execute_update(
                                    "UPDATE products SET width = ?, length = ?, bundles = ?, bundles_num = ?, piece_w = ?, look = ?, retail_price = ?, alert_quantity = ? WHERE id = ?",
                                    (product_width, product_length, product_bundles, product_bundles_num, product_piece_w, product_look, product_retail_price, product_alert_quantity, mid)
                                )
                                self.show_message('成功', f'产品 {pname} 修改成功！')
                                modify_popup.dismiss()
                                popup.dismiss()
                                self.load_product_list()
                                self.show_modify_product(None)
                            except ValueError as e:
                                self.show_message('错误', '请输入有效的数值！')
                            except Exception as e:
                                self.show_message('错误', f'修改失败: {str(e)}')
                        
                        save_btn.bind(on_press=do_save)
                        cancel_btn.bind(on_press=lambda x: modify_popup.dismiss())
                        
                        btn_row.add_widget(save_btn)
                        btn_row.add_widget(cancel_btn)
                        modify_layout.add_widget(btn_row)
                        
                        modify_popup.add_widget(modify_layout)
                        modify_popup.open()
                    
                    return handler
                
                modify_btn.bind(on_press=create_modify_handler(product['id'], product['product_name'], product['width'], product['length'], product['bundles'], product['bundles_num'], product['look'], product['piece_w'], product['retail_price'], product['alert_quantity']))
                
                product_row.add_widget(info_label)
                product_row.add_widget(modify_btn)
                product_grid.add_widget(product_row)

# ... existing code ...
        scroll.add_widget(product_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_delete_product(self, instance):
        """显示删除产品界面"""
        popup = Popup(title='删除产品', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 产品列表
        scroll = ScrollView(size_hint=(1, 1))
        product_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        product_grid.bind(minimum_height=product_grid.setter('height'))
        
        # 获取所有产品
        cursor = self.db.execute_query("SELECT * FROM products ORDER BY id")  
        products = cursor.fetchall()
        
        if not products:
            empty_label = Label(text='暂无产品数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            product_grid.add_widget(empty_label)
        else:
            for product in products:
                product_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])      
                product_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"ID: {product['id']} | 产品名: {product['product_name']} | 宽度: {product['width']} | 长度: {product['length']} | 扎数: {product['bundles']} | 扎量: {product['bundles_num']} | 件重: {product['piece_w']} | 外观: {product['look']} | 零售价格: {product['retail_price']} | 警戒数量: {product['alert_quantity']}",
                    font_name='chinese',
                    size_hint_x=0.7
                )
                
                delete_btn = Button(text='删除', font_name='chinese', size_hint_x=0.3)
                
                def create_delete_handler(uid, uname):
                    def handler(instance):
                        confirm_popup = Popup(
                            title='确认删除',
                            size_hint=(0.4, 0.3)
                        )
                        confirm_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
                        
                        msg_label = Label(
                            text=f'确定要删除产品 "{uname}" 吗？\n此操作不可恢复！',
                            font_name='chinese',
                            halign='center'
                        )
                        
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        confirm_btn = Button(text='确认', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_delete(instance):
                            try:
                                self.db.execute_update("DELETE FROM products WHERE id = ?", (uid,))
                                self.show_message('成功', f'产品 {uname} 已删除！')
                                confirm_popup.dismiss()
                                popup.dismiss()
                                self.load_product_list()
                                self.show_delete_product(None)
                            except Exception as e:
                                self.show_message('错误', f'删除失败: {str(e)}')
                        
                        confirm_btn.bind(on_press=do_delete)
                        cancel_btn.bind(on_press=lambda x: confirm_popup.dismiss())
                        
                        btn_row.add_widget(confirm_btn)
                        btn_row.add_widget(cancel_btn)
                        
                        confirm_layout.add_widget(msg_label)
                        confirm_layout.add_widget(btn_row)
                        confirm_popup.add_widget(confirm_layout)
                        confirm_popup.open()
                    
                    return handler
                
                delete_btn.bind(on_press=create_delete_handler(product['id'], product['product_name']))
                
                product_row.add_widget(info_label)
                product_row.add_widget(delete_btn)
                product_grid.add_widget(product_row)
        
        scroll.add_widget(product_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
            
    def show_reset_product(self, instance):
        """显示重置产品对话框"""        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
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
    
    