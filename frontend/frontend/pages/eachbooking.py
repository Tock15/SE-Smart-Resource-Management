import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
from frontend.state import State


class BookingState(rx.State):
    resource: dict = {}
    selected_times: list[str] = []
    selected_date: str = ""
    note: str = ""
    start_date: str = ""
    end_date: str = ""
    
    def set_start_date(self, value: str):
        self.start_date = value

    def set_end_date(self, value: str):
        self.end_date = value
    
    def toggle_time(self, time: str):
        if time in self.selected_times:
            self.selected_times = [t for t in self.selected_times if t != time]
        else:
            self.selected_times.append(time)

    def set_selected_date(self, value: str):
        self.selected_date = value

    def submit_booking(self):
        pass

    def data_to_resource(self, data):
        return {
            "id": data.get("resource_id", ""),
            "name": data.get("name", ""),
            "type": data.get("type", ""),
            "room_no": data.get("room_no", ""),
            "capacity": data.get("capacity", 0),
            "min_guests": data.get("min_guests", 0),
            "serial_no": data.get("serial_no", ""),
            "locker_no": data.get("locker_no", ""),
        }

    async def fetch_resource(self):
        booking_id = self.router.page.params.get("booking_id", "")
        if not booking_id:
            return rx.redirect("/")

        dashboard_state = await self.get_state(State)
        res = requests.get(
            f"http://localhost:8000/resources/{booking_id}",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            data = res.json()
            self.resource = self.data_to_resource(data)
        else:
            return rx.redirect("/")

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.user_check():
            return await self.fetch_resource()
        else:
            return rx.redirect("/login")


def navbar() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.flex(
            rx.image(
                src="/whitesidebar.png",
                width="28px",
                height="28px",
                cursor="pointer",
                on_click=SidebarState.open_sidebar,
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

def time_button(time: str) -> rx.Component:
    is_selected = BookingState.selected_times.contains(time)
    return rx.box(
        rx.hstack(
            rx.icon(
                "clock",
                size=13,
                color=rx.cond(is_selected, "#1E88E5", "#9e9e9e"),
                flex_shrink="0",
            ),
            rx.text(
                time,
                font_size="13px",
                font_weight=rx.cond(is_selected, "600", "400"),
                color=rx.cond(is_selected, "#1E88E5", "black"),
            ),
            align="center",
            spacing="2",
        ),
        padding="10px 14px",
        border_radius="8px",
        border=rx.cond(
            is_selected,
            "1.5px solid #1E88E5",
            "1.5px solid #e0e0e0",
        ),
        bg=rx.cond(is_selected, "#EBF5FB", "white"),
        cursor="pointer",
        on_click=BookingState.toggle_time(time),
        width="100%",
        _hover={"border": "1.5px solid #1E88E5", "bg": "#EBF5FB"},
    )


@rx.page(route="/booking/[booking_id]", on_load=BookingState.authorization)
def booking_page() -> rx.Component:
    time_slots = [
        "08:00 - 09:00",
        "09:00 - 10:00",
        "10:00 - 11:00",
        "11:00 - 12:00",
        "12:00 - 13:00",
        "13:00 - 14:00",
        "14:00 - 15:00",
        "15:00 - 16:00",
        "16:00 - 17:00",
        "17:00 - 18:00",
    ]

    return rx.box(
        navbar(),
        rx.box(
            rx.cond(
                BookingState.resource["type"] == "coworking_space",

                # ── Coworking space layout ──────────────────────────────────
                rx.hstack(
                    # Left column — room info
                    rx.vstack(
                        rx.heading("Book a Room", size="7", color="black"),
                        rx.text(
                            "Fill in the details to reserve your space.",
                            color="gray",
                            font_size="14px",
                        ),
                        rx.divider(),
                        rx.hstack(
                            rx.image(
                                src="/pic/room1.jpg",
                                width="80px",
                                height="80px",
                                object_fit="cover",
                                border_radius="10px",
                            ),
                            rx.vstack(
                                rx.text(
                                    BookingState.resource["name"],
                                    font_weight="bold",
                                    font_size="16px",
                                    color="black",
                                ),
                                rx.hstack(
                                    rx.icon("map-pin", size=14, color="#1E88E5"),
                                    rx.text(
                                        BookingState.resource["room_no"],
                                        font_size="13px",
                                        color="#1E88E5",
                                    ),
                                    align="center",
                                    spacing="1",
                                ),
                                rx.text(
                                    "Open hours: 08:00 AM - 06:00 PM",
                                    font_size="13px",
                                    color="gray",
                                ),
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

                    # Right column — date + days + times
                    rx.vstack(
                        # Date picker
                        rx.vstack(
                            rx.text(
                                "Select Date",
                                font_size="13px",
                                font_weight="bold",
                                color="gray",
                            ),
                            rx.input(
                                type="date",
                                value=BookingState.selected_date,
                                on_change=BookingState.set_selected_date,
                                border="1.5px solid #e0e0e0",
                                border_radius="8px",
                                padding="10px",
                                width="100%",
                                 bg="white",
                                color="black",
                                height="45px",
                                _focus={"border": "1.5px solid #1E88E5", "outline": "none"},
                            ),
                            align="start",
                            width="100%",
                            spacing="2",
                            margin_top="20px",
                        ),

                        # ── ime slot selector ──────────────────────────────
                        rx.vstack(
                            rx.text(
                                "Select Time Slots",
                                font_size="13px",
                                font_weight="bold",
                                color="gray",
                            ),
                            rx.grid(
                                *[time_button(slot) for slot in time_slots],
                                columns="2",
                                spacing="2",
                                width="100%",
                            ),
                            align="start",
                            width="100%",
                            spacing="2",
                        ),

                        # Selected times summary
                        rx.cond(
                            BookingState.selected_times,
                            rx.box(
                                rx.hstack(
                                    rx.icon("clock", size=14, color="#1E88E5"),
                                    rx.text(
                                        "Time slots: ",
                                        font_size="13px",
                                        font_weight="600",
                                        color="#1E88E5",
                                    ),
                                    rx.text(
                                        BookingState.selected_times.join(", "),
                                        font_size="13px",
                                        color="#555",
                                    ),
                                    align="center",
                                    spacing="1",
                                    flex_wrap="wrap",
                                ),
                                bg="#EBF5FB",
                                border="1px solid #b3d4f7",
                                border_radius="8px",
                                padding="10px 14px",
                                width="100%",
                            ),
                            rx.box(),
                        ),

                        # Confirm button
                        rx.button(
                            "Confirm Booking",
                            on_click=BookingState.submit_booking,
                            bg="#1E88E5",
                            color="white",
                            border_radius="8px",
                            padding="12px 0",
                            font_size="14px",
                            font_weight="600",
                            width="100%",
                            _hover={"bg": "#1565C0"},
                            cursor="pointer",
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

                # ── Fallback for other resource types ───────────────────────
                rx.vstack(
            rx.heading("Book a Resource", size="7", color="black"),
            rx.text(
                "Fill in the details to reserve your resource.",
                color="gray",
                font_size="14px",
            ),
            rx.divider(),

            # Resource info card
            rx.hstack(
                rx.vstack(
                    rx.text(
                        BookingState.resource["name"],
                        font_weight="bold",
                        font_size="16px",
                        color="black",
                    ),
                    rx.text(
                        BookingState.resource["type"],
                        font_size="13px",
                        color="#1E88E5",
                    ),
                    align="start",
                    spacing="1",
                ),
                padding="16px",
                border="1.5px solid #e0e0e0",
                border_radius="12px",
                width="100%",
            ),

            # Date range picker
            rx.vstack(
                rx.text(
                    "Select Date Range",
                    font_size="13px",
                    font_weight="bold",
                    color="gray",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Start Date", font_size="12px", color="gray"),
                        rx.input(
                            type="date",
                            value=BookingState.start_date,
                            on_change=BookingState.set_start_date,
                            border="1.5px solid #e0e0e0",
                            border_radius="8px",
                            padding="10px",
                            width="100%",
                            height="45px",
                             bg="white",
                             color="black",
                            _focus={"border": "1.5px solid #1E88E5", "outline": "none"},
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                    rx.icon("arrow-right", size=16, color="#9e9e9e", margin_top="22px"),
                    rx.vstack(
                        rx.text("End Date", font_size="12px", color="gray"),
                        rx.input(
                            type="date",
                            value=BookingState.end_date,
                            on_change=BookingState.set_end_date,
                            border="1.5px solid #e0e0e0",
                            border_radius="8px",
                            padding="10px",
                            width="100%",
                            height="45px",
                            bg="white",
                            color="black",
                            _focus={"border": "1.5px solid #1E88E5", "outline": "none"},
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                    align="end",
                    spacing="3",
                    width="100%",
                ),
                align="start",
                width="100%",
                spacing="2",
            ),

                rx.cond(
                    BookingState.start_date & BookingState.end_date,
                    rx.box(
                        rx.hstack(
                            rx.icon("calendar", size=14, color="#1E88E5"),
                            rx.text(
                                "Booking period: ",
                                font_size="13px",
                                font_weight="600",
                                color="#1E88E5",
                            ),
                            rx.text(
                                BookingState.start_date + " → " + BookingState.end_date,
                                font_size="13px",
                                color="#555",
                            ),
                            align="center",
                            spacing="1",
                        ),
                        bg="#EBF5FB",
                        border="1px solid #b3d4f7",
                        border_radius="8px",
                        padding="10px 14px",
                        width="100%",
                    ),
                    rx.box(),
                ),

                # Confirm button
                rx.button(
                    "Confirm Booking",
                    on_click=BookingState.submit_booking,
                    bg="#1E88E5",
                    color="white",
                    border_radius="8px",
                    padding="12px 0",
                    font_size="14px",
                    font_weight="600",
                    width="100%",
                    max_width="400px",
                    _hover={"bg": "#1565C0"},
                    cursor="pointer",
                ),

                align="center",
                spacing="5",
                width="100%",
                max_width="500px",
                margin_left="500px",
            ),
            ),
            padding="40px",
            bg="white",
            min_height="100vh",
        ),
        margin="0",
        padding="0",
    )