from datetime import datetime, date, timedelta
import sqlite3
from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    State,
    no_update,
    callback,
    ALL,
    ctx,
)
import dash_bootstrap_components as dbc


def create_card(card):
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.H6(
                        dbc.CardLink(
                            card["title"],
                            id={"type": "card_header", "index": card["id"]},
                            style={"color": "white"},
                        ),
                        className="card-title",
                        style={"display": "inline-block", "width": "80%"},
                    ),
                    html.H6(
                        card["sp"],
                        style={
                            "display": "inline-block",
                            "width": "19%",
                            "border-radius": "50%",
                            "border": "2px solid #666",
                            "padding": "2px",
                            "text-align": "center",
                            "background-color": "white",
                            "color": "black",
                        },
                    ),
                ],
            ),
            dbc.CardBody(
                [
                    (
                        html.Label(f"Due date: {to_timestamp(card['due_date'])}")
                        if card["due_date"]
                        else None
                    ),
                    create_dropdown(
                        {
                            "type": "dropdown_card",
                            "index": card["id"],
                            "status": card["status"],
                        },
                        "Move to:",
                    ),
                ]
            ),
        ],
        color=compute_color(card["due_date"], card["status"]),
        inverse=True,
    )


def compute_color(due_date, status="To Do"):
    if due_date and status != "Done":
        due_date = strptime(due_date)
        if due_date <= datetime.today():
            return "danger"
        elif due_date <= datetime.today() + timedelta(days=2):
            return "warning"
        return "success"
    else:
        return "secondary"


def create_dropdown(id, placeholder, *args):
    return dcc.Dropdown(
        [
            {
                "label": html.Span(["To Do"], style={"color": "black"}),
                "value": "To Do",
            },
            {
                "label": html.Span(["In Progress"], style={"color": "black"}),
                "value": "In Progress",
            },
            {
                "label": html.Span(["Blocked"], style={"color": "black"}),
                "value": "Blocked",
            },
            {
                "label": html.Span(["Done"], style={"color": "black"}),
                "value": "Done",
            },
        ],
        placeholder=placeholder,
        id=id,
        *args,
    )


def strptime(string):
    if string is not None:
        return datetime.strptime(string, "%Y-%m-%d")
    else:
        return None


def to_timestamp(string):
    if string is not None:
        return strptime(string).strftime("%d/%m/%Y")
    else:
        return None


create_card_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle(
                dcc.Input(value="", id="create_card_title", placeholder="Title")
            )
        ),
        dbc.ModalBody(
            html.Div(
                [
                    html.Label("Due date:", style={"display": "inline-block"}),
                    dcc.DatePickerSingle(
                        id="create_card_due_date",
                        initial_visible_month=date.today(),
                        date=date.today(),
                        clearable=True,
                        first_day_of_week=1,
                        placeholder="No due date",
                        display_format="DD/MM/YY",
                        style={"display": "inline-block", "margin-left": "3px"},
                    ),
                    html.Br(),
                    html.Label(
                        "Estimated duration (hours):", style={"display": "inline-block"}
                    ),
                    dcc.Input(
                        id="create_card_sp",
                        value=1,
                        type="number",
                        step="0.5",
                        min=0,
                        style={
                            "display": "inline-block",
                            "width": "60px",
                            "margin-left": "3px",
                        },
                    ),
                    html.Br(),
                    dcc.RadioItems(
                        id="create_card_sprint",
                        options=[
                            {
                                "label": html.Span(
                                    "In Sprint",
                                    style={
                                        "margin-left": "5px",
                                        "margin-right": "5px",
                                        "display": "inline-block",
                                    },
                                ),
                                "value": 1,
                            },
                            {
                                "label": html.Span(
                                    "In Backlog",
                                    style={
                                        "margin-left": "5px",
                                        "margin-right": "5px",
                                        "display": "inline-block",
                                    },
                                ),
                                "value": 0,
                            },
                        ],
                        value="In sprint",
                        inline=True,
                    ),
                    create_dropdown("create_card_status", "Status"),
                    html.Label("Description:"),
                    dcc.Textarea(
                        id="create_card_description",
                        value="",
                        style={"width": "90%", "height": 200},
                    ),
                    dcc.Store("create_card_id", data="-1"),
                ]
            )
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Delete",
                    id="button_delete",
                    style={"margin-right": "10px"},
                ),
                dbc.Button("Save & close", id="create_card_save"),
            ]
        ),
    ],
    id="create_card_modal",
    size="lg",
    is_open=False,
)


@callback(
    Output("confirm-delete", "displayed", allow_duplicate=True),
    Output("delete_id", "data", allow_duplicate=True),
    Input("button_delete", "n_clicks"),
    State("create_card_id", "data"),
    prevent_initial_call=True,
)
def delete_card(click, id):
    if click and id > 0:
        return True, id
    else:
        return False, 0


@callback(
    Output("update_page", "data", allow_duplicate=True),
    Input("create_card_save", "n_clicks"),
    State("create_card_id", "data"),
    State("create_card_title", "value"),
    State("create_card_due_date", "date"),
    State("create_card_sp", "value"),
    State("create_card_description", "value"),
    State("create_card_sprint", "value"),
    State("create_card_status", "value"),
    prevent_initial_call=True,
)
def create_card_save(n_clicks, id, *card_info):
    if id >= 0:
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute(
            """UPDATE tasks 
            SET title = ?, due_date = ?, sp = ?, description = ?, sprint = ?, status = ? 
            WHERE id = ?""",
            card_info + (id,),
        )
        con.commit()
        con.close()
        return True
    else:
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute(
            """INSERT INTO tasks(title, due_date, sp, description, sprint, status)
                    VALUES (?, ?, ?, ?, ?, ?)""",
            card_info,
        )
        con.commit()
        con.close()
        return True


def create_card_dict(id, title, due_date, sp, status):
    return {
        "title": title,
        "sp": sp,
        "status": status,
        "id": id,
        "due_date": due_date,
    }


def create_cards():
    con = sqlite3.connect("tame_management.db")
    cur = con.cursor()
    res = cur.execute(
        f"SELECT id, title, due_date, sp, status FROM tasks WHERE sprint = TRUE ORDER BY due_date NULLS LAST"
    )
    cards = []
    for c in res:
        cards.append(create_card_dict(*c))
    con.close()
    return cards


@callback(
    Output("update_page", "data", allow_duplicate=True),
    Input({"type": "dropdown_card", "index": ALL, "status": ALL}, "value"),
    prevent_initial_call=True,
)
def move_card(new_status):
    if any(new_status):
        new_status = list(filter(lambda item: item is not None, new_status))[0]
        id = ctx.triggered_id["index"]
        old_status = ctx.triggered_id["status"]
        if old_status == new_status or new_status is None:
            return no_update
        else:
            con = sqlite3.connect("tame_management.db")
            cur = con.cursor()
            cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, id))
            con.commit()
            con.close()
            return True


@callback(
    [
        Output("create_card_modal", "is_open", allow_duplicate=True),
        Output("create_card_id", "data", allow_duplicate=True),
        Output("create_card_title", "value", allow_duplicate=True),
        Output("create_card_due_date", "date", allow_duplicate=True),
        Output("create_card_sp", "value", allow_duplicate=True),
        Output("create_card_description", "value", allow_duplicate=True),
        Output("create_card_sprint", "value", allow_duplicate=True),
        Output("create_card_status", "value", allow_duplicate=True),
    ],
    Input({"type": "card_header", "index": ALL}, "n_clicks"),
    State("create_card_modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_card_modal(click, is_open):
    if any(click):
        id = ctx.triggered_id["index"]
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        res = cur.execute(
            "SELECT id, title, due_date, sp, description, sprint, status FROM tasks WHERE id = ?",
            (id,),
        ).fetchone()
        con.close()
        return toggle_new_card(click, 0, is_open, *res)
    return no_update


def max_length(dict):
    output = 0
    for key in dict:
        output = max(output, len(dict[key]))
    return output


def create_dashboard(cards):
    columns = {"To Do": [], "In Progress": [], "Blocked": [], "Done": []}
    for c in cards:
        columns[c["status"]].append(c)
    dashboard = []
    for i in range(max_length(columns) + 1):
        row = []
        for column in columns:
            if i == 0:
                row.append(dbc.Col(html.H4(column), style={"text-align": "center"}))
            else:
                try:
                    row.append(dbc.Col(create_card(columns[column][i - 1])))
                except IndexError:
                    row.append(dbc.Col())
        dashboard.append(dbc.Row(row, className="mb-4"))
    return dashboard


@callback(
    [
        Output("create_card_modal", "is_open", allow_duplicate=True),
        Output("create_card_id", "data", allow_duplicate=True),
        Output("create_card_title", "value", allow_duplicate=True),
        Output("create_card_due_date", "date", allow_duplicate=True),
        Output("create_card_sp", "value", allow_duplicate=True),
        Output("create_card_description", "value", allow_duplicate=True),
        Output("create_card_sprint", "value", allow_duplicate=True),
        Output("create_card_status", "value", allow_duplicate=True),
    ],
    Input("create_card_button", "n_clicks"),
    Input("create_card_save", "n_clicks"),
    State("create_card_modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_new_card(
    click1,
    click2,
    is_open,
    id=-1,
    title="",
    due_date=None,
    sp=1,
    description="",
    sprint=False,
    status="To Do",
):
    toggle = not is_open if click1 or click2 else is_open
    return toggle, id, title, due_date, sp, description, sprint, status


def line_backlog(id, title, due_date, duration, status, in_sprint, *args):
    color = compute_color(due_date, status)
    if color == "danger":
        color = "red"
    elif color == "success":
        color = "green"
    elif color == "warning":
        color = "orange"
    else:
        color = "gray"
    return html.Tr(
        [
            html.Td(
                [
                    dbc.CardLink(title, id={"type": "card_header", "index": id}),
                    html.Span(
                        status,
                        style={
                            "display": "inline-block",
                            "border-radius": "5px",
                            "border": "0px solid #666",
                            "padding": "3px",
                            "padding-left": "5px",
                            "padding-right": "5px",
                            "text-align": "center",
                            "background-color": color,
                            "color": "white",
                            "font-size": "12px",
                            "margin-left": "25px",
                        },
                    ),
                ],
            ),
            html.Td(
                to_timestamp(due_date), style={"width": "1%", "white-space": "nowrap"}
            ),
            html.Td(duration, style={"width": "1%", "white-space": "nowrap"}),
            html.Td(
                [
                    dbc.Button(
                        "Move to backlog" if in_sprint == 1 else "Move to sprint",
                        id={"type": "button_move", "index": id},
                    ),
                    dbc.Button(
                        "Delete",
                        id={"type": "button_delete", "index": id},
                        style={"margin-left": "10px"},
                    ),
                ],
                style={"width": "1%", "white-space": "nowrap"},
            ),
        ]
    )


def get_info_sprint():
    con = sqlite3.connect("tame_management.db")
    cur = con.cursor()
    res = cur.execute(
        "SELECT name, value FROM settings WHERE name = 'sprint_start' OR name = 'sprint_end'"
    ).fetchall()
    output = {"sprint_start": None, "sprint_end": None}
    for r in res:
        output[r[0]] = strptime(r[1])
    con.close()
    return output


@callback(
    Output("sprint_modal", "is_open", allow_duplicate=True),
    Input("start_sprint", "n_clicks"),
    prevent_initial_call=True,
)
def open_start_sprint_modal(click):
    if click:
        return True


@callback(
    Output("sprint_modal", "is_open", allow_duplicate=True),
    Output("update_page", "data", allow_duplicate=True),
    Input("start_sprint_modal", "n_clicks"),
    State("sprint_dates_modal", "start_date"),
    State("sprint_dates_modal", "end_date"),
    prevent_initial_call=True,
)
def start_sprint(click, start_date, end_date):
    if click and start_date is not None and end_date is not None:
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute(
            "UPDATE settings SET value = ? WHERE name = 'sprint_start'",
            (start_date.split("T")[0],),
        )
        cur.execute(
            "UPDATE settings SET value = ? WHERE name = 'sprint_end'",
            (end_date.split("T")[0],),
        )
        con.commit()
        con.close()
        return False, True
    if click:
        return True, no_update
    else:
        return False, no_update


def create_backlog():
    con = sqlite3.connect("tame_management.db")
    cur = con.cursor()
    res = cur.execute("SELECT value FROM settings WHERE name = 'sprint_start'")
    sprint_info = get_info_sprint()
    res = cur.execute(
        "SELECT id, title, due_date, sp, status, sprint FROM tasks ORDER BY due_date NULLS LAST, id"
    )

    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th("Name"),
                    html.Th("Due date"),
                    html.Th("Duration"),
                    html.Th("Actions"),
                ]
            )
        )
    ]

    sp = {"To Do": 0, "In Progress": 0, "Blocked": 0, "Done": 0}
    rows_sprint = []
    rows_backlog = []
    for task in res:
        row = line_backlog(*task)
        if task[5] == 1:
            rows_sprint.append(row)
            if task[4] != "Done":
                sp[task[4]] += task[3]
        else:
            if task[4] == "Done":
                continue
            rows_backlog.append(row)
    con.close()

    table_sprint_body = [html.Tbody(rows_sprint)]
    table_backlog_body = [html.Tbody(rows_backlog)]
    table_sprint = dbc.Table(
        table_header + table_sprint_body, bordered=True, hover=True, striped=True
    )
    table_backlog = dbc.Table(
        table_header + table_backlog_body, bordered=True, hover=True, striped=True
    )

    text_sp = " / ".join(
        [f"{key}: {value}" for key, value in sp.items() if key != "Done"]
    )

    close_sprint = dbc.Button(
        "Close Sprint",
        id="close_sprint",
        style={"margin-top": "-25px"},
    )
    start_sprint = dbc.Button(
        "Start Sprint",
        id="start_sprint",
        style={"margin-top": "-25px"},
    )

    sprint_modal = dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Start a new sprint")),
            dbc.ModalBody(
                html.Div(
                    [
                        dcc.DatePickerRange(
                            id="sprint_dates_modal",
                            min_date_allowed=datetime.today(),
                            initial_visible_month=datetime.today(),
                            first_day_of_week=1,
                            display_format="DD/MM/YY",
                            start_date=datetime.today(),
                            end_date=datetime.today() + timedelta(days=14),
                        )
                    ]
                )
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("Start sprint", id="start_sprint_modal"),
                ]
            ),
        ],
        id="sprint_modal",
        size="lg",
        is_open=False,
    )

    return html.Div(
        [
            sprint_modal,
            html.H2("Current Sprint"),
            dbc.Row(
                [
                    dbc.Col(
                        [text_sp + " / ", html.B(f"Total: {sum(sp.values())}")],
                        width=9,
                    ),
                    dbc.Col(
                        close_sprint if sprint_info["sprint_start"] else start_sprint
                    ),
                ]
            ),
            table_sprint,
            html.H2("Backlog"),
            table_backlog,
        ],
        style={"margin": "auto", "width": "90%", "margin-top": "20px"},
    )


@callback(
    Output("update_page", "data", allow_duplicate=True),
    Input("close_sprint", "n_clicks"),
    prevent_initial_call=True,
)
def close_sprint(click):
    if click:
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute(
            """UPDATE tasks SET sprint = FALSE WHERE sprint = TRUE AND status = 'Done'"""
        )
        cur.execute(
            """UPDATE settings SET value = NULL WHERE name = 'sprint_start' OR name = 'sprint_end'"""
        )
        con.commit()
        con.close()
        return True
    return False


@callback(
    Output("search_result", "children"),
    Input("searchbar", "n_submit"),
    State("searchbar", "value"),
    prevent_initial_call=True,
)
def search(start, value):
    if value:
        escaped_value = '"' + '" "'.join(value.split(" ")) + '"'
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        res = cur.execute(
            """SELECT tasks.id, tasks.title, due_date, sp, status, sprint, bm25(tasks_fts5, 0, 5, 1) as bm25
            FROM tasks INNER JOIN tasks_fts5 on tasks.id = tasks_fts5.id 
            WHERE tasks_fts5 MATCH (?) 
            ORDER BY bm25""",
            (escaped_value,),
        )
        table_header = [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Name"),
                        html.Th("Due date"),
                        html.Th("Duration"),
                        html.Th("Actions"),
                    ]
                )
            )
        ]
        search_results = []
        for task in res:
            row = line_backlog(*task)
            search_results.append(row)
        return dbc.Table(
            table_header + [html.Tbody(search_results)], hover=True, striped=True
        )
    return no_update


def create_search():
    searchbar = dcc.Input(
        id="searchbar",
        placeholder="Search for...",
        size="lg",
        autoFocus=True,
        debounce=True,
        style={"width": "95%"},
    )
    return html.Div(
        [
            searchbar,
            html.Div(html.P("Enter a query and press 'enter'."), id="search_result"),
        ],
        style={"margin": "auto", "width": "90%", "margin-top": "20px"},
    )


def layout():
    return [
        html.Div(
            [
                dcc.Location(id="url"),
                dbc.NavbarSimple(
                    children=[
                        dbc.Button(
                            "New task", id=f"create_card_button", className="ms-auto"
                        ),
                        dbc.NavLink("Current sprint", href="/", active="exact"),
                        dbc.NavLink("Backlog", href="/backlog", active="exact"),
                        dbc.NavLink("Search", href="/search", active="exact"),
                        # dbc.NavLink("Settings", href="/settings", active="exact"),
                    ],
                    brand="TameManagement",
                    color="dark",
                    dark=True,
                ),
                dcc.Store("update_page", data="False"),
                dcc.Store(id="delete_id", data=-1),
                dcc.ConfirmDialog(
                    id="confirm-delete",
                    message="You are going to delete a task. This action is not revertible. Are ou sure?",
                    displayed=False,
                ),
                create_card_modal,
            ]
        ),
        html.Div(
            create_dashboard(create_cards()),
            style={"margin": "auto", "width": "90%", "margin-top": "20px"},
            id="dashboard",
        ),
    ]


@callback(
    Output("confirm-delete", "displayed", allow_duplicate=True),
    Output("delete_id", "data"),
    Input({"type": "button_delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_button(click):
    if any(click):
        return True, ctx.triggered_id["index"]
    else:
        return False, 0


@callback(
    Output("update_page", "data", allow_duplicate=True),
    Input({"type": "button_move", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def move_button(click):
    if any(click):
        id = ctx.triggered_id["index"]
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute(
            """UPDATE tasks SET sprint = mod(sprint+1, 2) WHERE id = ?""", (id,)
        )
        con.commit()
        con.close()
        return True
    return no_update


@callback(
    Output("update_page", "data", allow_duplicate=True),
    Output("create_card_modal", "is_open"),
    Input("confirm-delete", "submit_n_clicks"),
    Input("confirm-delete", "cancel_n_clicks"),
    State("delete_id", "data"),
    prevent_initial_call=True,
)
def confirm_delete(confirm_delete, cancel_delete, id):
    if confirm_delete:
        con = sqlite3.connect("tame_management.db")
        cur = con.cursor()
        cur.execute("""DELETE FROM tasks WHERE id = ?""", (id,))
        con.commit()
        con.close()
        return True, False
    return no_update


@callback(
    Output("dashboard", "children"),
    Input("update_page", "data"),
    Input("url", "pathname"),
)
def render_page_content(_, pathname):
    if pathname == "/":
        return create_dashboard(create_cards())
    elif pathname == "/backlog":
        return create_backlog()
    elif pathname == "/search":
        return create_search()
    elif pathname == "/settings":
        return html.H1("Settings")

    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognized..."),
        ],
        className="p-3 bg-light rounded-3",
    )


app = Dash(suppress_callback_exceptions=True)
app.layout = layout

if __name__ == "__main__":
    app.run(debug=True)
