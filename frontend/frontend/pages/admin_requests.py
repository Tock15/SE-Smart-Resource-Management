import reflex as rx
from frontend.state import State   

@rx.page(route="/admin/requests", on_load=State.admin_authorization)
def admin_dashboard() -> rx.Component:
    return(
        rx.text("Test dashboard")
    )