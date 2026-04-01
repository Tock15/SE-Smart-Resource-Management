"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from .sidebar import SidebarState, sidebar
from rxconfig import config

import requests

class MyState(rx.State):
    data: list[dict] = []
    search_query: str = ""
    
    def get_data(self):
        res = requests.get("http://127.0.0.1:8000/resources/equipments")
        if res.status_code == 200:
            self.data = res.json()
        print(self.data)
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


def eq_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.foreach(MyState.data, eq_card),
            align="center",        # ← center the cards
            width="100%",
            spacing="4",
            padding="40px 20px",
        ),
        on_mount=MyState.get_data,
        bg="white",
        min_height="120vh",
    ),
    
def eq_card(item: dict) -> rx.Component:
    return rx.link(
        rx.flex(
            # Left - Images
            rx.box(
                rx.image(
                    src="/pic/room1.jpg",
                    width="100%",
                    height="200px",
                    object_fit="cover",
                    border_radius="8px 8px 0 0"
                ),
            ),

            # Middle - Info
            rx.box(
                rx.vstack(
                    rx.heading(item["name"], size="5",color="black",margin_top="40px"),
                    rx.hstack(
                        rx.icon("map-pin", size=14, color="#1E88E5"),
                        rx.text("Room", item["room_no"], font_size="13px", color="#1E88E5"),
                    ),
                    rx.text(
                        item["description"],
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

            # Right - Rating & Price
            rx.box(
                rx.vstack(
                    # Rating
                    rx.hstack(
                        rx.vstack(
                            rx.text("Capacity", font_size="17px", font_weight="bold",color="black"),
                            align="end",
                            spacing="0"
                        ),
                        rx.box(
                            rx.text(item["capacity"], color="white", font_weight="bold", font_size="18px"),
                            bg="#1E88E5",
                            padding="8px 12px",
                            border_radius="8px 8px 8px 0px",
                        ),
                        spacing="2",
                        align="center"
                    ),

                    align="end",
                    spacing="2",
                    height="100%",
                    justify="between"
                ),
                width="200px",
                flex_shrink="0",
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
        href=f"/booking/{item['resource_id']}",  # ← dynamic route per card
        text_decoration="none"

        
    )
    
