"""
销售客户管理界面
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
import sys
import os

# 添加父目录到路径以导入database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DatabaseManager


class SellerManagementScreen(BoxLayout):
    """销售客户管理界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 顶部按钮区域
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='添加销售客户', font_name='chinese')
        add_btn.bind(on_press=self.show_add_seller)
        top_bar.add_widget(add_btn)
        
        modify_btn = Button(text='修改销售客户', font_name='chinese')   
        modify_btn.bind(on_press=self.show_modify_seller)
        top_bar.add_widget(modify_btn)
        
        delete_btn = Button(text='删除销售客户', font_name='chinese')
        delete_btn.bind(on_press=self.show_delete_seller)
        top_bar.add_widget(delete_btn)        
        
        self.add_widget(top_bar)
        
        # 销售客户列表显示区域
        self.load_seller_list()
    
    def load_seller_list(self):
        """加载销售客户列表"""
        # 清除旧的列表容器和滚动视图
        if hasattr(self, 'seller_scroll'):
            self.remove_widget(self.seller_scroll)
        
        # 创建滚动视图
        scroll = ScrollView(size_hint=(1, 1))
        self.seller_scroll = scroll
        
        self.seller_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.seller_list_container.bind(minimum_height=self.seller_list_container.setter('height'))
        
        # 获取所有销售客户
        cursor = self.db.execute_query("SELECT * FROM sellers ORDER BY id")
        sellers = cursor.fetchall()      
                
        if not sellers:
            empty_label = Label(text='暂无销售客户数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.seller_list_container.add_widget(empty_label)
        else:
            for seller in sellers:
                seller_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
               
                market_label = Label(text=f"市场: {seller['market']}", font_name='chinese', size_hint_x=0.2)
                seller_label = Label(text=f"销售客户: {seller['seller']}", font_name='chinese', size_hint_x=0.2)
                contact_person_label = Label(text=f"联系人: {seller['contact_person']}", font_name='chinese', size_hint_x=0.2)
                phone_label = Label(text=f"电话: {seller['phone']}", font_name='chinese', size_hint_x=0.2)
                address_label = Label(text=f"地址: {seller['address']}", font_name='chinese', size_hint_x=0.2)
                wechat_label = Label(text=f"微信: {seller['wechat']}", font_name='chinese', size_hint_x=0.2)
                alipay_label = Label(text=f"支付宝号: {seller['alipay_account']}", font_name='chinese', size_hint_x=0.2)
                bank_account_label = Label(text=f"银行账户: {seller['bank_account']}", font_name='chinese', size_hint_x=0.2)
                
                seller_row.add_widget(market_label)
                seller_row.add_widget(seller_label)
                seller_row.add_widget(contact_person_label)
                seller_row.add_widget(phone_label)
                seller_row.add_widget(address_label)
                seller_row.add_widget(wechat_label)
                seller_row.add_widget(alipay_label)
                seller_row.add_widget(bank_account_label)
                                 
                self.seller_list_container.add_widget(seller_row)
        
        scroll.add_widget(self.seller_list_container)
        self.add_widget(scroll)
    
    def show_add_seller(self, instance):
        """显示添加销售客户对话框"""
        popup = Popup(title='添加销售客户', size_hint=(0.7, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title_label = Label(text='请填写销售客户信息', font_size=16, font_name='chinese', size_hint_y=None, height=30)
        layout.add_widget(title_label)
        
        # 创建滚动视图用于表单
        form_scroll = ScrollView(size_hint=(1, 1))
        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # 加载市场列表
        cursor = self.db.execute_query("SELECT market FROM markets ORDER BY market")
        markets = [row['market'] for row in cursor.fetchall()]
        market_values = ['请选择市场'] + markets if markets else ['暂无市场']
        
        # 市场选择
        market_layout = BoxLayout(size_hint_y=None, height=40)
        market_layout.add_widget(Label(text='市场:', font_name='chinese', size_hint_x=None, width=80))
        
        self.market_btn = Button(text='请选择市场', font_name='chinese', size_hint_x=1)
        self.market_dropdown = DropDown()
        
        for market in markets:
            btn = Button(text=market, font_name='chinese', size_hint_y=None, height=35)
            btn.bind(on_release=lambda btn: self.market_dropdown.select(btn.text))
            self.market_dropdown.add_widget(btn)
        
        self.market_dropdown.bind(on_select=lambda instance, x: setattr(self.market_btn, 'text', x))
        self.market_btn.bind(on_release=self.market_dropdown.open)
        
        market_layout.add_widget(self.market_btn)
        form_layout.add_widget(market_layout)
        
        # 销售客户名输入
        seller_layout = BoxLayout(size_hint_y=None, height=40)
        seller_layout.add_widget(Label(text='销售客户名:', font_name='chinese', size_hint_x=None, width=80))
        seller_input = TextInput(hint_text='请输入销售客户名', multiline=False, font_name='chinese')
        seller_layout.add_widget(seller_input)
        form_layout.add_widget(seller_layout)
        
        # 地址输入
        address_layout = BoxLayout(size_hint_y=None, height=40)
        address_layout.add_widget(Label(text='地址:', font_name='chinese', size_hint_x=None, width=80))
        address_input = TextInput(hint_text='请输入地址', multiline=False, font_name='chinese')
        address_layout.add_widget(address_input)
        form_layout.add_widget(address_layout)
        
        # 电话输入
        phone_layout = BoxLayout(size_hint_y=None, height=40)
        phone_layout.add_widget(Label(text='电话:', font_name='chinese', size_hint_x=None, width=80))
        phone_input = TextInput(hint_text='请输入电话', multiline=False, font_name='chinese')
        phone_layout.add_widget(phone_input)
        form_layout.add_widget(phone_layout)
        
        # 联系人输入
        contact_person_layout = BoxLayout(size_hint_y=None, height=40)
        contact_person_layout.add_widget(Label(text='联系人:', font_name='chinese', size_hint_x=None, width=80))
        contact_person_input = TextInput(hint_text='请输入联系人', multiline=False, font_name='chinese')
        contact_person_layout.add_widget(contact_person_input)
        form_layout.add_widget(contact_person_layout)
        
        # 微信号输入
        wechat_layout = BoxLayout(size_hint_y=None, height=40)
        wechat_layout.add_widget(Label(text='微信号:', font_name='chinese', size_hint_x=None, width=80))
        wechat_input = TextInput(hint_text='请输入微信号', multiline=False, font_name='chinese')
        wechat_layout.add_widget(wechat_input)
        form_layout.add_widget(wechat_layout)       
                     
        # 支付宝输入
        alipay_layout = BoxLayout(size_hint_y=None, height=40)
        alipay_layout.add_widget(Label(text='支付宝号:', font_name='chinese', size_hint_x=None, width=80))
        alipay_input = TextInput(hint_text='请输入支付宝号', multiline=False, font_name='chinese')
        alipay_layout.add_widget(alipay_input)
        form_layout.add_widget(alipay_layout)
        
        # 银行账户输入
        bank_account_layout = BoxLayout(size_hint_y=None, height=40)
        bank_account_layout.add_widget(Label(text='银行账户:', font_name='chinese', size_hint_x=None, width=80))
        bank_account_input = TextInput(hint_text='请输入银行账户', multiline=False, font_name='chinese')
        bank_account_layout.add_widget(bank_account_input)
        form_layout.add_widget(bank_account_layout)
        
        form_scroll.add_widget(form_layout)
        layout.add_widget(form_scroll)
               
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        submit_btn = Button(text='提交', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def submit_add(instance):
            market = self.market_btn.text.strip()
            seller_name = seller_input.text.strip()
            seller_address = address_input.text.strip()
            seller_phone = phone_input.text.strip()
            seller_contact_person = contact_person_input.text.strip()
            seller_wechat = wechat_input.text.strip()
            seller_alipay = alipay_input.text.strip()
            seller_bank_account = bank_account_input.text.strip()
            
            if market == '请选择市场' or market == '暂无市场':
                self.show_message('错误', '请选择市场！')
                return
            
            if not seller_name:
                self.show_message('错误', '销售客户名不能为空！')
                return
            
            try:       
                self.db.execute_update(
                    "INSERT INTO sellers (market, seller, address, phone, contact_person, wechat, alipay_account, bank_account) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (market, seller_name, seller_address, seller_phone, seller_contact_person, seller_wechat, seller_alipay, seller_bank_account)
                )
                self.show_message('成功', f'销售客户 {seller_name} 添加成功！')
                popup.dismiss()
                self.load_seller_list()
            except Exception as e:
                self.show_message('错误', f'添加失败: {str(e)}')
        
        submit_btn.bind(on_press=submit_add)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_modify_seller(self, instance):
        """显示修改销售客户界面"""
        popup = Popup(title='修改销售客户', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 销售客户列表
        scroll = ScrollView(size_hint=(1, 1))
        seller_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        seller_grid.bind(minimum_height=seller_grid.setter('height'))
        
        # 获取所有销售客户
        cursor = self.db.execute_query("SELECT * FROM sellers ORDER BY id")
        sellers = cursor.fetchall()
        
        if not sellers:
            empty_label = Label(text='暂无销售客户数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            seller_grid.add_widget(empty_label)
        else:
            for seller in sellers:
                seller_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"市场: {seller['market']} | 销售客户: {seller['seller']} | 地址: {seller['address']}| 联系人: {seller['contact_person']} | 电话: {seller['phone']}| 微信: {seller['wechat']} | 支付宝: {seller['alipay_account']} | 银行账户: {seller['bank_account']}",
                    font_name='chinese',
                    size_hint_x=0.7
                )
                
                modify_btn = Button(text='修改', font_name='chinese', size_hint_x=0.3)
                
                def create_modify_handler(sid, smarket, sname, saddress, sphone, scontact, swechat, salipay, sbank):
                    def handler(instance):
                        # 打开修改对话框
                        modify_popup = Popup(title='修改销售客户', size_hint=(0.7, 0.8), auto_dismiss=False)
                        modify_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
                        
                        # 标题
                        title_label = Label(text=f'修改销售客户: {sname}', font_size=16, font_name='chinese', size_hint_y=None, height=30)
                        modify_layout.add_widget(title_label)
                        
                        # 表单滚动
                        form_scroll = ScrollView(size_hint=(1, 1))
                        form_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
                        form_layout.bind(minimum_height=form_layout.setter('height'))
                        
                        # 市场选择
                        
                        cursor = self.db.execute_query("SELECT market FROM markets ORDER BY market")
                        markets = [row['market'] for row in cursor.fetchall()]
                        
                        market_layout = BoxLayout(size_hint_y=None, height=40)
                        market_layout.add_widget(Label(text='市场:', font_name='chinese', size_hint_x=None, width=80))
                        
                        self.modify_market_btn = Button(text=smarket, font_name='chinese', size_hint_x=1)
                        self.modify_market_dropdown = DropDown()
                        
                        for market in markets:
                            btn = Button(text=market, font_name='chinese', size_hint_y=None, height=35)
                            btn.bind(on_release=lambda btn: self.modify_market_dropdown.select(btn.text))
                            self.modify_market_dropdown.add_widget(btn)
                        
                        self.modify_market_dropdown.bind(on_select=lambda instance, x: setattr(self.modify_market_btn, 'text', x))
                        self.modify_market_btn.bind(on_release=self.modify_market_dropdown.open)
                        
                        market_layout.add_widget(self.modify_market_btn)
                        form_layout.add_widget(market_layout)
                        
                        # 销售客户名（禁用）
                        name_layout = BoxLayout(size_hint_y=None, height=40)
                        name_layout.add_widget(Label(text='销售客户名:', font_name='chinese', size_hint_x=None, width=80))
                        name_input = TextInput(text=sname, multiline=False, font_name='chinese', disabled=True)
                        name_layout.add_widget(name_input)
                        form_layout.add_widget(name_layout)
                        
                        # 地址
                        addr_layout = BoxLayout(size_hint_y=None, height=40)
                        addr_layout.add_widget(Label(text='地址:', font_name='chinese', size_hint_x=None, width=80))
                        addr_input = TextInput(text=saddress if saddress else '', multiline=False, font_name='chinese')
                        addr_layout.add_widget(addr_input)
                        form_layout.add_widget(addr_layout)
                        
                        # 电话
                        phone_layout = BoxLayout(size_hint_y=None, height=40)
                        phone_layout.add_widget(Label(text='电话:', font_name='chinese', size_hint_x=None, width=80))
                        phone_input = TextInput(text=sphone if sphone else '', multiline=False, font_name='chinese')
                        phone_layout.add_widget(phone_input)
                        form_layout.add_widget(phone_layout)
                        
                        # 联系人
                        contact_layout = BoxLayout(size_hint_y=None, height=40)
                        contact_layout.add_widget(Label(text='联系人:', font_name='chinese', size_hint_x=None, width=80))
                        contact_input = TextInput(text=scontact if scontact else '', multiline=False, font_name='chinese')
                        contact_layout.add_widget(contact_input)
                        form_layout.add_widget(contact_layout)
                        
                        # 微信号
                        wechat_layout = BoxLayout(size_hint_y=None, height=40)
                        wechat_layout.add_widget(Label(text='微信号:', font_name='chinese', size_hint_x=None, width=80))
                        wechat_input = TextInput(text=swechat if swechat else '', multiline=False, font_name='chinese')
                        wechat_layout.add_widget(wechat_input)
                        form_layout.add_widget(wechat_layout)
                        
                        # 支付宝
                        alipay_layout = BoxLayout(size_hint_y=None, height=40)
                        alipay_layout.add_widget(Label(text='支付宝号:', font_name='chinese', size_hint_x=None, width=80))
                        alipay_input = TextInput(text=salipay if salipay else '', multiline=False, font_name='chinese')
                        alipay_layout.add_widget(alipay_input)
                        form_layout.add_widget(alipay_layout)
                        
                        # 银行账户
                        bank_layout = BoxLayout(size_hint_y=None, height=40)
                        bank_layout.add_widget(Label(text='银行账户:', font_name='chinese', size_hint_x=None, width=80))
                        bank_input = TextInput(text=sbank if sbank else '', multiline=False, font_name='chinese')
                        bank_layout.add_widget(bank_input)
                        form_layout.add_widget(bank_layout)
                        
                        form_scroll.add_widget(form_layout)
                        modify_layout.add_widget(form_scroll)
                        
                        # 按钮
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        save_btn = Button(text='保存', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_save(instance):                            
                            new_market = self.modify_market_btn.text.strip()
                            if new_market == '请选择市场' or new_market == '暂无市场':
                                self.show_message('错误', '请选择市场！')
                                return
                            
                            try:
                                self.db.execute_update(
                                    "UPDATE sellers SET market = ?, address = ?, phone = ?, contact_person = ?, wechat = ?, alipay_account = ?, bank_account = ? WHERE id = ?",
                                    (new_market, addr_input.text.strip(), phone_input.text.strip(), 
                                     contact_input.text.strip(), wechat_input.text.strip(), 
                                     alipay_input.text.strip(), bank_input.text.strip(), sid)
                                )
                                self.show_message('成功', f'销售客户 {sname} 修改成功！')
                                modify_popup.dismiss()
                                popup.dismiss()
                                self.load_seller_list()
                                self.show_modify_seller(None)
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
                
                modify_btn.bind(on_press=create_modify_handler(
                    seller['id'], seller['market'], seller['seller'],
                    seller['address'], seller['phone'], seller['contact_person'],
                    seller['wechat'], seller['alipay_account'], seller['bank_account']
                ))
                
                seller_row.add_widget(info_label)
                seller_row.add_widget(modify_btn)
                seller_grid.add_widget(seller_row)
        
        scroll.add_widget(seller_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_delete_seller(self, instance):
        """显示删除销售客户界面"""
        popup = Popup(title='删除销售客户', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 销售客户列表
        scroll = ScrollView(size_hint=(1, 1))
        seller_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        seller_grid.bind(minimum_height=seller_grid.setter('height'))
        
        # 获取所有销售客户
        cursor = self.db.execute_query("SELECT * FROM sellers ORDER BY id")
        sellers = cursor.fetchall()
        
        if not sellers:
            empty_label = Label(text='暂无销售客户数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            seller_grid.add_widget(empty_label)
        else:
            for seller in sellers:
                seller_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"市场: {seller['market']} | 销售客户: {seller['seller']} | 联系人: {seller['contact_person']} | 电话: {seller['phone']}",
                    font_name='chinese',
                    size_hint_x=0.7
                )
                
                delete_btn = Button(text='删除', font_name='chinese', size_hint_x=0.3)
                
                # ... existing code ...

                def create_delete_handler(uid, uname):
                    def handler(instance):
                        # 先检查是否有入库记录引用该销售客户
                        cursor = self.db.execute_query(
                            "SELECT COUNT(*) as count FROM stock_in_orders WHERE seller = ?",
                            (uname,)
                        )
                        result = cursor.fetchone()
                        
                        if result['count'] > 0:
                            self.show_message('错误', f'无法删除销售客户 "{uname}"！\n\n该销售客户有 {result["count"]} 条入库记录，请先删除相关入库记录后再删除销售客户。')
                            return
                        
                        # 没有引用，可以删除
                        confirm_popup = Popup(
                            title='确认删除',
                            size_hint=(0.4, 0.3)
                        )
                        confirm_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
                        
                        msg_label = Label(
                            text=f'确定要删除销售客户 "{uname}" 吗？\n此操作不可恢复！',
                            font_name='chinese',
                            halign='center'
                        )
                        
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        confirm_btn = Button(text='确认', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_delete(instance):
                            try:
                                self.db.execute_update("DELETE FROM sellers WHERE id = ?", (uid,))
                                self.show_message('成功', f'销售客户 {uname} 已删除！')
                                confirm_popup.dismiss()
                                popup.dismiss()
                                self.load_seller_list()
                                self.show_delete_seller(None)
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

# ... existing code ...
                
                delete_btn.bind(on_press=create_delete_handler(seller['id'], seller['seller']))
                
                seller_row.add_widget(info_label)
                seller_row.add_widget(delete_btn)
                seller_grid.add_widget(seller_row)
        
        scroll.add_widget(seller_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
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