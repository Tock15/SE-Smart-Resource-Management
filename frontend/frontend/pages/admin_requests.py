import reflex as rx
from frontend.state import State
from .sidebar import SidebarState, sidebar
import requests
from typing import TypedDict


class BookingRow(TypedDict):
    booking_id: int
    username: str
    resource_name: str
    time_range: str
    status: str
    student_id: str
    start_time: str
    end_time: str


STATUS_COLORS = {
    "pending": "yellow",
    "approved": "green",
    "rejected": "red",
    "cancelled": "gray",
    "overridden": "purple"
}


class RequestsDashboardState(rx.State):
    current_page: int = 1
    rows_per_page: int = 10
    status_filter: str = "all"

    dashboard_data: list[BookingRow] = []

    def dataJSON_to_list(self, data) -> list[BookingRow]:
        result = []
        for item in data:
            start = item["timeslot"]["start_time"].replace("T", " ")
            end = item["timeslot"]["end_time"].replace("T", " ")
            result.append(BookingRow(
                booking_id=item["booking_id"],
                username=item["user"]["username"],
                resource_name=item["resource"]["name"],
                time_range=f"{start} - {end}",
                status=item["status"],
                student_id=item["user"]["student_id"],
                start_time=start,
                end_time=end,
            ))
        return result

    async def fetch_bookings(self):
        dashboard_state = await self.get_state(State)
        res = requests.get(
            "http://localhost:8000/bookings",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            self.dashboard_data = self.dataJSON_to_list(res.json())
        elif res.status_code == 401:
            return rx.redirect("/")
        else:
            print(res.json())
            return rx.redirect("/")

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.admin_check():
            return await self.fetch_bookings()
        else:
            return rx.redirect("/")

    def set_filter(self, filter_value: str):
        self.status_filter = filter_value
        self.current_page = 1  # reset to page 1 on filter change

    @rx.var
    def filtered_data(self) -> list[BookingRow]:
        if self.status_filter == "all":
            return self.dashboard_data
        return [row for row in self.dashboard_data if row["status"] == self.status_filter]

    @rx.var
    def total_pages(self) -> int:
        total = len(self.filtered_data)
        return max(1, (total + self.rows_per_page - 1) // self.rows_per_page)

    @rx.var
    def current_page_data(self) -> list[BookingRow]:
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        return self.filtered_data[start:end]

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    async def admin_decline(self, booking_id: int):
        dashboard_state = await self.get_state(State)
        res = requests.put(
            f"http://localhost:8000/admin/bookings/{booking_id}/reject",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            return await self.fetch_bookings()
        elif res.status_code == 401:
            return rx.redirect("/")

    async def admin_approve(self, booking_id: int):
        dashboard_state = await self.get_state(State)
        res = requests.put(
            f"http://localhost:8000/admin/bookings/{booking_id}/approve",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            return await self.fetch_bookings()
        elif res.status_code == 401:
            return rx.redirect("/")


def status_badge(status: str) -> rx.Component:
    # Map status string to a Radix color scheme
    color = rx.match(
        status,
        ("pending", "yellow"),
        ("approved", "green"),
        ("rejected", "red"),
        ("cancelled", "gray"),
        ("overridden", "purple"),
        "blue",  # default
    )
    return rx.badge(status, color_scheme=color, variant="solid", radius="full", high_contrast=True)


def filter_button(label: str, value: str) -> rx.Component:
    is_active = RequestsDashboardState.status_filter == value
    return rx.button(
        label,
        size="2",
        variant=rx.cond(is_active, "solid", "outline"),
        color_scheme=rx.cond(is_active, "blue", "black"),
        on_click=RequestsDashboardState.set_filter(value),
        cursor="pointer",
        # bg=rx.cond(is_active, "white", "transparent")
    )


def booking_view_dialog(row: BookingRow):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "View",
                size="1",
                border="1px solid black",
                bg="white",
                color="black",
            )
        ),
        rx.dialog.content(
            rx.dialog.title(
                rx.text("Booking #", row["booking_id"])
            ),
            rx.flex(
                status_badge(row["status"]),
                rx.text("User: ", row["username"]),
                rx.text("Student ID: ", row["student_id"]),
                rx.text("Resource: ", row["resource_name"]),
                rx.text("Start Time: ", row["start_time"]),
                rx.text("End Time: ", row["end_time"]),
                direction="column",
                spacing="2",
                margin_top="12px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Close", color_scheme="gray")
                ),
                justify="end",
                margin_top="16px",
            ),
            max_width="500px",
        ),
    )


@rx.page(route="/admin/requests", on_load=RequestsDashboardState.authorization)
def admin_dashboard() -> rx.Component:
    return rx.flex(
        sidebar(),
        rx.flex(
            # NavBar
            rx.flex(
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
                    spacing="6",
                    margin_left="10px"
                ),
                bg="#1E88E5",
                justify="start",
                align="center",
                width="100%",
                padding="1em",
            ),
            rx.flex(
                # Title + Filter bar
                rx.flex(
                    rx.text("Requests", color="black", font_weight="bold", font_size="1.2em"),
                    rx.flex(
                        filter_button("All", "all"),
                        filter_button("Pending", "pending"),
                        filter_button("Approved", "approved"),
                        filter_button("Rejected", "rejected"),
                        filter_button("Cancelled", "cancelled"),
                        filter_button("Overridden", "overridden"),
                        spacing="2",
                        wrap="wrap",
                    ),
                    justify="between",
                    align="center",
                    padding="1em",
                    width="99%",
                    padding_left="30px",
                ),
                # Table
                rx.flex(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID", color="black"),
                                rx.table.column_header_cell("Requester", color="black"),
                                rx.table.column_header_cell("Resource", color="black"),
                                rx.table.column_header_cell("Date", color="black"),
                                rx.table.column_header_cell("Status", color="black"),
                                rx.table.column_header_cell("Actions", color="black"),
                            ),
                            border_bottom="1px solid #e5e7eb",
                        ),
                        rx.table.body(
                            rx.foreach(
                                RequestsDashboardState.current_page_data,
                                lambda row: rx.table.row(
                                    rx.table.row_header_cell(row["booking_id"], color="black"),
                                    rx.table.cell(row["username"], color="black"),
                                    rx.table.cell(row["resource_name"], color="black"),
                                    rx.table.cell(row["time_range"], color="black"),
                                    rx.table.cell(
                                        status_badge(row["status"])
                                    ),
                                    rx.table.cell(
                                        rx.flex(
                                            booking_view_dialog(row),
                                            rx.button(
                                                "Decline",
                                                size="1",
                                                color_scheme=rx.cond(row["status"] == "pending", "red", "gray"),
                                                disabled=row["status"] != "pending",
                                                background_color=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "#f3f3f3"
                                                ),
                                                color=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "#888888"
                                                ),
                                                border=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "1px solid #d9d9d9"
                                                ),
                                                opacity="1",
                                                cursor=rx.cond(
                                                    row["status"] == "pending",
                                                    "pointer",
                                                    "not-allowed"
                                                ),
                                                on_click=lambda: RequestsDashboardState.admin_decline(row["booking_id"]),
                                            ),
                                            rx.button(
                                                "Approve",
                                                size="1",
                                                color_scheme=rx.cond(row["status"] == "pending", "grass", "gray"),
                                                disabled=row["status"] != "pending",
                                                background_color=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "#f3f3f3"
                                                ),
                                                color=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "#888888"
                                                ),
                                                border=rx.cond(
                                                    row["status"] == "pending",
                                                    "",
                                                    "1px solid #d9d9d9"
                                                ),
                                                opacity="1",
                                                cursor=rx.cond(
                                                    row["status"] == "pending",
                                                    "pointer",
                                                    "not-allowed"
                                                ),
                                                on_click=lambda: RequestsDashboardState.admin_approve(row["booking_id"]),
                                            ),
                                            align="center",
                                            spacing="1",
                                        )
                                    ),
                                    border_bottom="1px solid #e5e7eb",
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                    padding="0 1em",
                    overflow_x="auto",
                    bg="white",
                    margin_left="20px",
                    margin_right="20px",
                    border_radius="10px"
                ),
                # Pagination
                rx.flex(
                    rx.icon_button(
                        rx.icon("chevron-left"),
                        on_click=RequestsDashboardState.prev_page,
                        disabled=RequestsDashboardState.current_page <= 1,
                        color=rx.cond(
                            RequestsDashboardState.current_page <= 1,
                            "black",
                            "white"
                        ),
                        color_scheme="gray",
                        variant="solid",
                        size="2",
                    ),
                    rx.text(
                        "Page ",
                        rx.text.strong(RequestsDashboardState.current_page),
                        " of ",
                        rx.text.strong(RequestsDashboardState.total_pages),
                        color="black",
                        font_size="0.9em",
                    ),
                    rx.icon_button(
                        rx.icon("chevron-right"),
                        on_click=RequestsDashboardState.next_page,
                        disabled=RequestsDashboardState.current_page >= RequestsDashboardState.total_pages,
                        color=rx.cond(
                            RequestsDashboardState.current_page >= RequestsDashboardState.total_pages,
                            "black",
                            "white"
                        ),
                        color_scheme="gray",
                        variant="solid",
                        size="2",
                    ),
                    align="center",
                    justify="center",
                    spacing="4",
                    padding="1.5em",
                ),
                direction="column",
                flex="1",
            ),
            bg="#E2E2E2",
            min_height="100vh",
            direction="column",
            justify="between",
            flex="1",
            width="100%",
        ),
        width="100%",
    )