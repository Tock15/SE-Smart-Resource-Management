import reflex as rx
from frontend.state import State
from .sidebar import SidebarState, sidebar
import requests


class RequestsDashboardState(rx.State):
    current_page: int = 1
    rows_per_page: int = 10

    dashboard_data : list[list] = [
        ["1", "test1", "HM803", "12-01-2026"],
        ["2", "test2", "Raspberry Pi", "4-04-2026"],
        ["3", "test3", "Locker 15", "20-02-2026"],
        ["4", "test1", "HM803", "12-01-2026"],
        ["5", "test2", "Raspberry Pi", "4-04-2026"],
        ["6", "test3", "Locker 15", "20-02-2026"],
        ["7", "test1", "HM803", "12-01-2026"],
        ["8", "test2", "Raspberry Pi", "4-04-2026"],
        ["9", "test3", "Locker 15", "20-02-2026"],
        ["10", "test1", "HM803", "12-01-2026"],
        ["11", "test1", "HM803", "12-01-2026"],
        ["12", "test2", "Raspberry Pi", "4-04-2026"],
        ["13", "test3", "Locker 15", "20-02-2026"],
        ["14", "test1", "HM803", "12-01-2026"],
        ["15", "test2", "Raspberry Pi", "4-04-2026"],
        ["16", "test3", "Locker 15", "20-02-2026"],
        ["17", "test1", "HM803", "12-01-2026"],
        ["18", "test2", "Raspberry Pi", "4-04-2026"],
        ["19", "test3", "Locker 15", "20-02-2026"],
        ["20", "test1", "HM803", "12-01-2026"],
    ] 

    def dataJSON_to_list(self, data):
        result = []

        for item in data:
            booking_id = item["booking_id"]
            username = item["user"]["username"]
            resource_name = item["resource"]["name"]

            start = item["timeslot"]["start_time"].replace("T", " ")
            end = item["timeslot"]["end_time"].replace("T", " ")

            time_range = f"{start} - {end}"

            result.append([booking_id, username, resource_name, time_range])
        return result

    async def fetch_bookings(self):
        dashboard_state = await self.get_state(State)

        res = requests.get(
            "http://localhost:8000/bookings",
            headers={
                "Authorization": f"Bearer {dashboard_state.token}"
            }
        )

        if res.status_code == 200:
            data = res.json()
            self.dashboard_data = self.dataJSON_to_list(data)
        elif res.status_code == 401:
            print("You are not authorized to access request dashboard")
            return rx.redirect("/")

    async def authorization(self):
        dashboard_state = await self.get_state(State)

        if dashboard_state.admin_check():
            return await self.fetch_bookings()
        else:
            return rx.redirect("/")

    @rx.var
    def total_pages(self) -> int:
        total = len(self.dashboard_data)
        return max(1, (total + self.rows_per_page - 1) // self.rows_per_page)

    @rx.var
    def current_page_data(self) -> list[list]:
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        return self.dashboard_data[start:end]

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    async def admin_decline(self, booking_id: int):
        dashboard_state = await self.get_state(State)

        res = requests.post(
            f"http://localhost:8000/admin/bookings/{booking_id}/reject",
            headers={
                "Authorization": f"Bearer {dashboard_state.token}"
            }
        )

        if res.status_code == 200:
            print(f"Booking {booking_id} rejected successfully")
            return await self.fetch_bookings()
        elif res.status_code == 401:
            print("Unauthorized")
            return rx.redirect("/")
        else:
            print(f"Reject failed: {res.status_code} - {res.text}")

    async def admin_approve(self, booking_id: int):
        dashboard_state = await self.get_state(State)

        res = requests.post(
            f"http://localhost:8000/admin/bookings/{booking_id}/approve",
            headers={
                "Authorization": f"Bearer {dashboard_state.token}"
            }
        )

        if res.status_code == 200:
            print(f"Booking {booking_id} approved successfully")
            return await self.fetch_bookings()
        elif res.status_code == 401:
            print("Unauthorized")
            return rx.redirect("/")
        else:
            print(f"Approve failed: {res.status_code} - {res.text}")


@rx.page(route="/admin/requests", on_load=RequestsDashboardState.authorization)
def admin_dashboard() -> rx.Component:
    return rx.flex(
        sidebar(),
        rx.flex(
            # NavBar
            rx.flex(
                rx.flex(
                    rx.image(
                        src="/sidebar.png",
                        width="28px",
                        height="28px",
                        cursor="pointer",
                        on_click=SidebarState.open_sidebar,
                    ),
                    rx.text(
                        "SERSM",
                        color="black",
                        font_weight="bold",
                        font_size="1.5em",
                    ),
                    align="center",
                    spacing="4",
                ),
                bg="aqua",
                justify="start",
                align="center",
                width="100%",
                padding="1em",
            ),
            rx.flex(
                # Section title
                rx.flex(
                    rx.text("Requests", color="black", font_weight="bold"),
                    padding="1em",
                ),
                # Table
                rx.flex(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    "ID",
                                    color="black"
                                ),
                                rx.table.column_header_cell(
                                    "Requester",
                                    color="black"
                                ),
                                rx.table.column_header_cell(
                                    "Resource",
                                    color="black"
                                ),
                                rx.table.column_header_cell(
                                    "Date",
                                    color="black"
                                ),
                                rx.table.column_header_cell(
                                    "Actions",
                                    color="black"
                                ),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                RequestsDashboardState.current_page_data,
                                lambda row: rx.table.row(
                                    rx.table.row_header_cell(
                                        row[0],
                                        color="black"
                                    ),
                                    rx.table.cell(
                                        row[1],
                                        color="black"
                                    ),
                                    rx.table.cell(
                                        row[2],
                                        color="black"
                                    ),
                                    rx.table.cell(
                                        row[3],
                                        color="black"
                                    ),
                                    rx.table.cell(
                                        rx.flex(
                                            rx.button(
                                                "View",
                                                size="1",
                                                border="1px solid black",
                                                bg="white",
                                                color="black"
                                            ),
                                            rx.button(
                                                "Decline",
                                                size="1",
                                                color_scheme="red",
                                                on_click=lambda: RequestsDashboardState.admin_decline(row[0]),
                                            ),
                                            rx.button(
                                                "Approve",
                                                size="1",
                                                color_scheme="grass",
                                                on_click=lambda: RequestsDashboardState.admin_approve(row[0]),
                                            ),
                                            align="center",
                                            spacing="1"

                                        )
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                    ),
                    padding="0 1em",
                    overflow_x="auto",
                ),
                # Pagination
                rx.flex(
                    rx.icon_button(
                        rx.icon("chevron-left"),
                        on_click=RequestsDashboardState.prev_page,
                        disabled=RequestsDashboardState.current_page <= 1,
                        color="black",
                        size="2",
                    ),
                    rx.text(
                        "Page ",
                        rx.text.strong(RequestsDashboardState.current_page),
                        " of ",
                        rx.text.strong(RequestsDashboardState.total_pages),
                        color="gray",
                        font_size="0.9em",
                    ),
                    rx.icon_button(
                        rx.icon("chevron-right"),
                        on_click=RequestsDashboardState.next_page,
                        disabled=RequestsDashboardState.current_page >= RequestsDashboardState.total_pages,
                        color="black",
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
            bg="white",
            min_height="100vh",
            direction="column",
            justify="between",
            flex="1",
            width="100%",
        ),
        width="100%",
    )