import reflex as rx
from .sidebar import SidebarState, sidebar
import requests

class BookingState(rx.State):
    selected_time: str = ""
    selected_date: str = ""
    note: str = ""

    def select_time(self, time: str):
        self.selected_time = time

    def set_note(self, value: str):
        self.note = value

    def submit_booking(self):
        # call your API here
        pass

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

def time_slot(time: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(width="8px", height="8px", border_radius="50%", bg="#22c55e", flex_shrink="0"),
            rx.text(time, font_size="14px", color="black"),
            align="center",
            spacing="2",
        ),
        padding="12px 16px",
        border_radius="8px",
        border=rx.cond(
            time == BookingState.selected_time,
            "1.5px solid #1E88E5",
            "1.5px solid #e0e0e0",
        ),
        bg=rx.cond(time == BookingState.selected_time, "#EBF5FB", "white"),
        cursor="pointer",
        on_click=BookingState.select_time(time),
        width="100%",
        _hover={"border": "1.5px solid #1E88E5", "bg": "#EBF5FB"},
    )


def booking_page() -> rx.Component:
    time_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
        "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
    ]

    return rx.box(
        navbar(),
        rx.box(
            rx.hstack(

                # LEFT — Room info + note + confirm
                rx.vstack(
                    rx.heading("Book a Room", size="7", color="black"),
                    rx.text("Fill in the details to reserve your space.", color="gray", font_size="14px"),
                    rx.divider(),

                    # Room info card
                    rx.hstack(
                        rx.image(src="/pic/room1.jpg", width="80px", height="80px", object_fit="cover", border_radius="10px"),
                        rx.vstack(
                            rx.text("Innovation Hub", font_weight="bold", font_size="16px", color="black"),
                            rx.hstack(rx.icon("map-pin", size=14, color="#1E88E5"), rx.text("Room 402", font_size="13px", color="#1E88E5")),
                            rx.text("Open hours: 09:00 AM - 05:00 PM", font_size="13px", color="gray"),
                            align="start",
                            spacing="1",
                        ),
                        align="center",
                        spacing="4",
                        padding="16px",
                        border="1.5px solid #e0e0e0",
                        border_radius="12px",
                        width="100%",
                    ),

                    align="start",
                    spacing="5",
                    width="100%",
                    max_width="400px",
                ),

                # RIGHT — Date + Time slots
                rx.vstack(
                    # Date picker
                    rx.vstack(
                        rx.text("Select Date", font_size="13px", font_weight="bold", color="gray"),
                        rx.input(
                            type="date",
                            on_change=BookingState.set_note,
                            border="1.5px solid #e0e0e0",
                            border_radius="8px",
                            padding="10px",
                            width="100%",
                            _focus={"border": "1.5px solid #1E88E5", "outline": "none"},
                        ),
                        align="start",
                        width="100%",
                        spacing="2",
                        margin_top="20px",
                    ),

                    # Time slots
                    rx.vstack(
                        rx.text("Select Time", font_size="13px", font_weight="bold", color="gray"),
                        rx.grid(
                            *[time_slot(t) for t in time_slots],
                            columns="2",
                            spacing="2",
                            width="100%",
                        ),
                        align="start",
                        width="100%",
                        spacing="2",
                        
                    ),

                    align="start",
                    spacing="5",
                    width="100%",
                    max_width="350px",
                ),

                align="start",
                spacing="9",
                width="100%",
                justify="center",
            ),
            padding="40px",
            bg="white",
            min_height="100vh",
        ),
        margin="0",
        padding="0",
    )