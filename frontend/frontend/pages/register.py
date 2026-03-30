"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
import requests

class RegisterState(rx.State):
    username: str = ""
    email: str = ""
    student_id: str = ""
    password: str = ""
    role: str = "student"
    token: str = ""
    async def register(self):
        res = requests.post(
            "http://localhost:8000/register",
            json={
                "username": self.username,
                "email": self.email,
                "student_id": self.student_id,
                "password": self.password,
                "role": self.role,
            },
        )
        if res.status_code == 200:
            self.token = res.json()["access_token"]
        
def register_page() -> rx.Component:
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
                            margin_bottom="20px"
                        ),
                        rx.text("Student_ID",margin="5px 0 5px 20px",font_size="15px"),
                        rx.input(value=RegisterState.student_id,on_change=RegisterState.set_student_id,placeholder="Username", width="400px",bg="white",margin_bottom="5px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),

                        rx.text("Username",margin="5px 0 5px 20px",font_size="15px"),
                        rx.input(value=RegisterState.username,on_change=RegisterState.set_username,placeholder="Username", width="400px",bg="white",margin_bottom="5px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),

                        rx.text("Email",margin="5px 0 5px 20px",font_size="15px"),
                        rx.input(value=RegisterState.email,on_change=RegisterState.set_email,placeholder="Email", width="400px",bg="white",margin_bottom="5px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),
                        
                        rx.text("Password",margin="5px 0 5px 20px",font_size="15px"),
                        rx.input(type="password",value=RegisterState.password,on_change=RegisterState.set_password,placeholder="Password", width="400px",bg="white",margin_bottom="5px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),

                        rx.text("Confirm password",margin="5px 0 5px 20px",font_size="15px"),
                        rx.input(type="password",placeholder="Confirm Password", width="400px",bg="white",margin_bottom="25px",height="45px",border_radius="45px",padding_left="20px",color="black",font_size="17px"),

                        rx.radio_group(
                            items=["student", "teacher"],
                            direction="row",
                            margin_bottom="40px",
                            value=RegisterState.role,
                            on_change=RegisterState.set_role,
                        ),
                        
                        rx.button(
                            "Submit",
                            width="100%",
                            text_color="white",
                            bg="#1E88E5"
                            ,height="45px",border_radius="40px",padding_left="20px",
                            on_click=RegisterState.register,
                        ),
                        
                        
                        align="start",  
                        spacing="0"
                    ),
                    height="100%"
                ),
                flex="1"
            ),

            rx.box(
                rx.image(
                    src="/pic/room1.jpg",
                    width="100%",
                    height="100%",
                    object_fit="cover",  # ← move this to the image
                ),
                flex="1",
                width="300px",
                height="100%",
                overflow="hidden",
                border_radius="60px"
            ),   # space between boxes
            width="100%",
            height="100%",
            overflow="hidden"
        ),
        width="1000px",
        height="675px",
        padding="20px",
        border_radius="60px",
        bg="linear-gradient(to bottom, #4facfe, #00f2fe)"
    ),
    height="100vh",
    bg="gray"
)
