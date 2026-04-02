import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
from frontend.state import State


class MyState(rx.State):
    data: list[dict] = []
    search_query: str = ""

    async def get_data(self):
        dashboard_state = await self.get_state(State)
        res = requests.get("http://127.0.0.1:8000/bookings/",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
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

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.user_check():
            self.get_data()
            print(self.get_data)
        else:
            return rx.redirect("/login")


def booking_row(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(item.get("resource_id", ""),
            color="black"),
        rx.table.cell(item.get("name", ""),
            color="black"),
        rx.table.cell(item.get("room_no", ""),
            color="black"),
        rx.table.cell(
            rx.cond(
                item.get("status") == "pending",
                rx.badge(
                    item.get("type", ""),
                    color_scheme="yellow",
                    border_radius="20px",
                ),
            ),
            rx.cond(
                item.get("status") == "approved",
                rx.badge(
                    item.get("type", ""),
                    color_scheme="green",
                    border_radius="20px",
                ),
            ),
            rx.cond(
                item.get("status") == "rejected",
                rx.badge(
                    item.get("type", ""),
                    color_scheme="red",
                    border_radius="20px",
                ),
            ),
            rx.cond(
                item.get("status") == "cancelled",
                rx.badge(
                    item.get("type", ""),
                    color_scheme="red",
                    border_radius="20px",
                ),
            ),
            rx.cond(
                item.get("status") == "overriden",
                rx.badge(
                    item.get("type", ""),
                    color_scheme="purple",
                    border_radius="20px",
                ),
            ),
        ),
        rx.table.cell(
            rx.badge(
                item.get("type", ""),
                color_scheme="blue",
                border_radius="20px",
            )
        ),
        rx.table.cell(
            rx.text(
                f'{item.get("min_guests", 0)} - {item.get("capacity", 0)}',
            )
        ),
        border_bottom="1px solid #f0f0f0",
        color="black"
        )
def navbar() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.grid(
            rx.hstack(
                rx.flex(
                        rx.image(
                            src="/whitesidebar.png",
                            width="28px",
                            height="28px",
                            cursor="pointer",
                            on_click=SidebarState.open_sidebar,
                            color="white"# connect button here
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

            columns="3",         
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

@rx.page(route="/history", on_load=MyState.authorization)
def orders_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.heading("Booking History", size="7", color="black"),

                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Resource ID"),
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Room No"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Type"),
                            rx.table.column_header_cell("Guests"),
                            bg="#1E88E5",
                            color="white",
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            MyState.filtered_data,
                            booking_row,
                        )
                    ),
                    width="100%",
                    border="1px solid #e0e0e0",
                    border_radius="10px",
                    overflow="hidden",
                ),

                rx.hstack(
                    rx.text("Results: 1-3 per 3", font_size="13px", color="gray"),
                    rx.spacer(),
                    rx.hstack(
                        rx.button("‹", variant="outline", size="2"),
                        rx.button("1", bg="#1E88E5", color="white", size="2"),
                        rx.button("›", variant="outline", size="2"),
                        spacing="1",
                    ),
                    width="100%",
                    align="center",
                ),

                align="start",
                spacing="4",
                width="100%",
                max_width="900px",
            ),
            padding="40px 0 0 200px",
            bg="white",
            min_height="100vh",
        ),
        margin="0",
        padding="0",
    )