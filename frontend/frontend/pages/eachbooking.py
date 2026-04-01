import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
from frontend.state import State


class BookingState(rx.State):
    resource: dict = {}
    selected_time: str = ""
    selected_date: str = ""
    note: str = ""

    def select_time(self, time: str):
        self.selected_time = time

    def set_note(self, value: str):
        self.note = value

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
            print(self.resource)
        else:
            return rx.redirect("/")


    async def authorization(self):
        dashboard_state = await self.get_state(State)
        print(dashboard_state.user_check())
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


@rx.page(route="/booking/[booking_id]", on_load=BookingState.authorization)
def booking_page() -> rx.Component:
    time_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
        "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
    ]

    return rx.box(
        navbar(),
        rx.box(
            rx.cond(
                BookingState.resource["type"] == "coworking_space",
                rx.hstack(
                    rx.vstack(
                        rx.heading("Book a Room", size="7", color="black"),
                        rx.text("Fill in the details to reserve your space.", color="gray", font_size="14px"),
                        rx.divider(),
                        rx.hstack(
                            rx.image(
                                src="/pic/room1.jpg",
                                width="80px",
                                height="80px",
                                object_fit="cover",
                                border_radius="10px"
                            ),
                            rx.vstack(
                                rx.text(
                                    BookingState.resource["name"],
                                    font_weight="bold",
                                    font_size="16px",
                                    color="black"
                                ),
                                rx.hstack(
                                    rx.icon("map-pin", size=14, color="#1E88E5"),
                                    rx.text(
                                        BookingState.resource["room_no"],
                                        font_size="13px",
                                        color="#1E88E5"
                                    )
                                ),
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
                    rx.vstack(
                        rx.vstack(
                            rx.text("Select Date", font_size="13px", font_weight="bold", color="gray"),
                            rx.input(
                                type="date",
                                value=BookingState.selected_date,
                                on_change=BookingState.set_selected_date,
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
                rx.box(
                    rx.text("id: ", BookingState.resource["id"],
                            color="black"
                    ),
                    rx.text("name: ", BookingState.resource["name"],
                            color="black"
                    ),
                    rx.text("type: ", BookingState.resource["type"],
                            color="black"
                    )
                ),
            ),
            padding="40px",
            bg="white",
            min_height="100vh",
        ),
        margin="0",
        padding="0",
    )