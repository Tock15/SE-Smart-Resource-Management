import reflex as rx


def sidebar() -> rx.Component:
    pass

def index() -> rx.Component:
    shared_bg = "url('/room_home.jpg')"

    return rx.flex(
        rx.box(
            # Navbar
            rx.box(
                rx.flex(
                    rx.flex(
                        rx.image(
                            src="sidebar.png",
                            width="5%",
                            height="5%"
                        ),
                        rx.text(
                            "SERSM",
                            color="black",
                            font_weight="bold",
                            font_size="1.5em",
                        ),
                        align="center",
                        spacing="4"
                    ),
                    rx.flex(
                        rx.button("Login",
                            color="black",
                            background_color="rgba(255, 255, 255, 0)",
                            font_size="1em",
                        ),
                        rx.button("Signup",
                            color="white",
                            background_color="rgba(0, 0, 0, 1)",
                            font_size="1em",
                            padding="1.2em",
                            border_radius="20px"

                        ),
                        spacing="4",
                        align="center"
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                min_height="90px",
                padding="1.5em 2em",
            ),

            # Center text section
            rx.box(
                rx.flex(
                    rx.text.strong(
                        "Reserve Your Resource",
                        font_size="4em",
                        color="black",
                    ),
                    rx.text(
                        "with just four clicks",
                        font_size="2em",
                        color="black",
                    ),
                    direction="column",
                    align="center",
                    justify="center",
                    spacing="0",
                    height="40vh",
                    width="100%",
                ),
                display="flex",
                justify_content="center",
                align_items="center",
            ),
            background_image=shared_bg,
            background_size="cover",
            background_position="center",
            background_repeat="no-repeat",
            background_color="rgba(255, 255, 255, 0.7)",   # makes image more white
            background_blend_mode="lighten",
            width="calc(100% - 2em)",
            margin="1em",   # margin all directions
            border_radius="40px",
        ),

        # Cards section
        rx.box(
            rx.flex(
                rx.text(
                    "Select Category",
                    color="black",
                    font_weight="bold",
                    font_size="1.5em",
                ),
                rx.flex(
                    rx.card(
                        rx.flex(
                            rx.image(
                                src="coworking.png",
                                weight="40%",
                                height="40%"
                            ),
                            rx.text(
                                "Room",
                                font_weight="bold",
                                font_size="1.3em",
                                color="black",
                            ),
                            justify="center",
                            align="center",
                            width="100%",
                            height="100%",
                            direction="column",
                            spacing="4"
                        ),
                        height="25vh",
                        width="15vw",
                        border="1px solid black",
                    ),
                    rx.card(
                        rx.flex(
                            rx.image(
                                src="school-locker.png",
                                weight="40%",
                                height="40%"
                            ),
                            rx.text(
                                "Locker",
                                font_weight="bold",
                                font_size="1.3em",
                                color="black",
                            ),
                            justify="center",
                            align="center",
                            width="100%",
                            height="100%",
                            direction="column",
                            spacing="4"
                        ),
                        height="25vh",
                        width="15vw",
                        border="1px solid black",
                    ),
                    rx.card(
                        rx.flex(
                            rx.image(
                                src="tools.png",
                                weight="40%",
                                height="40%"
                            ),
                            rx.text(
                                "Lab Equipment",
                                font_weight="bold",
                                font_size="1.3em",
                                color="black",
                            ),
                            justify="center",
                            align="center",
                            width="100%",
                            height="100%",
                            direction="column",
                            spacing="4"
                        ),
                        height="25vh",
                        width="15vw",
                        border="1px solid black",
                    ),
                    spacing="9",
                    justify="center",
                    align="center",
                    width="100%",
                ),
                direction="column",
                spacing="5",   # space between title and cards
                align="center",
                width="100%",
            ),
            padding="2em",
            margin_bottom="5em",
        ),
        bg="white",
        min_height="100vh",
        direction="column",
        justify="between",
    )