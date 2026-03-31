"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

import requests


def allroom_page() -> rx.Component:
    return rx.center(
    rx.box(
        rx.flex(
            rx.box(
                rx.center(
                    rx.image(
                        src="/pic/login1.webp",
                        width="100%",
                        height="100%",
                        object_fit="cover",
                    ),
                    height="100%"
                ),
                flex="1",
                width="300px",
                height="100%",
                overflow="hidden",
                border_radius="40px"
            ),  
            rx.box(
                rx.center(
                    rx.vstack(
                        rx.heading(
                            "Login",
                            width="100%",
                            text_align="center",
                            margin_bottom="30px"
                        ),

                        rx.text("Username",margin="10px 0 5px 20px",font_size="15px"),
                        rx.input(placeholder="Username", width="400px",bg="white",margin_bottom="10px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),
                        
                        rx.text("Password",margin="10px 0 5px 20px",font_size="15px"),
                        rx.input(type="password",placeholder="Password", width="400px",bg="white",margin_bottom="10px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),
                        
                        rx.text(
                            "Forget the password?",
                            width="100%",        # ← add this
                            text_align="right",
                            color="blue",
                            font_size="15px",
                            cursor="pointer",
                        ),

                        rx.button(
                            "Login",
                            width="100%",
                            text_color="white",
                            bg="#1E88E5"
                            ,height="45px",border_radius="40px",padding_left="20px",
                            margin_top="30px"
                        ),
                        
                        rx.hstack(
                            rx.text("Dont have an Account?"),
                            rx.link("Register",href="/register"),
                            margin_top="30px",
                            justify="center",
                            width="100%"
                        ),
                        
                        
                        align="start",  
                        spacing="0"
                    ),
                    height="95%"
                ),
                flex="1",
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
