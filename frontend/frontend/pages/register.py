"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config


class RadioGroupState(rx.State):
    item: str = "No Selection"

    @rx.event
    def set_item(self, item: str):
        self.item = item
        
def register() -> rx.Component:
    return rx.center(
    rx.box(
        rx.flex(
            rx.box(
                rx.center(
                    rx.vstack(
                        rx.heading(
                            "Create an Account",
                            width="100%",
                            text_align="center",
                            margin_bottom="30px"
                        ),

                        rx.text("Username",margin_bottom="0px"),
                        rx.input(placeholder="Username", width="300px",bg="white",margin_bottom="10px"),

                        rx.text("Email"),
                        rx.input(placeholder="Email", width="300px",bg="white",margin_bottom="10px"),
                        
                        rx.text("Password"),
                        rx.input(placeholder="Password", width="300px",bg="white",margin_bottom="10px"),

                        rx.text("Confirm password"),
                        rx.input(placeholder="Confirm Password", width="300px",bg="white",margin_bottom="10px"),

                        rx.radio(
                            ["Student", "Teacher"], on_change=RadioGroupState.set_item, direction="row",margin_bottom="20px"
                        ),
                        
                        rx.button(
                            "Submit",
                            width="100%",
                            text_color="white"
                        ),
                        
                        
                        align="start",  
                        spacing="0"
                    ),
                    height="90%"
                ),
                flex="1",
                border="1px solid black"# equal width
            ),

            rx.box(
                rx.center(
                    rx.image(
                        #Put image
                    ),
                    height="100%"
                ),
                flex="1",
                border="1px solid black"# equal width
            ),

            spacing="3",   # space between boxes
            width="100%",
            height="100%"
        ),
        width="1000px",
        height="600px",
        padding="20px",
        border_radius="60px",
        bg="linear-gradient(to right, #4facfe, #00f2fe)"
    ),
    height="100vh",
    bg="gray"
)
