import reflex as rx
import requests
class State(rx.State):
    token : str = ""
    token_type : str = ""