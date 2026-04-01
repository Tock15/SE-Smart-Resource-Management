import reflex as rx

from .state import State
from frontend.pages.register import register_page
from frontend.pages.login import login_page
from frontend.pages.index import index
from frontend.pages.AllRoom import hotel_page
from frontend.pages.admin_requests import admin_dashboard
from frontend.pages.AllLocker import locker_page
from frontend.pages.AllEq import eq_page
from frontend.pages.accountinfo import account_page
from frontend.pages.Bookinghistory import orders_page
from frontend.pages.eachbooking import booking_page
from frontend.pages.admin_resource import admin_resource
from frontend.pages.invite import invite_page


app = rx.App()
app.add_page(index, route="/")
app.add_page(register_page,route="/register")
app.add_page(login_page,route="/login")
app.add_page(hotel_page,route="/resource/rooms")
app.add_page(admin_dashboard,route="/admin/requests")
app.add_page(locker_page,route="/resource/locker")
app.add_page(eq_page,route="/resource/equipment")
app.add_page(account_page,route="/account")
app.add_page(orders_page,route="/history")
app.add_page(booking_page,route="/booking/[booking_id]")
app.add_page(admin_resource,route="/admin/resources")
app.add_page(invite_page,route="/invite")
