import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
class MyState(rx.State):
    data: list[dict] = []
    search_query: str = ""

    def get_data(self):
        res = requests.get("http://127.0.0.1:8000/resources/coworking-spaces")
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
def orders_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.heading("Booking History", size="7", color="black"),

                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Booking ID"),
                            rx.table.column_header_cell("Resource"),
                            rx.table.column_header_cell("Date"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Actions"),
                            bg="#1E88E5",
                            color="white",
                        ),
                    ),
                    rx.table.body(
                        rx.table.row(
                            rx.table.cell(rx.text("#10001", color="#1E88E5", font_weight="500")),
                            rx.table.cell("Innovation Hub"),
                            rx.table.cell("Jan 02, 2025"),
                            rx.table.cell(rx.badge("● Completed", color_scheme="green", border_radius="20px")),
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("eye", size=16, color="gray", cursor="pointer"),
                                    rx.icon("trash-2", size=16, color="#e53e3e", cursor="pointer"),
                                    spacing="3",
                                )
                            ),
                            border_bottom="1px solid #f0f0f0",
                        ),
                        rx.table.row(
                            rx.table.cell(rx.text("#10002", color="#1E88E5", font_weight="500")),
                            rx.table.cell("Creative Corner"),
                            rx.table.cell("Feb 10, 2025"),
                            rx.table.cell(rx.badge("● On Hold", color_scheme="yellow", border_radius="20px")),
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("eye", size=16, color="gray", cursor="pointer"),
                                    rx.icon("trash-2", size=16, color="#e53e3e", cursor="pointer"),
                                    spacing="3",
                                )
                            ),
                            border_bottom="1px solid #f0f0f0",
                        ),
                        rx.table.row(
                            rx.table.cell(rx.text("#10003", color="#1E88E5", font_weight="500")),
                            rx.table.cell("West Wing Locker"),
                            rx.table.cell("Mar 05, 2025"),
                            rx.table.cell(rx.badge("● Cancelled", color_scheme="gray", border_radius="20px")),
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("eye", size=16, color="gray", cursor="pointer"),
                                    rx.icon("trash-2", size=16, color="#e53e3e", cursor="pointer"),
                                    spacing="3",
                                )
                            ),
                            border_bottom="1px solid #f0f0f0",
                        ),
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