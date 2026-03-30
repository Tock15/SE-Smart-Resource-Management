import reflex as rx

from .state import State
from frontend.pages.register import register

app = rx.App()
app.add_page(register)