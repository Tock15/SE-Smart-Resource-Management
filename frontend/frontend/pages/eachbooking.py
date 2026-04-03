import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
from frontend.state import State
from datetime import date


class BookingState(rx.State):
    resource: dict = {}
    selected_times: list[str] = []
    selected_date: str = str(date.today())
    note: str = ""
    start_date: str = ""
    end_date: str = ""
    current_user_role: str = ""

    def set_start_date(self, value: str):
        self.start_date = value

    def set_end_date(self, value: str):
        self.end_date = value

    def toggle_time(self, time: str):
        if time in self.selected_times:
            self.selected_times = [t for t in self.selected_times if t != time]
        else:
            self.selected_times.append(time)

    async def set_selected_date(self, value: str):
        self.selected_date = value
        self.selected_times = []
        print(self.selected_date)
        await self.fetch_resource()

    async def submit_booking(self):
        main_state = await self.get_state(State)
        token_data = main_state.verify_token()

        resource_id = self.router.page.params.get("booking_id", "")
        user_id = int(token_data["message"]["id"])

        if self.resource["type"] == "coworking_space":
            if len(self.selected_times) == 0:
                return  # no time selected, do nothing

            sorted_times = sorted(self.selected_times)
            first_start = sorted_times[0].split(" - ")[0]   # e.g. "08:00"
            last_end = sorted_times[-1].split(" - ")[1]      # e.g. "10:00"
            start_time = f"{self.selected_date}T{first_start}:00"
            end_time = f"{self.selected_date}T{last_end}:00"

            if self.current_user_role == "teacher":
                # Teachers book directly — no invite step, they are the sole guest
                payload = {
                    "resource_id": int(resource_id),
                    "start_time": start_time,
                    "end_time": end_time,
                    "guests": [user_id],
                }
                res = requests.post(
                    "http://localhost:8000/bookings/",
                    json=payload,
                    headers={"Authorization": f"Bearer {main_state.token}"}
                )
                if res.status_code == 201:
                    self.selected_times = []
                    self.selected_date = str(date.today())
                    self.start_date = ""
                    self.end_date = ""
                    return rx.redirect("/")
                else:
                    print(res.json())
            else:
                # Students go through the invite flow
                main_state.set_booking_info(int(resource_id), start_time, end_time, self.resource["min_guests"])
                self.selected_times = []
                self.selected_date = str(date.today())
                self.start_date = ""
                self.end_date = ""
                return rx.redirect("/invite")
        else:
            if self.start_date and self.end_date:
                start_time = f"{self.start_date}T00:00:00"
                end_time = f"{self.end_date}T23:59:59"
            else:
                return

            payload = {
                "resource_id": int(resource_id),
                "start_time": start_time,
                "end_time": end_time,
                "guests": [user_id],
            }
            requests.post(
                "http://localhost:8000/bookings/",
                json=payload,
                headers={"Authorization": f"Bearer {main_state.token}"}
            )
            self.selected_times = []
            self.selected_date = date.today()
            self.start_date = ""
            self.end_date = ""
            return rx.redirect("/")

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
            "bookings": data.get("bookings", []),
        }

    @rx.var
    def is_teacher(self) -> bool:
        return self.current_user_role == "teacher"

    @rx.var
    def booked_slots(self) -> list[str]:
        """Returns all booked (non-cancelled) time slots."""
        booked = []
        bookings = self.resource.get("bookings", [])
        time_slots = [
            "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
            "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00",
            "16:00 - 17:00", "17:00 - 18:00",
        ]
        for slot in time_slots:
            slot_start, slot_end = slot.split(" - ")
            for booking in bookings:
                if booking.get("status") == "cancelled":
                    continue
                timeslot = booking.get("timeslot", {})
                start_time = timeslot.get("start_time", "")
                end_time = timeslot.get("end_time", "")
                if start_time and end_time:
                    booked_start = start_time[11:16]
                    booked_end = end_time[11:16]
                    if slot_start < booked_end and slot_end > booked_start:
                        booked.append(slot)
                        break
        return booked

    @rx.var
    def student_booked_slots(self) -> list[str]:
        """Returns time slots booked ONLY by students (no teacher overlap) — teacher-overridable."""
        time_slots = [
            "08:00 - 09:00", "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
            "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00",
            "16:00 - 17:00", "17:00 - 18:00",
        ]
        bookings = self.resource.get("bookings", [])
        result = []
        for slot in time_slots:
            slot_start, slot_end = slot.split(" - ")
            has_student = False
            has_teacher = False
            for booking in bookings:
                if booking.get("status") == "cancelled":
                    continue
                timeslot = booking.get("timeslot", {})
                start_time = timeslot.get("start_time", "")
                end_time = timeslot.get("end_time", "")
                if start_time and end_time:
                    booked_start = start_time[11:16]
                    booked_end = end_time[11:16]
                    if slot_start < booked_end and slot_end > booked_start:
                        role = booking.get("user_role", "")
                        if role == "student":
                            has_student = True
                        else:
                            has_teacher = True
            if has_student and not has_teacher:
                result.append(slot)
        return result

    @rx.var
    def override_slots(self) -> list[str]:
        """Slots selected by teacher that are overriding a student booking."""
        if not self.is_teacher:
            return []
        return [t for t in self.selected_times if t in self.student_booked_slots]

    @rx.var
    def times_are_continuous(self) -> bool:
        if len(self.selected_times) <= 1:
            return len(self.selected_times) == 1
        sorted_times = sorted(self.selected_times)
        for i in range(len(sorted_times) - 1):
            current_end = sorted_times[i].split(" - ")[1]
            next_start = sorted_times[i + 1].split(" - ")[0]
            if current_end != next_start:
                return False
        return True

    def datetime_format(self, date_list):
        return f"{date_list[2]}-{date_list[1]}-{date_list[0]}"

    async def fetch_resource(self):
        booking_id = self.router.page.params.get("booking_id", "")
        if not booking_id:
            return rx.redirect("/")

        if self.selected_date == "":
            self.selected_date = str(date.today())
        today = str(self.selected_date).split("-")
        formatted_date = self.datetime_format(today)
        print(formatted_date)

        dashboard_state = await self.get_state(State)
        res = requests.get(
            f"http://localhost:8000/resources/{booking_id}?date={formatted_date}",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            try:
                data = res.json()
                self.resource = self.data_to_resource(data)
            except ValueError:
                print("Response is not valid JSON")
        else:
            print("Request failed:", res.status_code)

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.user_check():
            token_data = dashboard_state.verify_token()
            self.current_user_role = token_data.get("message", {}).get("role", "")
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
    is_booked = BookingState.booked_slots.contains(time)
    is_student_booked = BookingState.student_booked_slots.contains(time)
    is_teacher = BookingState.is_teacher

    # A teacher can click this slot if it's only student-booked
    is_overridable = is_teacher & is_student_booked
    # A slot is hard-blocked when booked and NOT overridable
    is_blocked = is_booked & ~is_overridable

    return rx.box(
        rx.hstack(
            rx.icon(
                "clock",
                size=13,
                color=rx.cond(
                    is_blocked,
                    "#9e9e9e",
                    rx.cond(
                        is_overridable & ~is_selected,
                        "#E65100",   # orange icon for overridable
                        rx.cond(is_selected, "#1E88E5", "#9e9e9e"),
                    ),
                ),
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    time,
                    font_size="13px",
                    font_weight=rx.cond(is_selected, "600", "400"),
                    color=rx.cond(
                        is_blocked,
                        "#9e9e9e",
                        rx.cond(
                            is_overridable & ~is_selected,
                            "#E65100",
                            rx.cond(is_selected, "#1E88E5", "black"),
                        ),
                    ),
                ),
                # "Student booked — override available" label for teachers
                rx.cond(
                    is_overridable & ~is_selected,
                    rx.text(
                        "Override available",
                        font_size="10px",
                        color="#E65100",
                        font_weight="500",
                    ),
                    rx.cond(
                        is_overridable & is_selected,
                        rx.text(
                            "Overriding student",
                            font_size="10px",
                            color="#1E88E5",
                            font_weight="600",
                        ),
                        rx.fragment(),
                    ),
                ),
                spacing="0",
                align="start",
            ),
            align="center",
            spacing="2",
        ),
        padding="10px 14px",
        border_radius="8px",
        border=rx.cond(
            is_blocked,
            "1.5px solid #d6d6d6",
            rx.cond(
                is_overridable & ~is_selected,
                "1.5px solid #FFCCBC",   # soft orange border
                rx.cond(
                    is_selected,
                    "1.5px solid #1E88E5",
                    "1.5px solid #e0e0e0",
                ),
            ),
        ),
        bg=rx.cond(
            is_blocked,
            "#f2f2f2",
            rx.cond(
                is_overridable & ~is_selected,
                "#FFF3E0",               # soft orange bg
                rx.cond(is_selected, "#EBF5FB", "white"),
            ),
        ),
        cursor=rx.cond(is_blocked, "not-allowed", "pointer"),
        opacity=rx.cond(is_blocked, "0.65", "1"),
        on_click=rx.cond(
            is_blocked,
            rx.noop(),
            BookingState.toggle_time(time),
        ),
        width="100%",
        _hover=rx.cond(
            is_blocked,
            {},
            rx.cond(
                is_overridable & ~is_selected,
                {"border": "1.5px solid #E65100", "bg": "#FFE0B2"},
                {"border": "1.5px solid #1E88E5", "bg": "#EBF5FB"},
            ),
        ),
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

                        # Legend — shown only to teachers
                        rx.cond(
                            BookingState.is_teacher,
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("info", size=13, color="#1E88E5"),
                                        rx.text(
                                            "Teacher Override",
                                            font_size="12px",
                                            font_weight="700",
                                            color="#1E88E5",
                                        ),
                                        align="center",
                                        spacing="1",
                                    ),
                                    rx.text(
                                        "Orange slots are booked by students. As a teacher, you can select them to override.",
                                        font_size="12px",
                                        color="#555",
                                        line_height="1.5",
                                    ),
                                    align="start",
                                    spacing="1",
                                ),
                                bg="#E3F2FD",
                                border="1px solid #90CAF9",
                                border_radius="8px",
                                padding="12px 14px",
                                width="100%",
                            ),
                            rx.fragment(),
                        ),

                        align="start",
                        spacing="5",
                        width="100%",
                        max_width="400px",
                    ),

                    # Right column — date + times
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

                        # Time slot selector
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
                                rx.vstack(
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
                                    # Override warning — shown when teacher has override slots
                                    rx.cond(
                                        BookingState.is_teacher & BookingState.override_slots,
                                        rx.hstack(
                                            rx.icon("triangle-alert", size=13, color="#E65100"),
                                            rx.text(
                                                "Overriding student booking: ",
                                                font_size="12px",
                                                font_weight="600",
                                                color="#E65100",
                                            ),
                                            rx.text(
                                                BookingState.override_slots.join(", "),
                                                font_size="12px",
                                                color="#E65100",
                                            ),
                                            align="center",
                                            spacing="1",
                                            flex_wrap="wrap",
                                        ),
                                        rx.fragment(),
                                    ),
                                    align="start",
                                    spacing="2",
                                    width="100%",
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
                            is_disabled=~BookingState.times_are_continuous,
                            bg=rx.cond(
                                BookingState.times_are_continuous,
                                "#1E88E5",
                                "#90CAF9",
                            ),
                            color="white",
                            border_radius="8px",
                            padding="12px 0",
                            font_size="14px",
                            font_weight="600",
                            width="100%",
                            _hover=rx.cond(
                                BookingState.times_are_continuous,
                                {"bg": "#1565C0"},
                                {},
                            ),
                            cursor=rx.cond(
                                BookingState.times_are_continuous,
                                "pointer",
                                "not-allowed",
                            ),
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