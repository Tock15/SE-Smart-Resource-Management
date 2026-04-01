"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from frontend.state import State
import requests
class LoginState(rx.State):
    username: str = ""
    password: str = ""
    token: str = ""
    token_type: str = ""
    role: str = "student"
    error_message: str = ""

    async def login_function(self):
        res = requests.post(
            "http://localhost:8000/auth/login",
            data={
                "username": self.username,
                "password": self.password,
            },
        )
        if res.status_code == 200:
            data = res.json()
            self.token = data["access_token"]
            self.token_type = data["token_type"]
            self.error_message = ""

            home_state = await self.get_state(State)
            home_state.set_user_data(
                username=self.username,
                token=self.token,
                token_type=self.token_type,
            )
            decoded = home_state.verify_token()['message']['role']
            home_state.set_user_data(
                role=decoded
            )
            print(decoded)

            return rx.redirect("/")
        elif res.status_code == 401:
            self.error_message = "Wrong username or password"
            print(self.error_message)
        elif res.status_code == 422:
            self.error_message = "Invalid input"
            print(self.error_message)
        elif res.status_code == 500:
            self.error_message = "Server error, try again later"
            print(self.error_message)
        else:
            self.error_message = f"Unexpected error: {res.status_code}"
            print(self.error_message)
    def getToken(self):
        return {"token":self.token,"token_type":self.token_type}
    

def login_page() -> rx.Component:
    return rx.center(
    rx.box(
        rx.flex(
            rx.box(
                rx.link(
                    rx.hstack(
                        rx.icon("arrow-left"),
                        rx.text("Back"),
                    ),
                    href="/",
                    color="white",
                    position="absolute",
                    top="20px",
                    left="20px",
                ),
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
                        rx.input(on_change=LoginState.set_username,value=LoginState.username,placeholder="Username", width="400px",bg="white",margin_bottom="10px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),
                        
                        rx.text("Password",margin="10px 0 5px 20px",font_size="15px"),
                        rx.input(type="password",on_change=LoginState.set_password,value=LoginState.password,placeholder="Password", width="400px",bg="white",margin_bottom="10px",height="45px",border_radius="40px",padding_left="20px",color="black",font_size="17px"),
                        
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
                            on_click=LoginState.login_function,margin_top="30px",
                            
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
