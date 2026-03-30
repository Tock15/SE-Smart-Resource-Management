import reflex as rx

from .state import State
from frontend.pages.register import register_page
from frontend.pages.login import login

app = rx.App()
app.add_page(register_page,route="/register")
app.add_page(login)