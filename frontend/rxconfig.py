import reflex as rx

config = rx.Config(
    app_name="frontend",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    api_url="http://localhost:8001"
)