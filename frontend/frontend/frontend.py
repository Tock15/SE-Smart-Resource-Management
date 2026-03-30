import reflex as rx

from .state import State
from frontend.pages.register import register
from frontend.pages.index import index

app = rx.App()
app.add_page(index, route="/")
app.add_page(register, route="register")