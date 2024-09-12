import datetime
from typing import Any

from nicegui import ui
from nicegui.elements.input import Input
from nicegui.elements.label import Label

from clarity.format import format_date, format_timespan
from clarity.fs import write_plan_note, read_plan_note
from clarity.parse import (
    ParseError,
    ParsedTimeSpan,
    construct_time_spent_map,
    get_current_task_status,
    parse_schedule,
)
from clarity.visualize import plot_time_spent_map

time_spent_map: dict[str, int] = {}
schedule: list[ParsedTimeSpan] = []
selected_date = str(datetime.date.today())


def date_selector(name: str, init_date: str) -> Input:
    date_input = ui.input(name, value=init_date).classes("px-4")

    with date_input as date_input:
        with ui.menu().props("no-parent-event") as menu:
            with ui.date().bind_value(date_input):
                with ui.row().classes("justify-end"):
                    ui.button("Close", on_click=menu.close).props("flat")
        with date_input.add_slot("append"):
            ui.icon("edit_calendar").on("click", menu.open).classes("cursor-pointer")

    return date_input


@ui.refreshable
def plot(time_spent_map: dict[str, int]) -> None:
    plot = ui.matplotlib()

    with plot.figure as fig:
        plot_time_spent_map(time_spent_map, fig)

    plot._props["innerHTML"] = plot._props["innerHTML"].replace(
        "<svg", '<svg style="width:100%;height:100%"'
    )


def status_bar() -> tuple[Label, Input, Label, Label, Label]:
    date_label = ui.label().classes("text-2xl px-4")
    date_input = date_selector("Date", selected_date)
    task_label = ui.label().classes("text-3xl px-4 flex-grow text-right font-bold")
    task_dot = ui.label("•").classes("text-5xl font-bold")
    time_label = ui.label().classes("text-4xl text-red-600 px-4 font-bold")

    return date_label, date_input, task_label, task_dot, time_label


ui.add_css("""
    :root {
        --nicegui-default-padding: 0;
        --nicegui-default-gap: 0;
    }
""")


with ui.row().classes("flex-nowrap gap-0 p-0"):
    with ui.tabs().props("vertical").classes("w-22") as tabs:
        planner = ui.tab("Planner", icon="schedule")
        calendar = ui.tab("Calender", icon="calendar_month")
        settings = ui.tab("Settings", icon="settings")
    with ui.tab_panels(tabs, value=planner):
        with ui.tab_panel(planner).classes("p-0 h-screen"):
            with ui.column().classes("w-full h-screen"):
                with ui.row().classes("items-center flex w-full"):
                    date_label, date_input, task_label, task_dot, time_label = (
                        status_bar()
                    )

                with ui.grid(columns=2).classes("gap-0 w-full h-screen"):
                    editor = ui.codemirror("").classes("h-full text-xl p-0")
                    plot(time_spent_map)


def on_tick() -> None:
    if selected_date != str(datetime.date.today()):
        disable_task_status()
        return

    now = datetime.datetime.now()

    current_task_status = get_current_task_status(schedule, now)

    if current_task_status:
        task_label.set_text(current_task_status.name)
        task_dot.set_visibility(True)
        time_label.set_text(format_timespan(current_task_status.remaining))
    else:
        disable_task_status()


def on_editor(_: Any) -> None:
    global time_spent_map
    global schedule

    try:
        write_plan_note(selected_date, editor.value)

        schedule = parse_schedule(
            editor.value, datetime.datetime.fromisoformat(selected_date)
        )
        time_spent_map = construct_time_spent_map(schedule)

        plot.refresh(time_spent_map)
    except ParseError:
        pass


def on_select_date(value: str) -> None:
    global selected_date

    selected_date = value

    plan_note = read_plan_note(selected_date)

    editor.set_value(plan_note)
    date_label.set_text(format_date(value))


def disable_task_status() -> None:
    task_label.set_text("")
    task_dot.set_visibility(False)
    time_label.set_text("")


on_select_date(date_input.value)
date_input.on_value_change(lambda e: on_select_date(e.value))

on_editor(None)
on_tick()
editor.on_value_change(on_editor)

ui.timer(1, on_tick)
