"""
用户管理界面
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


class UserManagementScreen(BoxLayout):
    """用户管理主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 初始化数据库
        self.db = DatabaseManager("huamo.db")
        
        # 顶部按钮区域
        top_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        add_btn = Button(text='添加用户', font_name='chinese')
        add_btn.bind(on_press=self.show_add_user)
        top_bar.add_widget(add_btn)
        
        delete_btn = Button(text='删除用户', font_name='chinese')
        delete_btn.bind(on_press=self.show_delete_user)
        top_bar.add_widget(delete_btn)
        
        reset_btn = Button(text='重置密码', font_name='chinese')
        reset_btn.bind(on_press=self.show_reset_password)
        top_bar.add_widget(reset_btn)
        
        self.add_widget(top_bar)
        
        # 用户列表显示区域
        self.load_user_list()
    
    def load_user_list(self):
        """加载用户列表"""
        # 清除旧的用户列表
        if hasattr(self, 'user_list_container'):
            self.remove_widget(self.user_list_container)
        
        # 创建滚动视图
        scroll = ScrollView(size_hint=(1, 1))
        self.user_list_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.user_list_container.bind(minimum_height=self.user_list_container.setter('height'))
        
        # 获取所有用户
        cursor = self.db.execute_query("SELECT id, username, role, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            empty_label = Label(text='暂无用户数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            self.user_list_container.add_widget(empty_label)
        else:
            for user in users:
                user_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                username_label = Label(text=f"用户名: {user['username']}", font_name='chinese', size_hint_x=0.3)
                role_label = Label(text=f"角色: {user['role']}", font_name='chinese', size_hint_x=0.3)
                date_label = Label(text=f"创建时间: {user['created_at']}", font_name='chinese', size_hint_x=0.4)
                
                user_row.add_widget(username_label)
                user_row.add_widget(role_label)
                user_row.add_widget(date_label)
                
                self.user_list_container.add_widget(user_row)
        
        scroll.add_widget(self.user_list_container)
        self.add_widget(scroll)
    
    def show_add_user(self, instance):
        """显示添加用户对话框"""
        popup = Popup(title='添加用户', size_hint=(0.6, 0.7), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 用户名输入
        username_layout = BoxLayout(size_hint_y=None, height=40)
        username_layout.add_widget(Label(text='用户名:', font_name='chinese', size_hint_x=None, width=80))
        username_input = TextInput(hint_text='请输入用户名', multiline=False, font_name='chinese')
        username_layout.add_widget(username_input)
        layout.add_widget(username_layout)
        
        # 密码输入
        password_layout = BoxLayout(size_hint_y=None, height=40)
        password_layout.add_widget(Label(text='密码:', font_name='chinese', size_hint_x=None, width=80))
        password_input = TextInput(hint_text='请输入密码', password=True, multiline=False, font_name='chinese')
        password_layout.add_widget(password_input)
        layout.add_widget(password_layout)
        
        # 角色选择
        role_layout = BoxLayout(size_hint_y=None, height=40)
        role_layout.add_widget(Label(text='角色:', font_name='chinese', size_hint_x=None, width=80))
        role_spinner = Spinner(text='admin', values=('admin', 'operator'), size_hint_x=1, font_name='chinese')
        role_layout.add_widget(role_spinner)
        layout.add_widget(role_layout)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        submit_btn = Button(text='提交', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def submit_add(instance):
            username = username_input.text.strip()
            password = password_input.text.strip()
            role = role_spinner.text
            
            if not username or not password:
                self.show_message('错误', '用户名和密码不能为空！')
                return
            
            try:
                password_hash = self.db._hash_password(password)
                self.db.execute_update(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                self.show_message('成功', f'用户 {username} 添加成功！')
                popup.dismiss()
                self.load_user_list()
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    self.show_message('错误', f'用户名 {username} 已存在！')
                else:
                    self.show_message('错误', f'添加失败: {str(e)}')
        
        submit_btn.bind(on_press=submit_add)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        layout.add_widget(btn_layout)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_delete_user(self, instance):
        """显示删除用户界面"""
        popup = Popup(title='删除用户', size_hint=(0.8, 0.8), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 用户列表
        scroll = ScrollView(size_hint=(1, 1))
        user_grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        user_grid.bind(minimum_height=user_grid.setter('height'))
        
        # 获取所有用户
        cursor = self.db.execute_query("SELECT id, username, role FROM users ORDER BY id")
        users = cursor.fetchall()
        
        if not users:
            empty_label = Label(text='暂无用户数据', font_size=18, font_name='chinese', size_hint_y=None, height=40)
            user_grid.add_widget(empty_label)
        else:
            for user in users:
                user_row = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=[5, 0, 5, 0])
                
                info_label = Label(
                    text=f"ID: {user['id']} | 用户名: {user['username']} | 角色: {user['role']}",
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
                            text=f'确定要删除用户 "{uname}" 吗？\n此操作不可恢复！',
                            font_name='chinese',
                            halign='center'
                        )
                        
                        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
                        confirm_btn = Button(text='确认', font_name='chinese')
                        cancel_btn = Button(text='取消', font_name='chinese')
                        
                        def do_delete(instance):
                            try:
                                self.db.execute_update("DELETE FROM users WHERE id = ?", (uid,))
                                self.show_message('成功', f'用户 {uname} 已删除！')
                                confirm_popup.dismiss()
                                popup.dismiss()
                                self.load_user_list()
                                self.show_delete_user(None)
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
                
                delete_btn.bind(on_press=create_delete_handler(user['id'], user['username']))
                
                user_row.add_widget(info_label)
                user_row.add_widget(delete_btn)
                user_grid.add_widget(user_row)
        
        scroll.add_widget(user_grid)
        layout.add_widget(scroll)
        
        # 关闭按钮
        close_btn = Button(text='关闭', size_hint_y=None, height=40, font_name='chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        layout.add_widget(close_btn)
        
        popup.add_widget(layout)
        popup.open()
    
    def show_reset_password(self, instance):
        """显示重置密码对话框"""
        popup = Popup(title='重置密码', size_hint=(0.5, 0.6), auto_dismiss=False)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 用户名输入
        username_layout = BoxLayout(size_hint_y=None, height=40)
        username_layout.add_widget(Label(text='用户名:', font_name='chinese', size_hint_x=None, width=80))
        username_input = TextInput(hint_text='请输入用户名', multiline=False, font_name='chinese')
        username_layout.add_widget(username_input)
        layout.add_widget(username_layout)
        
        # 新密码输入
        new_pass_layout = BoxLayout(size_hint_y=None, height=40)
        new_pass_layout.add_widget(Label(text='新密码:', font_name='chinese', size_hint_x=None, width=80))
        new_pass_input = TextInput(hint_text='请输入新密码', password=True, multiline=False, font_name='chinese')
        new_pass_layout.add_widget(new_pass_input)
        layout.add_widget(new_pass_layout)
        
        # 确认密码输入
        confirm_pass_layout = BoxLayout(size_hint_y=None, height=40)
        confirm_pass_layout.add_widget(Label(text='确认密码:', font_name='chinese', size_hint_x=None, width=80))
        confirm_pass_input = TextInput(hint_text='请再次输入新密码', password=True, multiline=False, font_name='chinese')
        confirm_pass_layout.add_widget(confirm_pass_input)
        layout.add_widget(confirm_pass_layout)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        submit_btn = Button(text='提交', font_name='chinese')
        cancel_btn = Button(text='取消', font_name='chinese')
        
        def submit_reset(instance):
            username = username_input.text.strip()
            new_password = new_pass_input.text.strip()
            confirm_password = confirm_pass_input.text.strip()
            
            if not username or not new_password or not confirm_password:
                self.show_message('错误', '所有字段都不能为空！')
                return
            
            if new_password != confirm_password:
                self.show_message('错误', '两次输入的密码不一致，请重新输入！')
                new_pass_input.text = ''
                confirm_pass_input.text = ''
                return
            
            # 检查用户是否存在
            cursor = self.db.execute_query("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if not user:
                self.show_message('错误', f'用户 {username} 不存在！')
                return
            
            try:
                password_hash = self.db._hash_password(new_password)
                self.db.execute_update(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (password_hash, username)
                )
                self.show_message('成功', f'用户 {username} 的密码已重置！')
                popup.dismiss()
            except Exception as e:
                self.show_message('错误', f'重置失败: {str(e)}')
        
        submit_btn.bind(on_press=submit_reset)
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