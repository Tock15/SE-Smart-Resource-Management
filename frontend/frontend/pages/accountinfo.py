import reflex as rx

from rxconfig import config

import requests
from .sidebar import SidebarState, sidebar
class MyState(rx.State):
    data: list[dict] = []
    search_query: str = ""
    token: str = ""  # ← store token after login
    
    # profile fields
    student_id: str = ""
    full_name: str = ""
    email: str = ""

    def get_data(self):
        res = requests.get(
            "http://127.0.0.1:8000/auth/profile",
            headers={"Authorization": f"Bearer {self.token}"}  # ← send token
        )
        if res.status_code == 200:
            profile = res.json()
            self.student_id = profile["student_id"]
            self.full_name = profile["username"]
            self.email = profile["email"]
            
            
def navbar() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.flex(
            rx.image(
                src="whitesidebar.png",
                width="28px",
                height="28px",
                cursor="pointer",
                on_click=SidebarState.open_sidebar,   # connect button here
            ),
            rx.text(
                "SERSM",
                color="white",
                font_weight="bold",
                font_size="1.5em",
            ),
            align="center",
            spacing="4",
        ),
        bg="#1E88E5",
        height="60px",
        width="100%",
        display="flex",
        align_items="center",
        padding="0 30px",
        position="sticky",
        top="0",
        z_index="100",
    )
def account_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
        rx.vstack(
            rx.heading("Account details", size="7", color="black", margin_bottom="20px"),

            rx.text("PROFILE DETAILS", font_size="12px", font_weight="bold", color="gray", letter_spacing="1px"),
            rx.divider(),

            profile_field("Student ID", "66011450"),   # ← added
            rx.divider(),
            
            profile_field("Full name", "Mila Meloni"),
            rx.divider(),

            profile_field("Email address", "milameloni@mail.com"),
            rx.divider(),

            profile_field("Password", "••••••••••"),
            rx.divider(),

            align="start",
            spacing="3",
            width="100%",
            max_width="500px",
        ),
        padding="40px 0 0 500px",
        bg="white",
        min_height="100vh",
    ),
        margin="0",
        padding="0"
    )


def profile_field(label: str, value: str) -> rx.Component:
    return rx.vstack(
        rx.text(label, font_size="13px", color="gray"),
        rx.hstack(
            rx.text(value, font_size="15px", color="black"),
            rx.spacer(),
            rx.icon("pencil", size=16, color="gray", cursor="pointer"),
            width="100%",
            align="center",
        ),
        align="start",
        spacing="1",
        width="100%",
        padding_y="8px",
    )
