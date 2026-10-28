"""
市场管理界面
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


class MarketManagementScreen(BoxLayout):
    """市场管理主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 顶部按钮区域
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='添加市场', font_name='chinese')
        add_btn.bind(on_press=self.show_add_market)
        top_bar.add_widget(add_btn)
        
        modify_btn = Button(text='修改市场', font_name='chinese')
        modify_btn.bind(on_press=self.show_modify_market)
        top_bar.add_widget(modify_btn)
        
        delete_btn = Button(text='删除市场', font_name='chinese')
        delete_btn.bind(on_press=self.show_delete_market)
        top_bar.add_widget(delete_btn)        
        
        self.add_widget(top_bar)
        
        # 市场列表显示区域
        self.load_market_list()
    
    def load_market_list(self):
        """加载市场列表"""
        # 清除旧的市场列表容器和滚动视图
        if hasattr(self, 'market_scroll'):
            self.remove_widget(self.market_scroll)
        
        # 创建滚动视图
        scroll = ScrollView(size_hint=(1, 1))
        self.market_scroll = scroll
        
        self.market_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.market_list_container.bind(minimum_height=self.market_list_container.setter('height'))
        
        # 获取所有市场
        cursor = self.db.execute_query("SELECT * FROM markets ORDER BY id")
        markets = cursor.fetchall()        
        
        if not markets:
            empty_label = Label(text='暂无市场数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.market_list_container.add_widget(empty_label)
        else:
            for market in markets:
                market_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                market_label = Label(text=f"市场名: {market['market']}", font_name='chinese', size_hint_x=0.3)
                description_label = Label(text=f"描述: {market['description']}", font_name='chinese', size_hint_x=0.7)
                                
                market_row.add_widget(market_label)
                market_row.add_widget(description_label)
                                                
                self.market_list_container.add_widget(market_row)
        
        scroll.add_widget(self.market_list_container)
        self.add_widget(scroll)
    
    def show_add_market(self, instance):
        """显示添加市场对话框"""
        popup = Popup(title='添加市场', size_hint=(0.6, 0.5), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 市场名输入
        market_layout = BoxLayout(size_hint_y=None, height=40)
        market_layout.add_widget(Label(text='市场名:', font_name='chinese', size_hint_x=None, width=80))
        market_input = TextInput(hint_text='请输入市场名', multiline=False, font_name='chinese')
        market_layout.add_widget(market_input)
        layout.add_widget(market_layout)
        
        # 市场描述输入
        description_layout = BoxLayout(size_hint_y=None, height=40)
        description_layout.add_widget(Label(text='描述:', font_name='chinese', size_hint_x=None, width=80))
        description_input = TextInput(hint_text='请输入描述', multiline=False, font_name='chinese')
        description_layout.add_widget(description_input)
        layout.add_widget(description_layout)
               
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        submit_btn = Button(text='提交', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def submit_add(instance):
            market_name = market_input.text.strip()
            market_description = description_input.text.strip()
            
            if not market_name:
                self.show_message('错误', '市场名不能为空！')
                return
            
            try:                               
                self.db.execute_update(
                    "INSERT INTO markets (market, description) VALUES (?, ?)",
                    (market_name, market_description)
                )
                self.show_message('成功', f'市场 {market_name} 添加成功！')
                popup.dismiss()
                self.load_market_list()
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    self.show_message('错误', f'市场名 {market_name} 已存在！')
                else:
                    self.show_message('错误', f'添加失败: {str(e)}')
        
        submit_btn.bind(on_press=submit_add)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_modify_market(self, instance):
        """显示修改市场界面"""
        popup = Popup(title='修改市场', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 市场列表
        scroll = ScrollView(size_hint=(1, 1))
        market_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        market_grid.bind(minimum_height=market_grid.setter('height'))
        
        # 获取所有市场
        cursor = self.db.execute_query("SELECT * FROM markets ORDER BY id")  
        markets = cursor.fetchall()
        
        if not markets:
            empty_label = Label(text='暂无市场数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            market_grid.add_widget(empty_label)
        else:
            for market in markets:
                market_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"ID: {market['id']} | 市场名: {market['market']} | 描述: {market['description']}",
                    font_name='chinese',
                    size_hint_x=0.7
                )
                
                modify_btn = Button(text='修改', font_name='chinese', size_hint_x=0.3)
                
                def create_modify_handler(mid, mname, mdesc):
                    def handler(instance):
                        # 打开修改对话框
                        modify_popup = Popup(title='修改市场', size_hint=(0.6, 0.5), auto_dismiss=False)
                        modify_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
                        
                        # 市场名输入（禁用修改）
                        name_layout = BoxLayout(size_hint_y=None, height=40)
                        name_layout.add_widget(Label(text='市场名:', font_name='chinese', size_hint_x=None, width=80))
                        name_input = TextInput(text=mname, multiline=False, font_name='chinese', disabled=True)
                        name_layout.add_widget(name_input)
                        modify_layout.add_widget(name_layout)
                        
                        # 描述输入
                        desc_layout = BoxLayout(size_hint_y=None, height=40)
                        desc_layout.add_widget(Label(text='描述:', font_name='chinese', size_hint_x=None, width=80))
                        desc_input = TextInput(text=mdesc, multiline=False, font_name='chinese')
                        desc_layout.add_widget(desc_input)
                        modify_layout.add_widget(desc_layout)
                        
                        # 按钮
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        save_btn = Button(text='保存', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_save(instance):
                            new_desc = desc_input.text.strip()
                            if not new_desc:
                                self.show_message('错误', '描述不能为空！')
                                return
                            
                            try:
                                self.db.execute_update(
                                    "UPDATE markets SET description = ? WHERE id = ?",
                                    (new_desc, mid)
                                )
                                self.show_message('成功', f'市场 {mname} 修改成功！')
                                modify_popup.dismiss()
                                popup.dismiss()
                                self.load_market_list()
                                self.show_modify_market(None)
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
                
                modify_btn.bind(on_press=create_modify_handler(market['id'], market['market'], market['description']))
                
                market_row.add_widget(info_label)
                market_row.add_widget(modify_btn)
                market_grid.add_widget(market_row)
        
        scroll.add_widget(market_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_delete_market(self, instance):
        """显示删除市场界面"""
        popup = Popup(title='删除市场', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 市场列表
        scroll = ScrollView(size_hint=(1, 1))
        market_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        market_grid.bind(minimum_height=market_grid.setter('height'))
        
        # 获取所有市场
        cursor = self.db.execute_query("SELECT * FROM markets ORDER BY id")  
        markets = cursor.fetchall()
        
        if not markets:
            empty_label = Label(text='暂无市场数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            market_grid.add_widget(empty_label)
        else:
            for market in markets:
                market_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"ID: {market['id']} | 市场名: {market['market']} | 描述: {market['description']}",
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
                            text=f'确定要删除市场 "{uname}" 吗？\n此操作不可恢复！',
                            font_name='chinese',
                            halign='center'
                        )
                        
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        confirm_btn = Button(text='确认', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_delete(instance):
                            try:
                                self.db.execute_update("DELETE FROM markets WHERE id = ?", (uid,))
                                self.show_message('成功', f'市场 {uname} 已删除！')
                                confirm_popup.dismiss()
                                popup.dismiss()
                                self.load_market_list()
                                self.show_delete_market(None)
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
                
                delete_btn.bind(on_press=create_delete_handler(market['id'], market['market']))
                
                market_row.add_widget(info_label)
                market_row.add_widget(delete_btn)
                market_grid.add_widget(market_row)
        
        scroll.add_widget(market_grid)
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