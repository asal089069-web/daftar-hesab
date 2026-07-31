# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
import arabic_reshaper
from bidi.algorithm import get_display

LabelBase.register(name="Vazir", fn_regular="Vazir.ttf")
Window.clearcolor = (0.06, 0.07, 0.09, 1)


def fa(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


class StyledLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "Vazir"


class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = "Vazir"
        self.background_color = (0.15, 0.16, 0.19, 1)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (1, 1, 1, 1)
        self.padding = [15, 15, 15, 15]
        self.multiline = False


class RoundButton(Button):
    def __init__(self, bg=(0.2, 0.5, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.font_name = "Vazir"
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        with self.canvas.before:
            Color(*bg)
            self.rect = RoundedRectangle(radius=[12], pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


def make_row(text, color):
    row = BoxLayout(size_hint_y=None, height=45)
    with row.canvas.before:
        Color(0.14, 0.15, 0.18, 1)
        row.rect = RoundedRectangle(radius=[8], pos=row.pos, size=row.size)
    row.bind(pos=lambda w, *a: setattr(w.rect, 'pos', w.pos))
    row.bind(size=lambda w, *a: setattr(w.rect, 'size', w.size))
    label = StyledLabel(text=text, color=color)
    row.add_widget(label)
    return row


class MoneyTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.balance = 0

        self.balance_label = StyledLabel(
            text=fa("موجودی: ۰"), font_size=30, size_hint_y=None,
            height=70, bold=True, color=(0.3, 1, 0.5, 1)
        )
        self.add_widget(self.balance_label)

        self.amount_input = StyledInput(hint_text=fa("مبلغ"), input_filter='float', size_hint_y=None, height=55, font_size=20)
        self.add_widget(self.amount_input)

        self.desc_input = StyledInput(hint_text=fa("توضیح (مثلاً خرید آرد)"), size_hint_y=None, height=55, font_size=20)
        self.add_widget(self.desc_input)

        buttons_layout = BoxLayout(size_hint_y=None, height=55, spacing=10)
        expense_btn = RoundButton(text=fa("ثبت هزینه"), bg=(0.9, 0.25, 0.3, 1), font_size=18)
        expense_btn.bind(on_press=self.add_expense)
        income_btn = RoundButton(text=fa("ثبت درآمد"), bg=(0.2, 0.75, 0.4, 1), font_size=18)
        income_btn.bind(on_press=self.add_income)
        buttons_layout.add_widget(expense_btn)
        buttons_layout.add_widget(income_btn)
        self.add_widget(buttons_layout)

        history_title = StyledLabel(text=fa("تراکنش‌های اخیر"), font_size=18, size_hint_y=None, height=35, color=(0.7, 0.7, 0.75, 1))
        self.add_widget(history_title)

        self.scroll = ScrollView()
        self.history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.scroll.add_widget(self.history_layout)
        self.add_widget(self.scroll)

    def add_expense(self, instance):
        self.process_transaction(-1)

    def add_income(self, instance):
        self.process_transaction(1)

    def process_transaction(self, sign):
        amount_text = self.amount_input.text
        desc = self.desc_input.text
        if amount_text == "":
            return

        amount = float(amount_text) * sign
        self.balance += amount
        self.balance_label.text = fa(f"موجودی: {self.balance:,.0f}")
        self.balance_label.color = (0.3, 1, 0.5, 1) if self.balance >= 0 else (1, 0.4, 0.4, 1)

        desc_text = desc if desc else "بدون توضیح"
        sign_text = "+" if amount > 0 else "-"
        record_text = fa(f"{desc_text}   |   {sign_text}{abs(amount):,.0f} تومان")
        color = (0.3, 1, 0.5, 1) if amount > 0 else (1, 0.4, 0.4, 1)
        self.history_layout.add_widget(make_row(record_text, color))

        self.amount_input.text = ""
        self.desc_input.text = ""


class InstallmentsTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        title = StyledLabel(text=fa("مدیریت قسط‌ها"), font_size=26, bold=True, size_hint_y=None, height=50, color=(0.4, 0.7, 1, 1))
        self.add_widget(title)

        self.amount_input = StyledInput(hint_text=fa("مبلغ قسط"), input_filter='float', size_hint_y=None, height=55, font_size=20)
        self.add_widget(self.amount_input)

        self.date_input = StyledInput(hint_text=fa("تاریخ سررسید (مثلاً ۱۴۰۴/۰۵/۱۵)"), size_hint_y=None, height=55, font_size=20)
        self.add_widget(self.date_input)

        add_btn = RoundButton(text=fa("افزودن قسط"), bg=(0.3, 0.5, 1, 1), size_hint_y=None, height=55, font_size=18)
        add_btn.bind(on_press=self.add_installment)
        self.add_widget(add_btn)

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.add_widget(self.scroll)

    def add_installment(self, instance):
        amount = self.amount_input.text
        date = self.date_input.text
        if amount == "" or date == "":
            return

        record_text = fa(f"مبلغ: {float(amount):,.0f} تومان   |   سررسید: {date}")
        self.list_layout.add_widget(make_row(record_text, (0.4, 0.7, 1, 1)))

        self.amount_input.text = ""
        self.date_input.text = ""


class BakeryTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=12, **kwargs)
        self.shop_totals = {}

        title = StyledLabel(text=fa("ثبت نان مغازه‌ها"), font_size=26, bold=True, size_hint_y=None, height=45, color=(1, 0.7, 0.2, 1))
        self.add_widget(title)

        self.shop_input = StyledInput(hint_text=fa("اسم مغازه"), size_hint_y=None, height=50, font_size=18)
        self.add_widget(self.shop_input)

        self.date_input = StyledInput(hint_text=fa("تاریخ (مثلاً ۱۴۰۴/۰۵/۱۵)"), size_hint_y=None, height=50, font_size=18)
        self.add_widget(self.date_input)

        row_inputs = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.qty_input = StyledInput(hint_text=fa("تعداد نان"), input_filter='float', font_size=18)
        self.price_input = StyledInput(hint_text=fa("قیمت واحد"), input_filter='float', font_size=18)
        row_inputs.add_widget(self.qty_input)
        row_inputs.add_widget(self.price_input)
        self.add_widget(row_inputs)

        add_btn = RoundButton(text=fa("ثبت"), bg=(1, 0.6, 0.1, 1), size_hint_y=None, height=50, font_size=18)
        add_btn.bind(on_press=self.add_entry)
        self.add_widget(add_btn)

        entries_title = StyledLabel(text=fa("موارد ثبت‌شده"), font_size=16, size_hint_y=None, height=30, color=(0.7, 0.7, 0.75, 1))
        self.add_widget(entries_title)

        self.entries_scroll = ScrollView(size_hint_y=0.4)
        self.entries_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6)
        self.entries_layout.bind(minimum_height=self.entries_layout.setter('height'))
        self.entries_scroll.add_widget(self.entries_layout)
        self.add_widget(self.entries_scroll)

        summary_title = StyledLabel(text=fa("جمع کل به تفکیک مغازه"), font_size=16, size_hint_y=None, height=30, color=(1, 0.7, 0.2, 1))
        self.add_widget(summary_title)

        self.summary_scroll = ScrollView(size_hint_y=0.4)
        self.summary_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6)
        self.summary_layout.bind(minimum_height=self.summary_layout.setter('height'))
        self.summary_scroll.add_widget(self.summary_layout)
        self.add_widget(self.summary_scroll)

    def add_entry(self, instance):
        shop = self.shop_input.text.strip()
        date = self.date_input.text.strip()
        qty_text = self.qty_input.text
        price_text = self.price_input.text

        if shop == "" or qty_text == "" or price_text == "":
            return

        qty = float(qty_text)
        price = float(price_text)
        total = qty * price

        entry_text = fa(f"{shop} | {date}   |   {qty:,.0f} عدد × {price:,.0f} = {total:,.0f} تومان")
        self.entries_layout.add_widget(make_row(entry_text, (1, 0.8, 0.4, 1)))

        if shop not in self.shop_totals:
            self.shop_totals[shop] = {"qty": 0, "total": 0}
        self.shop_totals[shop]["qty"] += qty
        self.shop_totals[shop]["total"] += total

        self.refresh_summary()

        self.shop_input.text = ""
        self.date_input.text = ""
        self.qty_input.text = ""
        self.price_input.text = ""

    def refresh_summary(self):
        self.summary_layout.clear_widgets()
        for shop, data in self.shop_totals.items():
            summary_text = fa(f"{shop}:   {data['qty']:,.0f} عدد   |   {data['total']:,.0f} تومان")
            self.summary_layout.add_widget(make_row(summary_text, (1, 0.7, 0.2, 1)))


class MainApp(App):
    def build(self):
        self.title = "دفتر حساب روزانه"
        panel = TabbedPanel(do_default_tab=False, tab_width=140)

        money_item = TabbedPanelItem(text=fa("صندوق"))
        money_item.add_widget(MoneyTab())
        panel.add_widget(money_item)

        bakery_item = TabbedPanelItem(text=fa("نانوایی"))
        bakery_item.add_widget(BakeryTab())
        panel.add_widget(bakery_item)

        installments_item = TabbedPanelItem(text=fa("قسط‌ها"))
        installments_item.add_widget(InstallmentsTab())
        panel.add_widget(installments_item)

        for tab in panel.tab_list:
            tab.font_name = "Vazir"
            tab.font_size = 16

        return panel


MainApp().run()