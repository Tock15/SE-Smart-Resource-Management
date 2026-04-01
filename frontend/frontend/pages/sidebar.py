import reflex as rx
from frontend.state import State

class SidebarState(rx.State):
    sidebar_opening: bool = False

    def close_sidebar(self):
        self.sidebar_opening = False

    def open_sidebar(self):
        self.sidebar_opening = True

    async def logout(self):
        home_state = await self.get_state(State)
        home_state.logout()
        self.close_sidebar()
        return rx.redirect("/")
def sidebar() -> rx.Component:

    return rx.box(
        # dark overlay
        rx.box(
            position="fixed",
            top="0",
            left="0",
            width="100vw",
            height="100vh",
            bg="rgba(0, 0, 0, 0.3)",
            display=rx.cond(SidebarState.sidebar_opening, "block", "none"),
            z_index="9",
            on_click=SidebarState.close_sidebar,
        ),
        # actual sidebar
        rx.box(
            rx.flex(
                rx.flex(
                    rx.text(
                        "SERSM",
                        font_weight="bold",
                        font_size="1.5em",
                        color="black",
                    ),
                    rx.button(
                        "✕",
                        on_click=SidebarState.close_sidebar,
                        background_color="transparent",
                        color="black",
                    ),
                    width="100%",
                    align="center",
                    justify="between",
                    margin_bottom="3em"

                ),
                rx.flex(
                    rx.image(
                        src="/sidebar_house-chimney.png",
                        width="10%",
                        height="10%"
                    ),
                    rx.text(
                        "Home",
                        color="black",
                        font_size="1.3em"
                    ),
                    width="100%",
                    spacing="3",
                    align="center",
                    cursor="pointer",
                    on_click=rx.redirect("/")
                ),
                rx.divider(),
                rx.flex(
                    rx.image(
                        src="/sidebar_user.png",
                        width="10%",
                        height="10%"
                    ),
                    rx.text(
                        "Account",
                        color="black",
                        font_size="1.3em"
                    ),
                    width="100%",
                    spacing="3",
                    align="center",
                    cursor="pointer",
                    on_click=rx.redirect("/account")
                ),
                rx.divider(),
                rx.cond(
                    State.role == "admin",
                    rx.flex(
                        rx.image(
                            src="/sidebar_square-plus.png",
                            width="10%",
                            height="10%"
                        ),
                        rx.text(
                            "Add resource",
                            color="black",
                            font_size="1.3em",
                        ),
                        width="100%",
                        spacing="3",
                        align="center",
                        cursor="pointer",
                        on_click=rx.redirect("/admin/resources")
                    ),
                    rx.flex(
                        rx.image(
                            src="/sidebar_book-alt.png",
                            width="10%",
                            height="10%"
                        ),
                        rx.text(
                            "Booking",
                            color="black",
                            font_size="1.3em",
                        ),
                        width="100%",
                        spacing="3",
                        align="center",
                        cursor="pointer",
                        on_click=rx.redirect("/booking")
                    )
                ),
                rx.cond(
                    State.role == "admin",
                    rx.divider()
                ),
                rx.cond(
                    State.role == "admin",
                    rx.flex(
                        rx.image(
                            src="/sidebar_search.png",
                            width="10%",
                            height="10%"
                        ),
                        rx.text(
                            "Requests",
                            color="black",
                            font_size="1.3em",
                        ),
                        width="100%",
                        spacing="3",
                        align="center",
                        cursor="pointer",
                        on_click=rx.redirect("/admin/requests")
                    ),
                ),
                rx.divider(),
                rx.flex(
                    rx.image(
                        src="/sidebar_leave.png",
                        width="10%",
                        height="10%"
                    ),
                    rx.text(
                        "Logout",
                        color="black",
                        font_size="1.3em",
                    ),
                    width="100%",
                    spacing="3",
                    align="center",
                    cursor="pointer",
                    on_click=SidebarState.logout
                ),
                direction="column",
                spacing="4",
                width="100%",
            ),
            position="fixed",
            top="0",
            left=rx.cond(SidebarState.sidebar_opening, "0", "-280px"),
            width="240px",
            height="100vh",
            bg="white",
            padding="1.5em",
            box_shadow="2px 0 10px rgba(0,0,0,0.15)",
            transition="left 0.3s ease",
            z_index="10",
        ),
    )