"""
自定义Kivy组件
"""
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button


class ChineseSpinnerOption(Button):
    """支持中文的Spinner选项按钮"""
    def __init__(self, **kwargs):
        kwargs['font_name'] = 'chinese'
        super().__init__(**kwargs)


class ChineseSpinner(Spinner):
    """支持中文显示的Spinner"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.option_cls = ChineseSpinnerOption
