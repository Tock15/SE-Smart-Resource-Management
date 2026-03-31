"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config

import requests

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            # Logo
            rx.text("SESRM", font_size="20px", font_weight="bold", color="white"),
            
            # Nav links
            rx.hstack(
                rx.link("Home", href="/", color="white", font_size="15px"),
                rx.link("Hotels", href="/hotels", color="white", font_size="15px"),
                rx.link("About", href="/about", color="white", font_size="15px"),
                spacing="6",
            ),

            # Auth buttons
            rx.hstack(
               rx.link(
                    rx.hstack(
                        rx.text("Back"),
                        rx.icon("arrow-right"),
                    ),
                    href="/login",
                    color="white",
    
                ),
            ),

            justify="between",
            align="center",
            width="100%",
            padding="0 40px",
        ),
        bg="#1E88E5",
        height="60px",
        width="100%",
        display="flex",
        align_items="center",
        position="sticky",  # ← stays on top when scrolling
        top="0",
        z_index="100",
    )


def hotel_page() -> rx.Component:
    return rx.box(
        navbar(),
        rx.vstack(
            rx.center(
            hotel_card(),
            width="100%",
        ),
            rx.center(
            hotel_card(),
            width="100%",
        ),
        rx.center(
            hotel_card(),
            width="100%",
        ),
        bg="white",
        min_height="100vh",
        padding="20px",
        ),
    )
    
def hotel_card() -> rx.Component:
    return rx.box(
        rx.flex(
            # Left - Images
            rx.box(
                rx.image(
                    src="/pic/room1.jpg",
                    width="100%",
                    height="200px",
                    object_fit="cover",
                    border_radius="8px 8px 0 0"
                ),
            ),

            # Middle - Info
            rx.box(
                rx.vstack(
                    rx.heading("Solaria Nishitetsu Hotel Bangkok", size="5",color="black"),
                    rx.hstack(
                        rx.icon("map-pin", size=14, color="#1E88E5"),
                        rx.text("Sukhumvit, Bangkok", font_size="13px", color="#1E88E5"),
                    ),
                    rx.text(
                        '"My room was spotless, with a cozy bed and great city views."',
                        font_size="13px",
                        color="gray",
                        margin_top="10px"
                    ),
                    align="start",
                    spacing="2"
                ),
                flex="1",
                padding="15px",
            ),

            # Right - Rating & Price
            rx.box(
                rx.vstack(
                    # Rating
                    rx.hstack(
                        rx.vstack(
                            rx.text("Exceptional", font_size="13px", font_weight="bold"),
                            rx.text("14588 reviews", font_size="11px", color="gray"),
                            align="end",
                            spacing="0"
                        ),
                        rx.box(
                            rx.text("9.2", color="white", font_weight="bold", font_size="18px"),
                            bg="#1E88E5",
                            padding="8px 12px",
                            border_radius="8px 8px 8px 0px",
                        ),
                        spacing="2",
                        align="center"
                    ),

                    rx.button(
                        "Check availability",
                        bg="#1E88E5",
                        color="white",
                        width="100%",
                        height="45px",
                        border_radius="8px",
                        margin_top="10px",
                        cursor="pointer"
                    ),

                    align="end",
                    spacing="2",
                    height="100%",
                    justify="between"
                ),
                width="200px",
                flex_shrink="0",
                padding="15px",
            ),

            width="100%",
            align="stretch",
        ),
        border="2px solid #e0e0e0",
        border_radius="10px",
        overflow="hidden",
        bg="white",
        width="900px",
        max_width="900px",

        
    )
    
