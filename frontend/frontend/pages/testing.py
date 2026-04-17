import reflex as rx
from frontend.state import State

class CalendarState(rx.State):
    calendar_month: int = 0
    calendar_year: int = 0
    start_date: str = ""
    end_date: str = ""
    confirmed: bool = False
    disabled_days: list[str] = []  # store as "YYYY-MM-DD" strings
    max_range: int = 100
    
    def add_disabled_day(self, day: str):
        if day not in self.disabled_days:
            self.disabled_days = self.disabled_days + [day]
            
    def has_disabled_in_range(self, start: str, end: str) -> bool:
        import datetime
        s = datetime.date.fromisoformat(start)
        e = datetime.date.fromisoformat(end)
        d = s
        while d <= e:
            if d.isoformat() in self.disabled_days:
                return True
            d += datetime.timedelta(days=1)
        return False
    
    def add_disabled_range(self, start: str, end: str):
        import datetime
        s = datetime.date.fromisoformat(start)
        e = datetime.date.fromisoformat(end)
        new_days = []
        d = s
        while d <= e:
            if d.isoformat() not in self.disabled_days:
                new_days.append(d.isoformat())
            d += datetime.timedelta(days=1)
        self.disabled_days = self.disabled_days + new_days

    @rx.var
    def disabled_days_of_month(self) -> list[int]:
        if self.calendar_year == 0 or self.calendar_month == 0:
            return []
        result = []
        for d in self.disabled_days:
            parts = d.split("-")
            if int(parts[0]) == self.calendar_year and int(parts[1]) == self.calendar_month:
                result.append(int(parts[2]))
        return result   
    def confirm_dates(self):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date
            self.confirmed = True
        elif self.start_date and self.end_date:
            self.confirmed = True

    def reset_dates(self):
        self.start_date = ""
        self.end_date = ""
        self.confirmed = False
    @rx.var
    def disabled_days_set(self) -> list[str]:
        return self.disabled_days
    @rx.var
    def padded_days(self) -> list[int]:
        import calendar
        if self.calendar_year == 0 or self.calendar_month == 0:
            return []
        offset = calendar.monthrange(self.calendar_year, self.calendar_month)[0]
        _, days_in_month = calendar.monthrange(self.calendar_year, self.calendar_month)
        return [0] * offset + list(range(1, days_in_month + 1))

    @rx.var
    def highlighted_days(self) -> list[int]:
        if not self.start_date or not self.end_date or self.calendar_month == 0:
            return []
        if not self.start_date or not self.end_date:
            return []
        import datetime
        start = datetime.date.fromisoformat(self.start_date)
        end = datetime.date.fromisoformat(self.end_date)
        result = []
        for day in range(1, 32):
            try:
                d = datetime.date(self.calendar_year, self.calendar_month, day)
                if start < d < end:
                    result.append(day)
            except ValueError:
                break
        return result

    @rx.var
    def start_day(self) -> int:
        if not self.start_date or self.calendar_month == 0:
            return -1
        import datetime
        d = datetime.date.fromisoformat(self.start_date)
        if d.year == self.calendar_year and d.month == self.calendar_month:
            return d.day
        return -1

    @rx.var
    def end_day(self) -> int:
        if not self.end_date or self.calendar_month == 0:
            return -1
        import datetime
        d = datetime.date.fromisoformat(self.end_date)
        if d.year == self.calendar_year and d.month == self.calendar_month:
            return d.day
        return -1

    @rx.var
    def month_label(self) -> str:
        import datetime
        if self.calendar_year <= 0 or self.calendar_month == 0:
            return ""
        return datetime.date(self.calendar_year, self.calendar_month, 1).strftime("%B %Y")

    def prev_month(self):
        if self.calendar_month == 1:
            if self.calendar_year <= 1:
                return
            self.calendar_month = 12
            self.calendar_year -= 1
        else:
            self.calendar_month -= 1
        print("Calendar Month: ", self.calendar_month, " Calendar Year: ", self.calendar_year)
    def getMonth(self):
        return self.calendar_month,self.calendar_year
    def next_month(self):
        if self.calendar_month == 12:
            self.calendar_month = 1; self.calendar_year += 1
        else:
            self.calendar_month += 1
        print("Calendar Month: ", self.calendar_month, " Calendar Year: ", self.calendar_year)
        
    def select_date(self, day: int):
        if self.confirmed:
            return
        import datetime
        if day == 0:
            return
        clicked = datetime.date(self.calendar_year, self.calendar_month, day).isoformat()
        if clicked < datetime.date.today().isoformat():
            return
        if any(clicked == d for d in self.disabled_days_set):
            return
        if clicked == self.end_date:
            self.end_date = ""
        elif not self.start_date or (self.start_date and self.end_date):
            self.start_date = clicked
            self.end_date = ""
        elif clicked < self.start_date:
            self.start_date = clicked
            self.end_date = ""
        else:
            if self.has_disabled_in_range(self.start_date, clicked):
                self.start_date = clicked
                self.end_date = ""
            else:
                import datetime
                s = datetime.date.fromisoformat(self.start_date)
                e = datetime.date.fromisoformat(clicked)
                diff = (e - s).days + 1  # inclusive
                if diff > self.max_range:
                    return  # exceeds max range, do nothing
                self.end_date = clicked

    def set_calendar_month_year(self):
        import datetime
        now = datetime.date.today()
        self.calendar_month = now.month
        self.calendar_year = now.year
    @rx.var
    def today_key(self) -> str:
        import datetime
        return datetime.date.today().isoformat()
    @rx.var
    def past_days(self) -> list[int]:
        import datetime
        if self.calendar_year == 0 or self.calendar_month == 0:
            return []
        today = datetime.date.today()
        result = []
        for day in range(1, 32):
            try:
                d = datetime.date(self.calendar_year, self.calendar_month, day)
                if d < today:
                    result.append(day)
            except ValueError:
                break
        return result
    async def authorization(self):
        self.set_calendar_month_year()  # add this line
        dashboard_state = await self.get_state(State)
        if dashboard_state.user_check():
            return await self.fetch_resource()
        else:
            return rx.redirect("/login")

@rx.page(route="/testing", on_load=CalendarState.set_calendar_month_year)
def calendar_page() -> rx.Component:
    week_days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    def day_cell(day: int) -> rx.Component:
        is_start = CalendarState.start_day == day
        is_end = CalendarState.end_day == day
        is_highlighted = CalendarState.highlighted_days.contains(day)
        is_endpoint = is_start | is_end
        is_empty = day == 0
        is_disabled = CalendarState.disabled_days_of_month.contains(day)
        is_past = CalendarState.past_days.contains(day)
        return rx.box(
            rx.cond(
                ~is_empty,
                rx.box(
                    rx.text(
                        day,
                        font_size="13px",
                        font_weight="400",
                        color=rx.cond(
                            is_past, "#c0c0c0",
                            rx.cond(is_disabled, "#ffb74d",  # add this
                                rx.cond(is_endpoint, "white",
                                    rx.cond(is_highlighted, "#1E88E5", "black")))
                        ),
                        text_decoration=rx.cond(
                            is_past, "line-through",
                            rx.cond(is_disabled, "line-through", "none")  # add this
                        ),
                        text_align="center",
                        line_height="32px",
                        width="32px",
                        height="32px",
                        border_radius="50%",
                        bg=rx.cond(
                            is_past, "transparent",
                            rx.cond(is_endpoint, "#1E88E5", "transparent")
                        ),
                        z_index="1",
                        position="relative",
                    ),
                    position="relative",
                    bg=rx.cond(
                        is_past, "#f5f5f5",
                        rx.cond(
                            is_disabled, "#fff3e0",
                            rx.cond(
                                is_highlighted & ~is_endpoint, "#EBF5FB",
                                rx.cond(is_start & ~is_end, "linear-gradient(to right, transparent 50%, #EBF5FB 50%)",
                                    rx.cond(is_end & ~is_start, "linear-gradient(to left, transparent 50%, #EBF5FB 50%)",
                                        "transparent"))
                            )
                        )
                    ),
                    display="flex",
                    justify_content="center",
                    align_items="center",
                    height="38px",
                    cursor="pointer",
                    on_click=CalendarState.select_date(day),
                ),
                rx.box(height="38px"),
            ),
        )

    return rx.box(
        rx.hstack(
            rx.icon("chevron-left", size=18, cursor="pointer", color="#1E88E5",
                    on_click=CalendarState.prev_month),
            rx.text(CalendarState.month_label, font_size="15px", font_weight="600",
                    color="black", text_align="center", flex="1"),
            rx.icon("chevron-right", size=18, cursor="pointer", color="#1E88E5",
                    on_click=CalendarState.next_month),
            align="center", width="100%", margin_bottom="12px",
        ),
        rx.grid(
            *[rx.text(d, font_size="12px", color="gray", text_align="center",
                      font_weight="500") for d in week_days],
            columns="7", width="100%", margin_bottom="4px",
        ),
        rx.grid(
            rx.foreach(CalendarState.padded_days, day_cell),
            columns="7", width="100%", spacing="0",
        ),
        rx.cond(
            CalendarState.start_date & CalendarState.end_date,
            rx.box(
                rx.hstack(
                    rx.icon("calendar", size=14, color="#1E88E5"),
                    rx.text(
                        CalendarState.start_date + " → " + CalendarState.end_date,
                        font_size="13px",
                        color="#555",
                    ),
                    align="center",
                    spacing="2",
                ),
                bg="#EBF5FB",
                border="1px solid #b3d4f7",
                border_radius="8px",
                padding="10px 14px",
                width="100%",
                margin_top="12px",
            ),
            rx.cond(
                CalendarState.start_date,
                rx.box(
                    rx.hstack(
                        rx.icon("calendar", size=14, color="#1E88E5"),
                        rx.text(
                            CalendarState.start_date + " → " + rx.cond(
                                CalendarState.end_date == "",
                                CalendarState.start_date,
                                CalendarState.end_date,
                            ),
                            font_size="13px",
                            color="#9e9e9e",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    bg="#F8F9FA",
                    border="1px solid #e0e0e0",
                    border_radius="8px",
                    padding="10px 14px",
                    width="100%",
                    margin_top="12px",
                ),
                rx.box(),
            ),
        ),
        rx.cond(
            ~CalendarState.confirmed,
            rx.button(
                "Confirm Dates",
                on_click=CalendarState.confirm_dates,
                disabled=(CalendarState.start_date == ""),
                bg=rx.cond(
                    CalendarState.start_date == "",
                    "#b0bec5",
                    "#1E88E5",
                ),
                color="white",
                border_radius="8px",
                padding="10px 0",
                font_size="14px",
                font_weight="600",
                width="100%",
                margin_top="12px",
                cursor=rx.cond(
                    CalendarState.start_date == "",
                    "not-allowed",
                    "pointer",
                ),
                _hover={},
            ),
            rx.vstack(
                rx.box(
                    rx.hstack(
                        rx.icon("check-circle", size=14, color="#22c55e"),
                        rx.text(
                            "Dates confirmed: " + CalendarState.start_date + " → " + CalendarState.end_date,
                            font_size="13px",
                            color="#22c55e",
                            font_weight="600",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    bg="#f0fdf4",
                    border="1px solid #bbf7d0",
                    border_radius="8px",
                    padding="10px 14px",
                    width="100%",
                    margin_top="12px",
                ),
                rx.text(
                    "Change dates",
                    font_size="12px",
                    color="#9e9e9e",
                    text_decoration="underline",
                    cursor="pointer",
                    on_click=CalendarState.reset_dates,
                    margin_top="4px",
                ),
                align="start",
                spacing="1",
                width="100%",
            ),
        ),
        padding="20px",
        border_radius="16px",
        bg="white",
        width="100%",
        max_width="100%",
        box_shadow="0 2px 12px rgba(0,0,0,0.07)",
    )