import reflex as rx
from .sidebar import SidebarState, sidebar
import requests
from frontend.state import State


class Timeslot(rx.Base):
    start_time: str = ""
    end_time: str = ""


class Resource(rx.Base):
    name: str = ""
    type: str = ""
    room_no: str | None = None
    locker_no: str | None = None


class Booking(rx.Base):
    booking_id: int = 0
    resource: Resource = Resource()
    timeslot: Timeslot = Timeslot()
    status: str = ""
    display_time : str = ""


class MyState(rx.State):
    data: list[Booking] = []
    search_query: str = ""
    current_page: int = 1
    rows_per_page: int = 10

    async def get_data(self):
        dashboard_state = await self.get_state(State)
        res = requests.get(
            "http://127.0.0.1:8000/bookings/",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )

        if res.status_code == 200:
            raw = res.json()
            self.data = [
                Booking(
                    booking_id=item["booking_id"],
                    status=item["status"],
                    resource=Resource(**item["resource"]),
                    timeslot=Timeslot(**item["timeslot"]),
                    display_time=format_date_python(
                        item["timeslot"]["start_time"],
                        item["timeslot"]["end_time"]
                    ) if item["resource"]["type"] == "coworking_space" else format_date_only(
                        item["timeslot"]["start_time"],
                        item["timeslot"]["end_time"]
                    ),
                    room_no=item.get("room_no", ""),
                    locker_no=item.get("locker_no", ""),
                )
                for item in raw
            ]
    async def cancel(self, booking_id):
        booking_state = await self.get_state(State)
        res = requests.patch(
            f"http://127.0.0.1:8000/bookings/{booking_id}/cancel",
            headers={"Authorization": f"Bearer {booking_state.token}"}
        )

        if res.status_code == 200:
            try:
                return await self.get_data()
            except ValueError:
                print("Response is not valid JSON")
        else:
            data = res.json()
            if data["detail"]:
                return rx.toast.error(
                    data["detail"],
                    duration=4000
                )
            else:
                return rx.toast.error(
                    f"Request failed : {res.status_code}",
                    duration=4000
                )


    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    def go_to_page(self, page: int):
        self.current_page = page

    def set_search(self, value: str):
        self.search_query = value
        self.current_page = 1  # reset to page 1 on new search

    @rx.var
    def filtered_data(self) -> list[Booking]:
        if not self.search_query:
            return self.data
        return [
            item for item in self.data
            if self.search_query.lower() in item.resource.name.lower()
        ]

    @rx.var
    def total_pages(self) -> int:
        return max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)

    @rx.var
    def current_page_data(self) -> list[Booking]:
        start = (self.current_page - 1) * self.rows_per_page
        return self.filtered_data[start: start + self.rows_per_page]

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.user_check():
            await self.get_data()
        else:
            dashboard_state.set_error_msg("you need to login before accessing this page")
            return rx.redirect("/login")

def format_date_only(start: str, end : str) -> str:
    month_names = {
        "1": "January", "2": "February", "3": "March", "4": "April",
        "5": "May", "6": "June", "7": "July", "8": "August",
        "9": "September", "10": "October", "11": "November", "12": "December"
    }
    start_date = start.split("T")[0]
    end_date = end.split("T")[0]
    start_year, start_month, start_day = start_date.split("-")
    end_year, end_month, end_day = end_date.split("-")
    return f"{int(start_day)} {month_names[start_month.lstrip('0')]} {start_year} - {int(end_day)} {month_names[end_month.lstrip('0')]} {end_year}"
def format_date_python(start: str, end: str) -> str:
    month_names = {
        "1": "January", "2": "February", "3": "March", "4": "April",
        "5": "May", "6": "June", "7": "July", "8": "August",
        "9": "September", "10": "October", "11": "November", "12": "December"
    }

    def to_readable(date: str) -> str:
        year, month, day = date.split("-")
        return f"{int(day)} {month_names[month.lstrip('0')]} {year}"

    def trim_time(time: str) -> str:
        h, m, _ = time.split(":")
        return f"{h}:{m}"

    start_date, start_time = start.split("T")
    end_date, end_time = end.split("T")

    start_time = trim_time(start_time)
    end_time = trim_time(end_time)

    if start_date == end_date:
        return f"{to_readable(start_date)} ({start_time}–{end_time})"
    else:
        return f"{to_readable(start_date)} ({start_time}) – {to_readable(end_date)} ({end_time})"
    
def empty_table_placeholder():
    return rx.center(
        rx.flex(
            rx.icon(
                "circle-slash", 
                size=40, 
                color="gray", 
                opacity=0.5
            ),
            rx.text(
                "No bookings found. Please book something first", 
                color="gray", 
                font_weight="medium"
            ),
            spacing="4",
            padding_y="10",
            direction="column",
            align="center"
        ),
        width="100%",
    )

def booking_row(item: Booking) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.cond(
                item.resource.type == "coworking_space",
                rx.text(
                    item.resource.name + " (" + item.resource.room_no + ")",
                    color="black",
                ),
                rx.cond(
                    item["resource"]["type"] == "locker",
                    rx.text(
                        item.resource.name + " (" + item.resource.locker_no + ")",
                        color="black",
                    ),
                    rx.text(item.resource.name, color="black"),
                ),
            ),
        ),
        rx.table.cell(rx.text(item.resource.type, color="black"),
        ),
        rx.table.cell(rx.text(item.display_time, color="black")
        ),
        rx.table.cell(
            rx.cond(
                item.status == "pending",
                rx.badge(item.status, color_scheme="yellow", border_radius="20px"),
                rx.cond(
                    item.status == "approved",
                    rx.badge(item.status, color_scheme="green", border_radius="20px"),
                    rx.cond(
                        item.status == "rejected",
                        rx.badge(item.status, color_scheme="red", border_radius="20px"),
                        rx.cond(
                            item.status == "cancelled",
                            rx.badge(item.status, color_scheme="red", border_radius="20px"),
                            rx.badge(item.status, color_scheme="purple", border_radius="20px"),
                        ),
                    ),
                ),
            ),
        ),
        rx.table.cell(
            rx.button("Cancel", color_scheme="red", size="1"),
            on_click=lambda : MyState.cancel(item["booking_id"])
        ),
        border_bottom="1px solid #f0f0f0",
        color="black",
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
                        color="white",
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
                        rx.text(
                            "Back",
                            color="white",
                            font_weight="bold",
                            font_size="1.5em",
                        ),
                        rx.icon(
                            "arrow-right",
                            color="white",
                            font_weight="bold",
                            font_size="1.5em",
                        ),
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
        rx.toast.provider(),
        navbar(),
        rx.box(
            rx.vstack(
                rx.heading("Booking History", size="7", color="black"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Type"),
                            rx.table.column_header_cell("Time"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Action"),
                            color="black",
                            border_bottom="1px solid #f0f0f0",
                        ),
                        
                    ),
                    rx.table.body(
                        rx.foreach(
                            MyState.current_page_data,
                            booking_row,
                        )
                    ),
                    width="100%",
                    border="1px solid #e0e0e0",
                    border_radius="10px",
                    overflow="hidden",
                ),
                rx.cond(
                    MyState.filtered_data.length() == 0,
                    rx.center(
                        empty_table_placeholder(),
                        width="100%",
                        padding="40px",
                    ),
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.spacer(),
                    # Replace the old pagination hstack with this:
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("chevron-left"),
                            on_click=MyState.prev_page,
                            disabled=MyState.current_page <= 1,
                            variant="outline",
                            size="2",
                        ),
                        rx.text(
                            "Page ",
                            rx.text.strong(MyState.current_page),
                            " of ",
                            rx.text.strong(MyState.total_pages),
                            color="gray",
                            font_size="0.9em",
                        ),
                        rx.icon_button(
                            rx.icon("chevron-right"),
                            on_click=MyState.next_page,
                            disabled=MyState.current_page >= MyState.total_pages,
                            variant="outline",
                            size="2",
                        ),
                        spacing="3",
                        align="center",
                        justify="center",
                        width="100%",
                    ),
                    width="100%",
                    align="center",
                ),
                align="start",
                spacing="4",
                width="100%",
                max_width="900px",
                margin="auto",
            ),
            padding="40px",
            bg="white",
            width="100%",
            min_height="100vh",
        ),
        padding="0",
    )