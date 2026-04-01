"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from .sidebar import SidebarState, sidebar
import requests

class MyState(rx.State):
    data: list[dict] = []
    search_query: str = ""

    def get_data(self):
        res = requests.get("http://127.0.0.1:8000/resources/lockers")
        if res.status_code == 200:
            self.data = res.json()
    def set_search(self, value: str):
        self.search_query = value
    @rx.var
    def filtered_data(self) -> list[dict]:
        if not self.search_query:
            return self.data
        return [
            item for item in self.data
            if self.search_query.lower() in item["name"].lower()
        ]
def navbar() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.grid(
            # Left - Logo
            rx.hstack(
                rx.flex(
                        rx.image(
                            src="/whitesidebar.png",
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
            ),

            rx.center(
                rx.hstack(
                    rx.icon("search", color="#90CAF9", size=15),
                    rx.input(
                        placeholder="Search...",
                        border="none",
                        outline="none",
                        background="transparent",
                        on_change=MyState.set_search,
                        color="#1E88E5",
                        font_size="14px",
                        width="100%",
                        _placeholder={"color": "#90CAF9"},
                        _focus={"outline": "none", "box_shadow": "none"},
                    ),
                    bg="white",
                    border_radius="20px",
                    padding="6px 16px",
                    align="center",
                    spacing="2",
                    width="100%",
                    max_width="400px",
                ),
                width="100%",
            ),

            # Right - Back button
            rx.hstack(
                rx.link(
                    rx.hstack(
                        rx.text("Back", color="white", font_weight="bold",
                            font_size="1.5em",),
                        rx.icon("arrow-right", color="white", font_weight="bold",
                            font_size="1.5em",),
                        align="center",
                        spacing="1",
                    ),
                    href="/",
                ),
                align="center",
                justify="end",
                height="100%",
            ),

            columns="3",          # ← equal 3-column grid
            width="100%",
            padding="0 30px",
            align="center",
            height="100%",
        ),
        bg="#1E88E5",
        height="90px",
        width="100%",
        position="sticky",
        top="0",
        z_index="100",
    )


def locker_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.foreach(MyState.filtered_data, locker_card),
            align="center",        # ← center the cards
            width="100%",
            spacing="4",
            padding="40px 20px",
        ),
        on_mount=MyState.get_data,
        bg="white",
        min_height="120vh",
    ),
    
def locker_card(item: dict) -> rx.Component:
    return rx.link(
        rx.flex(
            rx.box(
                rx.image(
                    src="/pic/room1.jpg",
                    width="100%",
                    height="200px",
                    object_fit="cover",
                    border_radius="8px 8px 0 0"
                ),
            ),

            rx.box(
                rx.vstack(
                    rx.heading(item["name"], size="7",color="black"),
                    rx.hstack(
                        rx.badge("Room ", item["type"], color_scheme="blue"),
                        rx.badge(item["locker_no"], color_scheme="cyan"),
                    ),
                    rx.text(
                        "i dont know what to put in since the ",
                        font_size="13px",
                        color="gray",
                        margin_top="10px"
                    ),
                    align="start",
                    spacing="2"
                ),
                flex="1",
                padding="15px",
            ),

            width="100%",
            align="stretch",
        ),
        border="2px solid #e0e0e0",
        border_radius="10px",
        overflow="hidden",
        bg="white",
        width="900px",
        max_width="900px",
        href=f"/resource/{item['resource_id']}",  # ← dynamic route per card
        text_decoration="none",
        box_shadow="0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)"
        
    )
    
