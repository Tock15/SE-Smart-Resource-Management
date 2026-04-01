import reflex as rx

from .state import State
from frontend.pages.register import register_page
from frontend.pages.login import login_page
from frontend.pages.index import index
from frontend.pages.AllRoom import hotel_page
from frontend.pages.admin_requests import admin_dashboard
from frontend.pages.admin_resource import admin_resource


app = rx.App()
app.add_page(index, route="/")
app.add_page(register_page,route="/register")
app.add_page(login_page,route="/login")
app.add_page(hotel_page,route="/resource/rooms")
app.add_page(admin_dashboard,route="/admin/requests")
app.add_page(admin_resource,route="/admin/resources")
