import reflex as rx
from .sidebar import SidebarState, sidebar
from frontend.state import State

class InviteState(rx.State):
    student_id_input: str = ""
    invited_list: list[dict] = []

    def set_student_id(self, value: str):
        self.student_id_input = value

    def add_invite(self):
        ids = [s["id"] for s in self.invited_list]
        if self.student_id_input and self.student_id_input not in ids:
            self.invited_list.append({"id": self.student_id_input, "status": "Pending"})
            self.student_id_input = ""

    def remove_invite(self, student_id: str):
        self.invited_list = [s for s in self.invited_list if s["id"] != student_id]

    def toggle_status(self, student_id: str):
        self.invited_list = [
            {**s, "status": "Accepted" if s["status"] == "Pending" else "Pending"}
            if s["id"] == student_id else s
            for s in self.invited_list
        ]

    async def authorization(self):
        invite_state = await self.get_state(State)
        print(invite_state.booking_info)
        if not invite_state.user_check():
            return rx.redirect("/login")


def navbar() -> rx.Component:
    return rx.box(
        sidebar(),
        rx.flex(
            rx.image(
                src="whitesidebar.png",
                width="28px",
                height="28px",
                cursor="pointer",
                on_click=SidebarState.open_sidebar,
            ),
            rx.text("SESRM", color="white", font_weight="bold", font_size="1.5em"),
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


def status_badge(student: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                width="7px",
                height="7px",
                border_radius="50%",
                bg=rx.cond(student["status"] == "Accepted", "#22c55e", "#f59e0b"),
            ),
            rx.text(
                student["status"],
                font_size="12px",
                font_weight="600",
            ),
            align="center",
            spacing="1",
        ),
        px="10px",
        py="4px",
        border_radius="20px",
        bg=rx.cond(student["status"] == "Accepted", "#e8f5e9", "#fff8e1"),
        border=rx.cond(
            student["status"] == "Accepted",
            "1px solid #bbf7d0",
            "1px solid #fde68a",
        ),
        color=rx.cond(student["status"] == "Accepted", "#22c55e", "#f59e0b"),
        cursor="pointer",
        on_click=InviteState.toggle_status(student["id"]),
    )


def invited_row(student: dict) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon("user", size=16, color="white"),
            bg="#1E88E5",
            border_radius="50%",
            width="38px",
            height="38px",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(student["id"], font_size="14px", color="#111", font_weight="600"),
            rx.text("Student", font_size="12px", color="#aaa"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        status_badge(student),
        rx.icon(
            "x",
            size=15,
            color="#ccc",
            cursor="pointer",
            on_click=InviteState.remove_invite(student["id"]),
            _hover={"color": "#ef4444"},
        ),
        width="100%",
        align="center",
        padding="12px 0",
        border_bottom="1px solid #f5f5f5",
        spacing="3",
    )

@rx.page(route="/invite", on_load=InviteState.authorization)
def invite_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.flex(
            rx.box(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.heading("Invite Friends", size="7", color="#111"),
                        rx.text(
                            "Invite your friends to join SESRM.",
                            color="#888",
                            font_size="14px",
                        ),
                        align="start",
                        spacing="1",
                    ),

                    rx.divider(),

                    # Input section
                    rx.vstack(
                        rx.text(
                            "INVITE BY STUDENT ID",
                            font_size="12px",
                            font_weight="700",
                            color="#aaa",
                            letter_spacing="0.08em",
                        ),
                        rx.hstack(
                            rx.input(
                                placeholder="Enter student ID (e.g. 66011450)...",
                                value=InviteState.student_id_input,
                                on_change=InviteState.set_student_id,
                                border="1.5px solid #e0e0e0",
                                border_radius="10px",
                                padding="11px 14px",
                                width="100%",
                                bg="#fafafa",
                                color="black",
                                font_size="14px",
                                _focus={"border": "1.5px solid #1E88E5", "outline": "none", "bg": "white"},
                                height="45px",
                            ),
                            rx.button(
                                "Send Invite",
                                on_click=InviteState.add_invite,
                                bg="#1E88E5",
                                color="white",
                                border_radius="10px",
                                padding="11px 22px",
                                font_size="14px",
                                font_weight="600",
                                _hover={"bg": "#1565C0"},
                                cursor="pointer",
                                white_space="nowrap",
                                height="45px",
                            ),
                            width="100%",
                            spacing="3",
                        ),
                        align="start",
                        spacing="2",
                        width="100%",
                    ),

                    rx.divider(),

                    # Invited list
                    rx.vstack(
                        rx.text(
                            "INVITED PEOPLE",
                            font_size="12px",
                            font_weight="700",
                            color="#aaa",
                            letter_spacing="0.08em",
                        ),
                        rx.cond(
                            InviteState.invited_list,
                            rx.vstack(
                                rx.foreach(InviteState.invited_list, invited_row),
                                width="100%",
                                spacing="0",
                            ),
                            rx.text(
                                "No one invited yet.",
                                font_size="13px",
                                color="#bbb",
                                text_align="center",
                                width="100%",
                                padding="16px 0",
                            ),
                        ),
                        align="start",
                        width="100%",
                        spacing="2",
                    ),

                    align="start",
                    spacing="5",
                    width="100%",
                ),
                bg="white",
                border_radius="20px",
                padding="40px",
                width="100%",
                max_width="560px",
                box_shadow="0 4px 32px rgba(30,136,229,0.10), 0 1px 4px rgba(0,0,0,0.06)",
            ),
            justify="center",
            align="start",
            padding="48px 24px",
            bg="#f0f4fa",
            min_height="calc(100vh - 60px)",
            width="100%",
        ),
        margin="0",
        padding="0",
    )