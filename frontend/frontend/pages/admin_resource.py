import reflex as rx
from frontend.state import State
from .sidebar import SidebarState, sidebar
import requests
from typing import TypedDict


class ResourceRow(TypedDict):
    resource_id: int
    name: str
    description: str
    type: str
    room_no: str
    capacity: str
    min_guests: str
    locker_no: str
    serial_no: str


class ResourceState(rx.State):
    dashboard_data: list[ResourceRow] = []
    type_filter: str = "all"
    current_page: int = 1
    rows_per_page: int = 10

    # Edit dialog state
    edit_open: bool = False
    edit_id: int = 0
    edit_name: str = ""
    edit_description: str = ""
    edit_type: str = ""
    edit_room_no: str = ""
    edit_capacity: str = ""
    edit_locker_no: str = ""
    edit_serial_no: str = ""
    edit_min_guests: str = ""

    # Add dialog state
    add_open: bool = False
    add_name: str = ""
    add_description: str = ""
    add_type: str = "coworking_space"
    add_room_no: str = ""
    add_capacity: str = ""
    add_locker_no: str = ""
    add_serial_no: str = ""
    add_min_guests: str = ""

    def dataJSON_to_list(self, data) -> list[ResourceRow]:
        result = []
        for item in data:
            result.append(ResourceRow(
                resource_id=item["resource_id"],
                name=item.get("name") or "",
                description=item.get("description") or "",
                type=item.get("type") or "",
                room_no=item.get("room_no") or "",
                capacity=str(item.get("capacity") or ""),
                locker_no=item.get("locker_no") or "",
                serial_no=item.get("serial_no") or "",
                min_guests=str(item.get("min_guests") or ""),
            ))
        return result

    async def fetch_resource(self):
        dashboard_state = await self.get_state(State)
        res = requests.get(
            "http://localhost:8000/resources",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            self.dashboard_data = self.dataJSON_to_list(res.json())
        else:
            return rx.redirect("/")

    async def authorization(self):
        dashboard_state = await self.get_state(State)
        if dashboard_state.admin_check():
            return await self.fetch_resource()
        else:
            return rx.redirect("/")

    def set_filter(self, value: str):
        self.type_filter = value
        self.current_page = 1

    @rx.var
    def filtered_data(self) -> list[ResourceRow]:
        if self.type_filter == "all":
            return self.dashboard_data
        return [r for r in self.dashboard_data if r["type"] == self.type_filter]

    @rx.var
    def total_pages(self) -> int:
        total = len(self.filtered_data)
        return max(1, (total + self.rows_per_page - 1) // self.rows_per_page)

    @rx.var
    def current_page_data(self) -> list[ResourceRow]:
        start = (self.current_page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        return self.filtered_data[start:end]

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    # ── Setters ───────────────────────────────────────────
    def set_add_open(self, value: bool):
        self.add_open = value

    def set_add_name(self, value: str):
        self.add_name = value

    def set_add_description(self, value: str):
        self.add_description = value

    def set_add_type(self, value: str):
        self.add_type = value

    def set_add_room_no(self, value: str):
        self.add_room_no = value

    def set_add_capacity(self, value: str):
        self.add_capacity = value

    def set_add_locker_no(self, value: str):
        self.add_locker_no = value

    def set_add_serial_no(self, value: str):
        self.add_serial_no = value

    def set_add_min_guests(self, value: str):
        self.add_min_guests = value

    def set_edit_open(self, value: bool):
        self.edit_open = value

    def set_edit_name(self, value: str):
        self.edit_name = value

    def set_edit_description(self, value: str):
        self.edit_description = value

    def set_edit_type(self, value: str):
        self.edit_type = value

    def set_edit_room_no(self, value: str):
        self.edit_room_no = value

    def set_edit_capacity(self, value: str):
        self.edit_capacity = value

    def set_edit_locker_no(self, value: str):
        self.edit_locker_no = value

    def set_edit_serial_no(self, value: str):
        self.edit_serial_no = value
    def set_edit_min_guests(self, value: str):
        self.edit_min_guests = value

    # ── Add resource ──────────────────────────────────────
    def open_add_dialog(self):
        self.add_name = ""
        self.add_description = ""
        self.add_type = "coworking_space"
        self.add_room_no = ""
        self.add_capacity = ""
        self.add_locker_no = ""
        self.add_serial_no = ""
        self.add_min_guests = ""
        self.add_open = True

    def close_add_dialog(self):
        self.add_open = False

    async def submit_add_resource(self):
        dashboard_state = await self.get_state(State)

        if self.add_type == "coworking_space":
            payload = {
                "name": self.add_name,
                "description": self.add_description,
                "type": self.add_type,
                "room_no": self.add_room_no,
                "capacity": int(self.add_capacity) if self.add_capacity else 0,
                "min_guests": int(self.add_min_guests) if self.add_min_guests else 0,
            }
        elif self.add_type == "locker":
            payload = {
                "name": self.add_name,
                "type": self.add_type,
                "locker_no": self.add_locker_no,
            }
        else:  # equipment
            payload = {
                "name": self.add_name,
                "description": self.add_description,
                "type": self.add_type,
                "serial_no": self.add_serial_no,
            }
        print(payload)
        res = requests.post(
            "http://localhost:8000/admin/resources",
            data=payload,
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        self.add_open = False
        print(res.json())
        if res.status_code in (200, 201):
            return await self.fetch_resource()

    # ── Edit resource ─────────────────────────────────────
    def open_edit_dialog(self, row: ResourceRow):
        self.edit_id = row["resource_id"]
        self.edit_name = row["name"] or ""
        self.edit_description = row["description"] or ""
        self.edit_type = row["type"] or ""
        self.edit_room_no = row["room_no"] or ""
        self.edit_capacity = row["capacity"] or ""
        self.edit_locker_no = row["locker_no"] or ""
        self.edit_serial_no = row["serial_no"] or ""
        self.edit_min_guests = row["min_guests"] or ""
        self.edit_open = True

    def close_edit_dialog(self):
        self.edit_open = False

    async def submit_edit_resource(self):
        dashboard_state = await self.get_state(State)

        if self.edit_type == "coworking_space":
            payload = {
                "name": self.edit_name,
                "description": self.edit_description,
                "type": self.edit_type,
                "room_no": self.edit_room_no,
                "capacity": int(self.edit_capacity) if self.edit_capacity else 0,
                "min_guests": int(self.add_min_guests) if self.add_min_guests else 0,
            }
        elif self.edit_type == "locker":
            payload = {
                "name": self.edit_name,
                "type": self.edit_type,
                "locker_no": self.edit_locker_no,
            }
        else:  # equipment
            payload = {
                "name": self.edit_name,
                "description": self.edit_description,
                "type": self.edit_type,
                "serial_no": self.edit_serial_no,
            }
        res = requests.put(
            f"http://localhost:8000/admin/resources/{self.edit_id}",
            json=payload,
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        self.edit_open = False
        if res.status_code == 200:
            return await self.fetch_resource()

    # ── Delete resource ───────────────────────────────────
    async def delete_resource(self, resource_id: int):
        dashboard_state = await self.get_state(State)
        res = requests.delete(
            f"http://localhost:8000/admin/resources/{resource_id}",
            headers={"Authorization": f"Bearer {dashboard_state.token}"}
        )
        if res.status_code == 200:
            return await self.fetch_resource()


# ── Helper components ──────────────────────────────────────────────────────────

def type_badge(resource_type: str) -> rx.Component:
    color = rx.match(
        resource_type,
        ("coworking_space", "blue"),
        ("locker", "orange"),
        ("equipment", "purple"),
        "gray",
    )
    return rx.badge(resource_type, color_scheme=color, variant="soft", radius="full")


def filter_button(label: str, value: str) -> rx.Component:
    is_active = ResourceState.type_filter == value
    return rx.button(
        label,
        size="2",
        variant=rx.cond(is_active, "solid", "outline"),
        color_scheme=rx.cond(is_active, "blue", "black"),
        on_click=ResourceState.set_filter(value),
        cursor="pointer",
    )


def add_form_fields() -> rx.Component:
    return rx.flex(
        rx.text("Name", color="white", font_weight="bold"),
        rx.input(
            value=ResourceState.add_name,
            on_change=ResourceState.set_add_name,
            placeholder="Resource name",
        ),

        rx.text("Type", color="white", font_weight="bold"),
        rx.select(
            ["coworking_space", "locker", "equipment"],
            value=ResourceState.add_type,
            on_change=ResourceState.set_add_type,
        ),

        # coworking_space fields
        rx.cond(
            ResourceState.add_type == "coworking_space",
            rx.flex(
                rx.text("Description", color="white", font_weight="bold"),
                rx.text_area(
                    value=ResourceState.add_description,
                    on_change=ResourceState.set_add_description,
                    placeholder="Description",
                ),
                rx.text("Room No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.add_room_no,
                    on_change=ResourceState.set_add_room_no,
                    placeholder="e.g. 101",
                ),
                rx.text("Capacity", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.add_capacity,
                    on_change=ResourceState.set_add_capacity,
                    placeholder="0",
                    type="number",
                ),
                rx.text("Min Guests", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.add_min_guests,
                    on_change=ResourceState.set_add_min_guests,
                    placeholder="0",
                    type="number",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        # locker fields
        rx.cond(
            ResourceState.add_type == "locker",
            rx.flex(
                rx.text("Locker No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.add_locker_no,
                    on_change=ResourceState.set_add_locker_no,
                    placeholder="e.g. L-05",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        # equipment fields
        rx.cond(
            ResourceState.add_type == "equipment",
            rx.flex(
                rx.text("Description", color="white", font_weight="bold"),
                rx.text_area(
                    value=ResourceState.add_description,
                    on_change=ResourceState.set_add_description,
                    placeholder="Description",
                ),
                rx.text("Serial No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.add_serial_no,
                    on_change=ResourceState.set_add_serial_no,
                    placeholder="e.g. SN-12345",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        direction="column",
        spacing="2",
        width="100%",
    )


def edit_form_fields() -> rx.Component:
    return rx.flex(
        rx.text("Name", color="white", font_weight="bold"),
        rx.input(
            value=ResourceState.edit_name,
            on_change=ResourceState.set_edit_name,
            placeholder="Resource name",
        ),

        rx.text("Type", color="white", font_weight="bold"),
        type_badge(ResourceState.edit_type),

        # coworking_space fields
        rx.cond(
            ResourceState.edit_type == "coworking_space",
            rx.flex(
                rx.text("Description", color="white", font_weight="bold"),
                rx.text_area(
                    value=ResourceState.edit_description,
                    on_change=ResourceState.set_edit_description,
                    placeholder="Description",
                ),
                rx.text("Room No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.edit_room_no,
                    on_change=ResourceState.set_edit_room_no,
                    placeholder="e.g. 101",
                ),
                rx.text("Capacity", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.edit_capacity,
                    on_change=ResourceState.set_edit_capacity,
                    placeholder="0",
                    type="number",
                ),
                rx.text("Min Guests", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.edit_min_guests,
                    on_change=ResourceState.set_edit_min_guests,
                    placeholder="0",
                    type="number",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        # locker fields
        rx.cond(
            ResourceState.edit_type == "locker",
            rx.flex(
                rx.text("Locker No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.edit_locker_no,
                    on_change=ResourceState.set_edit_locker_no,
                    placeholder="e.g. L-05",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        # equipment fields
        rx.cond(
            ResourceState.edit_type == "equipment",
            rx.flex(
                rx.text("Description", color="white", font_weight="bold"),
                rx.text_area(
                    value=ResourceState.edit_description,
                    on_change=ResourceState.set_edit_description,
                    placeholder="Description",
                ),
                rx.text("Serial No.", color="white", font_weight="bold"),
                rx.input(
                    value=ResourceState.edit_serial_no,
                    on_change=ResourceState.set_edit_serial_no,
                    placeholder="e.g. SN-12345",
                ),
                direction="column",
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),

        direction="column",
        spacing="2",
        width="100%",
    )


# ── Page ───────────────────────────────────────────────────────────────────────

@rx.page(route="/admin/resources", on_load=ResourceState.authorization)
def admin_resource() -> rx.Component:
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
                # Title row + Add button
                rx.flex(
                    rx.text("Resources", color="black", font_weight="bold", font_size="1.2em"),

                    # ── Add Resource Dialog ──────────────
                    rx.dialog.root(
                        rx.dialog.trigger(
                            rx.button(
                                rx.icon("plus", size=16),
                                "Add Resource",
                                color_scheme="blue",
                                size="2",
                                cursor="pointer",
                                on_click=ResourceState.open_add_dialog,
                            )
                        ),
                        rx.dialog.content(
                            rx.dialog.title("Add New Resource"),
                            add_form_fields(),
                            rx.flex(
                                rx.button(
                                    "Cancel",
                                    color_scheme="gray",
                                    on_click=ResourceState.close_add_dialog,
                                ),
                                rx.button(
                                    "Add",
                                    color_scheme="blue",
                                    on_click=ResourceState.submit_add_resource,
                                ),
                                justify="end",
                                spacing="2",
                                margin_top="16px",
                            ),
                            style={"color": "white", "backgroundColor": "#1a1a1a"},
                            max_width="480px",
                        ),
                        open=ResourceState.add_open,
                        on_open_change=ResourceState.set_add_open,
                    ),

                    justify="between",
                    align="center",
                    padding="1em",
                    width="100%",
                ),

                # Filter bar
                rx.flex(
                    filter_button("All", "all"),
                    filter_button("Coworking Space", "coworking_space"),
                    filter_button("Locker", "locker"),
                    filter_button("Equipment", "equipment"),
                    spacing="2",
                    wrap="wrap",
                    padding="0 1em 1em 1em",
                ),

                # Table
                rx.flex(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID", color="black"),
                                rx.table.column_header_cell("Name", color="black"),
                                rx.table.column_header_cell("Type", color="black"),
                                rx.table.column_header_cell("Details", color="black"),
                                rx.table.column_header_cell("Actions", color="black"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                ResourceState.current_page_data,
                                lambda row: rx.table.row(
                                    rx.table.row_header_cell(row["resource_id"], color="black"),
                                    rx.table.cell(row["name"], color="black"),
                                    rx.table.cell(type_badge(row["type"])),
                                    rx.table.cell(
                                        rx.cond(
                                            row["type"] == "coworking_space",
                                            rx.text(
                                                "Room: ", row["room_no"],
                                                " | Cap: ", row["capacity"],
                                                " | Min Guests: ", row["min_guests"],
                                                color="black"
                                            ),
                                            rx.cond(
                                                row["type"] == "locker",
                                                rx.text("Locker: ", row["locker_no"], color="black"),
                                                rx.text("S/N: ", row["serial_no"], color="black"),
                                            ),
                                        ),
                                    ),
                                    rx.table.cell(
                                        rx.flex(
                                            # ── Edit Dialog ─────────────────
                                            rx.dialog.root(
                                                rx.dialog.trigger(
                                                    rx.button(
                                                        rx.icon("pencil", size=14),
                                                        size="1",
                                                        variant="soft",
                                                        color_scheme="blue",
                                                        on_click=ResourceState.open_edit_dialog(row),
                                                    )
                                                ),
                                                rx.dialog.content(
                                                    rx.dialog.title("Edit Resource"),
                                                    edit_form_fields(),
                                                    rx.flex(
                                                        rx.button(
                                                            "Cancel",
                                                            color_scheme="gray",
                                                            on_click=ResourceState.close_edit_dialog,
                                                        ),
                                                        rx.button(
                                                            "Save",
                                                            color_scheme="blue",
                                                            on_click=ResourceState.submit_edit_resource,
                                                        ),
                                                        justify="end",
                                                        spacing="2",
                                                        margin_top="16px",
                                                    ),
                                                    style={"color": "white", "backgroundColor": "#1a1a1a"},
                                                    max_width="480px",
                                                ),
                                                open=ResourceState.edit_open,
                                                on_open_change=ResourceState.set_edit_open,
                                            ),
                                            # ── Delete Dialog ────────────────
                                            rx.alert_dialog.root(
                                                rx.alert_dialog.trigger(
                                                    rx.button(
                                                        rx.icon("trash-2", size=14),
                                                        size="1",
                                                        variant="soft",
                                                        color_scheme="red",
                                                    )
                                                ),
                                                rx.alert_dialog.content(
                                                    rx.alert_dialog.title("Delete Resource"),
                                                    rx.alert_dialog.description(
                                                        rx.text(
                                                            "Are you sure you want to delete ",
                                                            rx.text.strong(row["name"]),
                                                            "? This cannot be undone.",
                                                        )
                                                    ),
                                                    rx.flex(
                                                        rx.alert_dialog.cancel(
                                                            rx.button("Cancel", color_scheme="gray", variant="soft")
                                                        ),
                                                        rx.alert_dialog.action(
                                                            rx.button(
                                                                "Delete",
                                                                color_scheme="red",
                                                                on_click=ResourceState.delete_resource(row["resource_id"]),
                                                            )
                                                        ),
                                                        justify="end",
                                                        spacing="2",
                                                        margin_top="16px",
                                                    ),
                                                    max_width="400px",
                                                ),
                                            ),
                                            spacing="2",
                                            align="center",
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
                        on_click=ResourceState.prev_page,
                        disabled=ResourceState.current_page <= 1,
                        color="black",
                        size="2",
                    ),
                    rx.text(
                        "Page ",
                        rx.text.strong(ResourceState.current_page),
                        " of ",
                        rx.text.strong(ResourceState.total_pages),
                        color="gray",
                        font_size="0.9em",
                    ),
                    rx.icon_button(
                        rx.icon("chevron-right"),
                        on_click=ResourceState.next_page,
                        disabled=ResourceState.current_page >= ResourceState.total_pages,
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