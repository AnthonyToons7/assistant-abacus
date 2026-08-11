import calendar as pycalendar
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, date
import dateparser

# -- Palette ------------------------------------------------------------------
BG = "#081229"
PANEL = "#0e1b3d"
CARD = "#13295a"
ACCENT = "#2a65df"
ACCENT2 = "#8bb1ff"
TEXT = "#eaf4ff"
SUBTEXT = "#9fb8e4"
BORDER = "#2f4f8e"

FONT_TITLE = ("Segoe UI Semibold", 13)
FONT_LABEL = ("Segoe UI Semibold", 10)
FONT_SUB = ("Segoe UI", 9)
FONT_BTN = ("Segoe UI Semibold", 10)


def section_header(parent, text):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill=tk.X, pady=(16, 4), padx=4)
    tk.Label(
        f,
        text=text.upper(),
        font=("Segoe UI Semibold", 8),
        bg=BG,
        fg=ACCENT2,
    ).pack(side=tk.LEFT, padx=4)
    tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 4))


def make_checkbox(parent, title, description, var):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    left = tk.Frame(row, bg=CARD)
    left.pack(side=tk.LEFT, fill=tk.X, expand=True)
    tk.Label(left, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
    if description:
        tk.Label(left, text=description, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

    canvas = tk.Canvas(row, width=42, height=22, bg=CARD, highlightthickness=0, cursor="hand2")
    canvas.pack(side=tk.RIGHT, padx=(8, 0))

    def draw():
        canvas.delete("all")
        on = var.get()
        color = ACCENT if on else BORDER
        canvas.create_oval(0, 2, 20, 20, fill=color, outline="")
        canvas.create_oval(22, 2, 42, 20, fill=color, outline="")
        canvas.create_rectangle(10, 2, 32, 20, fill=color, outline="")
        kx = 23 if on else 3
        canvas.create_oval(kx, 4, kx + 16, 18, fill=TEXT, outline="")

    def toggle(_=None):
        var.set(not var.get())
        draw()

    canvas.bind("<Button-1>", toggle)
    row.bind("<Button-1>", toggle)
    draw()


def make_dropdown(parent, title, description, var, options):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    tk.Label(row, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
    if description:
        tk.Label(row, text=description, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Abacus.TCombobox",
        fieldbackground=PANEL,
        background=PANEL,
        foreground=TEXT,
        selectbackground=ACCENT,
        selectforeground=TEXT,
        arrowcolor=ACCENT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
    )
    style.map("Abacus.TCombobox", fieldbackground=[("readonly", PANEL)])

    combo = ttk.Combobox(
        row,
        textvariable=var,
        values=options,
        state="readonly",
        style="Abacus.TCombobox",
        font=FONT_SUB,
    )
    combo.pack(fill=tk.X, pady=(6, 0))
    return combo


def make_text_input(parent, title, description, var):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    tk.Label(row, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
    if description:
        tk.Label(row, text=description, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

    entry = tk.Entry(
        row,
        textvariable=var,
        font=FONT_SUB,
        bg=PANEL,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
    )
    entry.pack(fill=tk.X, pady=(6, 0), ipady=5)


def make_action_button(parent, label, on_click=None):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    btn = tk.Button(
        row,
        text=label,
        font=FONT_BTN,
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#3b78ef",
        activeforeground=TEXT,
        relief="flat",
        cursor="hand2",
        pady=6,
        command=on_click or (lambda: None),
    )
    btn.pack(fill=tk.X)
    btn.bind("<Enter>", lambda e: btn.config(bg="#3b78ef", fg=TEXT))
    btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT, fg="#ffffff"))
    return btn


def make_spotify_devices_widget(parent, title, description, devices_dict, on_change):
    outer = tk.Frame(parent, bg=CARD, padx=16, pady=12)
    outer.pack(fill=tk.X, pady=(0, 2))

    tk.Label(outer, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
    if description:
        tk.Label(outer, text=description, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

    dd_row = tk.Frame(outer, bg=CARD)
    dd_row.pack(fill=tk.X, pady=(8, 0))

    selected_var = tk.StringVar()

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Abacus.TCombobox",
        fieldbackground=PANEL,
        background=PANEL,
        foreground=TEXT,
        selectbackground=ACCENT,
        selectforeground=TEXT,
        arrowcolor=ACCENT,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
    )
    style.map("Abacus.TCombobox", fieldbackground=[("readonly", PANEL)])

    combo = ttk.Combobox(
        dd_row,
        textvariable=selected_var,
        state="readonly",
        style="Abacus.TCombobox",
        font=FONT_SUB,
    )
    combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def refresh_combo():
        keys = list(devices_dict.keys())
        combo["values"] = keys
        if keys:
            if selected_var.get() not in keys:
                selected_var.set(keys[0])
        else:
            selected_var.set("")

    refresh_combo()

    def delete_selected():
        alias = selected_var.get()
        if alias and alias in devices_dict:
            del devices_dict[alias]
            refresh_combo()
            on_change()
            refresh_real_name_hint()

    del_btn = tk.Button(
        dd_row,
        text="X  Remove",
        font=FONT_SUB,
        bg=PANEL,
        fg="#ff7588",
        activebackground="#ff5e73",
        activeforeground=TEXT,
        relief="flat",
        cursor="hand2",
        padx=10,
        pady=4,
        command=delete_selected,
    )
    del_btn.pack(side=tk.RIGHT)
    del_btn.bind("<Enter>", lambda e: del_btn.config(bg="#ff5e73", fg=TEXT))
    del_btn.bind("<Leave>", lambda e: del_btn.config(bg=PANEL, fg="#ff7588"))

    hint_var = tk.StringVar()
    hint_label = tk.Label(outer, textvariable=hint_var, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w")
    hint_label.pack(fill=tk.X, pady=(2, 0))

    def refresh_real_name_hint(*_):
        alias = selected_var.get()
        if alias and alias in devices_dict:
            hint_var.set(f"  -> real name: {devices_dict[alias]}")
        else:
            hint_var.set("")

    selected_var.trace_add("write", refresh_real_name_hint)
    refresh_real_name_hint()

    tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, pady=(12, 8))

    tk.Label(
        outer,
        text="ADD NEW DEVICE",
        font=("Segoe UI Semibold", 8),
        bg=CARD,
        fg=ACCENT2,
        anchor="w",
    ).pack(fill=tk.X, pady=(0, 6))

    alias_var = tk.StringVar()
    realname_var = tk.StringVar()
    error_var = tk.StringVar()

    def _styled_entry(parent_frame, textvar, placeholder):
        e = tk.Entry(
            parent_frame,
            textvariable=textvar,
            font=FONT_SUB,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        e.pack(fill=tk.X, pady=(0, 6), ipady=5)

        def _on_focus_in(_):
            if textvar.get() == placeholder:
                textvar.set("")
                e.config(fg=TEXT)

        def _on_focus_out(_):
            if not textvar.get():
                textvar.set(placeholder)
                e.config(fg=SUBTEXT)

        textvar.set(placeholder)
        e.config(fg=SUBTEXT)
        e.bind("<FocusIn>", _on_focus_in)
        e.bind("<FocusOut>", _on_focus_out)
        return e

    placeholder_alias = "Internal name (e.g. Living Room)"
    placeholder_realname = "Real device name (e.g. Sonos Era 100)"

    _styled_entry(outer, alias_var, placeholder_alias)
    _styled_entry(outer, realname_var, placeholder_realname)

    tk.Label(outer, textvariable=error_var, font=FONT_SUB, bg=CARD, fg="#ff4d6d", anchor="w").pack(fill=tk.X)

    def add_device():
        alias = alias_var.get().strip()
        realname = realname_var.get().strip()

        if not alias or alias == placeholder_alias:
            error_var.set("Warning: Internal name is required.")
            return
        if not realname or realname == placeholder_realname:
            error_var.set("Warning: Real device name is required.")
            return
        if alias in devices_dict:
            error_var.set(f"Warning: '{alias}' already exists.")
            return

        error_var.set("")
        devices_dict[alias] = realname
        refresh_combo()
        selected_var.set(alias)
        on_change()

        alias_var.set(placeholder_alias)
        realname_var.set(placeholder_realname)

    add_btn = tk.Button(
        outer,
        text="+  Add Device",
        font=FONT_BTN,
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#3b78ef",
        activeforeground="#ffffff",
        relief="flat",
        cursor="hand2",
        pady=6,
        command=add_device,
    )
    add_btn.pack(fill=tk.X, pady=(6, 0))
    add_btn.bind("<Enter>", lambda e: add_btn.config(bg="#3b78ef"))
    add_btn.bind("<Leave>", lambda e: add_btn.config(bg=ACCENT))

    return selected_var


def _resolve_theme(saved):
    global BG, PANEL, CARD, ACCENT, ACCENT2, TEXT, SUBTEXT, BORDER
    if saved.get("light_mode", False):
        BG = "#eef4ff"
        PANEL = "#dbe8ff"
        CARD = "#ffffff"
        ACCENT = "#2a65df"
        ACCENT2 = "#4f7fda"
        TEXT = "#13295a"
        SUBTEXT = "#5f79a8"
        BORDER = "#b6caec"
    else:
        BG = "#081229"
        PANEL = "#0e1b3d"
        CARD = "#13295a"
        ACCENT = "#2a65df"
        ACCENT2 = "#8bb1ff"
        TEXT = "#eaf4ff"
        SUBTEXT = "#9fb8e4"
        BORDER = "#2f4f8e"


def _open_add_event_dialog(window, day_date, events_getter, events_setter, refresh_calendar):
    dialog = tk.Toplevel(window)
    dialog.title("Add Event")
    dialog.configure(bg=BG)
    dialog.attributes("-topmost", False)
    dialog.transient(window)
    dialog.grab_set()
    dialog.geometry("460x780")

    wrap = tk.Frame(dialog, bg=BG, padx=16, pady=16)
    wrap.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        wrap,
        text=f"New Event - {day_date.strftime('%A %d %B %Y')}",
        font=FONT_TITLE,
        bg=BG,
        fg=ACCENT2,
        anchor="w",
    ).pack(fill=tk.X, pady=(0, 12))

    title_var = tk.StringVar()
    description_var = tk.StringVar()
    start_time_var = tk.StringVar(value="09:00")
    end_time_var = tk.StringVar(value="10:00")
    reminder_minutes_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="")

    def field(label, var, hint=""):
        card = tk.Frame(wrap, bg=CARD, padx=12, pady=10)
        card.pack(fill=tk.X, pady=(0, 8))
        tk.Label(card, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
        if hint:
            tk.Label(card, text=hint, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)
        entry = tk.Entry(
            card,
            textvariable=var,
            font=FONT_SUB,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        entry.pack(fill=tk.X, pady=(6, 0), ipady=5)
        return entry

    title_entry = field("Title", title_var)
    field("Description", description_var)
    field("Start time", start_time_var, "24h format HH:MM")
    field("End time", end_time_var, "24h format HH:MM")
    field("Reminder", reminder_minutes_var, "Minutes before start, optional")

    tk.Label(wrap, textvariable=status_var, font=FONT_SUB, bg=BG, fg="#ff4d6d", anchor="w").pack(fill=tk.X, pady=(2, 8))

    btn_row = tk.Frame(wrap, bg=BG)
    btn_row.pack(fill=tk.X)

    def parse_time(s):
        try:
            hour, minute = [int(x) for x in s.split(":", 1)]
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                return None
            return hour, minute
        except Exception:
            return None

    def save_event():
        title = title_var.get().strip()
        description = description_var.get().strip()
        start_parts = parse_time(start_time_var.get().strip())
        end_parts = parse_time(end_time_var.get().strip())

        if not title:
            status_var.set("Title is required.")
            return
        if not description:
            status_var.set("Description is required.")
            return
        if start_parts is None:
            status_var.set("Start time must be HH:MM.")
            return
        if end_parts is None:
            status_var.set("End time must be HH:MM.")
            return

        start_dt = datetime(day_date.year, day_date.month, day_date.day, start_parts[0], start_parts[1])
        end_dt = datetime(day_date.year, day_date.month, day_date.day, end_parts[0], end_parts[1])
        if end_dt <= start_dt:
            status_var.set("End time must be after start time.")
            return

        reminder_payload = []
        reminder_raw = reminder_minutes_var.get().strip()
        if reminder_raw:
            reminder_value = reminder_raw.split(",")
            for rv in reminder_value:
                rv = rv.strip()
                if not rv:
                    continue

                if rv.isdigit():
                    minutes = int(rv)
                    if minutes <= 0:
                        status_var.set("Reminder minutes must be greater than 0.")
                        return
                    reminder_dt = start_dt - timedelta(minutes=minutes)
                else:
                    reminder_dt = dateparser.parse(rv)

                if reminder_dt is None:
                    status_var.set(f"Could not parse reminder value: '{rv}'.")
                    return

                reminder_payload.append(
                    {
                        "time": json_serial(reminder_dt),
                        "reminded": False,
                    }
                )

        new_event = {
            "title": title,
            "description": description,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "reminder": reminder_payload,
        }

        events = events_getter()
        if not isinstance(events, list):
            events = []
        events.append(new_event)
        events_setter(events)

        refresh_calendar()
        dialog.destroy()

    cancel_btn = tk.Button(
        btn_row,
        text="Cancel",
        font=FONT_SUB,
        bg=PANEL,
        fg=SUBTEXT,
        activebackground="#2a406f",
        activeforeground=TEXT,
        relief="flat",
        cursor="hand2",
        command=dialog.destroy,
        padx=14,
        pady=6,
    )
    cancel_btn.pack(side=tk.LEFT)

    save_btn = tk.Button(
        btn_row,
        text="Add Event",
        font=FONT_BTN,
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#3b78ef",
        activeforeground="#ffffff",
        relief="flat",
        cursor="hand2",
        command=save_event,
        padx=14,
        pady=6,
    )
    save_btn.pack(side=tk.RIGHT)

    title_entry.focus_set()


def _open_event_details_dialog(window, event):
    dialog = tk.Toplevel(window)
    dialog.title("Event Details")
    dialog.configure(bg=BG)
    dialog.attributes("-topmost", True)
    dialog.transient(window)
    dialog.grab_set()
    dialog.geometry("480x560")

    wrap = tk.Frame(dialog, bg=BG, padx=16, pady=16)
    wrap.pack(fill=tk.BOTH, expand=True)

    def parse_dt(value):
        if not value:
            return None
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                dt = dt.astimezone().replace(tzinfo=None)
            return dt
        except Exception:
            return None

    title_text = str(event.get("title", "Event"))
    desc_text = str(event.get("description", ""))
    start_dt = parse_dt(event.get("start_date"))
    end_dt = parse_dt(event.get("end_date"))
    reminder = event.get("reminder", [])
    if isinstance(reminder, dict):
        reminder = [reminder]
    if not isinstance(reminder, list):
        reminder = []

    tk.Label(wrap, text=title_text, font=FONT_TITLE, bg=BG, fg=ACCENT2, anchor="w").pack(fill=tk.X, pady=(0, 12))

    card = tk.Frame(wrap, bg=CARD, padx=12, pady=12)
    card.pack(fill=tk.BOTH, expand=True)

    def info_row(label, value):
        row = tk.Frame(card, bg=CARD)
        row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(row, text=label, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
        tk.Label(row, text=value, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w", justify="left", wraplength=420).pack(fill=tk.X, pady=(2, 0))

    info_row("Description", desc_text or "(No description)")
    info_row("Start", start_dt.strftime("%A %d %B %Y %H:%M") if start_dt else str(event.get("start_date", "-")))
    info_row("End", end_dt.strftime("%A %d %B %Y %H:%M") if end_dt else str(event.get("end_date", "-")))

    if reminder:
        readable = []
        for item in reminder:
            dt = parse_dt(item.get("time") if isinstance(item, dict) else None)
            if dt is not None:
                flag = "done" if item.get("reminded") else "pending"
                readable.append(f"- {dt.strftime('%d %b %Y %H:%M')} ({flag})")
        info_row("Reminders", "\n".join(readable) if readable else "Configured")
    else:
        info_row("Reminders", "None")

    close_btn = tk.Button(
        wrap,
        text="Close",
        font=FONT_BTN,
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#3b78ef",
        activeforeground="#ffffff",
        relief="flat",
        cursor="hand2",
        command=dialog.destroy,
        pady=8,
    )
    close_btn.pack(fill=tk.X, pady=(10, 0))


def _open_day_events_dialog(window, day_date, day_events):
    dialog = tk.Toplevel(window)
    dialog.title("Day Events")
    dialog.configure(bg=BG)
    dialog.attributes("-topmost", True)
    dialog.transient(window)
    dialog.grab_set()
    dialog.geometry("500x720")

    wrap = tk.Frame(dialog, bg=BG, padx=16, pady=16)
    wrap.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        wrap,
        text=f"Events - {day_date.strftime('%A %d %B %Y')}",
        font=FONT_TITLE,
        bg=BG,
        fg=ACCENT2,
        anchor="w",
    ).pack(fill=tk.X, pady=(0, 12))

    list_area = tk.Frame(wrap, bg=BG)
    list_area.pack(fill=tk.BOTH, expand=True)

    for event in day_events:
        title = str(event.get("title", "Event"))

        row = tk.Frame(list_area, bg=CARD, padx=10, pady=8, cursor="hand2")
        row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(row, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
        tk.Label(row, text="Click to view details", font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

        def on_row_click(_event, ev=event):
            _open_event_details_dialog(window, ev)
            return "break"

        row.bind("<Button-1>", on_row_click)
        for child in row.winfo_children():
            child.bind("<Button-1>", on_row_click)

    close_btn = tk.Button(
        wrap,
        text="Close",
        font=FONT_BTN,
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#3b78ef",
        activeforeground="#ffffff",
        relief="flat",
        cursor="hand2",
        command=dialog.destroy,
        pady=8,
    )
    close_btn.pack(fill=tk.X, pady=(10, 0))


def _build_schedule_tab(parent, events_getter, events_setter):
    current = {"year": datetime.now().year, "month": datetime.now().month}

    root = tk.Frame(parent, bg=BG)
    root.pack(fill=tk.BOTH, expand=True)

    header = tk.Frame(root, bg=BG)
    header.pack(fill=tk.X, padx=16, pady=(12, 6))

    month_label = tk.Label(header, text="", font=FONT_TITLE, bg=BG, fg=ACCENT2)
    month_label.pack(side=tk.LEFT)

    nav = tk.Frame(header, bg=BG)
    nav.pack(side=tk.RIGHT)

    grid_wrap = tk.Frame(root, bg=BG)
    grid_wrap.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

    legend = tk.Label(
        root,
        text="Click any day card to add a new event.",
        font=FONT_SUB,
        bg=BG,
        fg=SUBTEXT,
        anchor="w",
    )
    legend.pack(fill=tk.X, padx=16, pady=(0, 12))

    def parse_event_start(event):
        raw = event.get("start_date") if isinstance(event, dict) else None
        if raw is None:
            return None
        try:
            dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                dt = dt.astimezone().replace(tzinfo=None)
            return dt
        except Exception:
            return None

    def format_event_time(event):
        dt = parse_event_start(event)
        if dt is None:
            return "--:--"
        return dt.strftime("%H:%M")

    def shift_month(offset):
        month = current["month"] + offset
        year = current["year"]
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        current["year"] = year
        current["month"] = month
        rebuild()

    def bind_day_click(widget, day_date):
        widget.bind(
            "<Button-1>",
            lambda _e, target=day_date: _open_add_event_dialog(
                parent.winfo_toplevel(),
                target,
                events_getter,
                events_setter,
                rebuild,
            ),
        )

    def bind_event_click(widget, event_obj):
        def on_click(_event, ev=event_obj):
            _open_event_details_dialog(parent.winfo_toplevel(), ev)
            return "break"

        widget.bind("<Button-1>", on_click)

    def bind_day_list_click(widget, day_date, day_events):
        def on_click(_event, target=day_date, events=day_events):
            _open_day_events_dialog(parent.winfo_toplevel(), target, events)
            return "break"

        widget.bind("<Button-1>", on_click)

    def rebuild():
        for child in grid_wrap.winfo_children():
            child.destroy()

        year = current["year"]
        month = current["month"]
        month_label.config(text=datetime(year, month, 1).strftime("%B %Y"))

        all_events = events_getter()
        if not isinstance(all_events, list):
            all_events = []

        events_by_day = {}
        for event in all_events:
            dt = parse_event_start(event)
            if dt is None:
                continue
            if dt.year != year or dt.month != month:
                continue
            events_by_day.setdefault(dt.day, []).append(event)

        for day in events_by_day:
            events_by_day[day].sort(key=lambda ev: parse_event_start(ev) or datetime.min)

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_row = tk.Frame(grid_wrap, bg=BG)
        header_row.pack(fill=tk.X, pady=(0, 6))

        for i, name in enumerate(weekdays):
            lbl = tk.Label(header_row, text=name, font=FONT_SUB, bg=BG, fg=ACCENT2)
            lbl.grid(row=0, column=i, sticky="nsew", padx=3)
            header_row.grid_columnconfigure(i, weight=1)

        cal = pycalendar.Calendar(firstweekday=0)
        weeks = cal.monthdayscalendar(year, month)

        body = tk.Frame(grid_wrap, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        for r, week in enumerate(weeks):
            body.grid_rowconfigure(r, weight=1)
            for c, day in enumerate(week):
                body.grid_columnconfigure(c, weight=1)
                cell_bg = CARD if day else PANEL
                cell_border = BORDER

                cell = tk.Frame(body, bg=cell_bg, highlightthickness=1, highlightbackground=cell_border)
                cell.bind('<Enter>', lambda e, w=cell: w.config(bg="#3456a1"))
                cell.bind('<Leave>', lambda e, w=cell, bg=cell_bg: w.config(bg=bg))
                cell.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
                cell.grid_propagate(False)

                if day == 0:
                    continue

                day_date = datetime(year, month, day).date()
                bind_day_click(cell, day_date)

                top = tk.Frame(cell, bg=cell_bg)
                top.pack(fill=tk.X, padx=6, pady=(6, 2))
                bind_day_click(top, day_date)

                day_lbl = tk.Label(top, text=str(day), font=FONT_LABEL, bg=cell_bg, fg=TEXT, anchor="w")
                day_lbl.pack(side=tk.LEFT)
                bind_day_click(day_lbl, day_date)

                add_lbl = tk.Label(top, text="+", font=("Segoe UI Semibold", 10), bg=cell_bg, fg=ACCENT2)
                add_lbl.pack(side=tk.RIGHT)
                bind_day_click(add_lbl, day_date)

                day_events = events_by_day.get(day, [])
                for idx, event in enumerate(day_events[:3]):
                    text = f"{format_event_time(event)}  {event.get('title', 'Event')}"
                    chip = tk.Label(
                        cell,
                        text=text,
                        font=("Segoe UI", 8),
                        bg="#23437e",
                        fg=TEXT,
                        anchor="w",
                        padx=5,
                        pady=2,
                    )
                    chip.pack(fill=tk.X, padx=6, pady=(0 if idx == 0 else 3, 0))
                    bind_event_click(chip, event)

                if len(day_events) > 3:
                    extra = tk.Label(
                        cell,
                        text=f"+{len(day_events) - 3} more",
                        font=("Segoe UI", 8),
                        bg=cell_bg,
                        fg=SUBTEXT,
                        anchor="w",
                    )
                    extra.pack(fill=tk.X, padx=6, pady=(3, 0))
                    bind_day_list_click(extra, day_date, day_events)

    prev_btn = tk.Button(
        nav,
        text="<",
        font=FONT_BTN,
        bg=PANEL,
        fg=TEXT,
        relief="flat",
        cursor="hand2",
        width=3,
        command=lambda: shift_month(-1),
    )
    prev_btn.pack(side=tk.LEFT, padx=(0, 4))

    next_btn = tk.Button(
        nav,
        text=">",
        font=FONT_BTN,
        bg=PANEL,
        fg=TEXT,
        relief="flat",
        cursor="hand2",
        width=3,
        command=lambda: shift_month(1),
    )
    next_btn.pack(side=tk.LEFT)

    rebuild()
    return rebuild


def open_settings_window(
    t,
    get_saved_settings,
    get_audio_inputs,
    settings: dict,
    save_callback,
    setting_actions=None,
    initial_tab="settings",
    extra_tabs=None,
    get_calendar_events=None,
    set_calendar_events=None,
):
    saved = get_saved_settings()
    _resolve_theme(saved)

    if get_calendar_events is None:
        get_calendar_events = lambda: []
    if set_calendar_events is None:
        set_calendar_events = lambda events: None

    window = tk.Tk()
    window.title("Control Panel")

    width = 940
    height = 760
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = max(16, (screen_w - width) // 2)
    y = max(16, (screen_h - height) // 3)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.configure(bg=BG)
    window.resizable(True, True)

    def start_move(event):
        window.x = event.x
        window.y = event.y

    def do_move(event):
        deltax = event.x - window.x
        deltay = event.y - window.y
        next_x = window.winfo_x() + deltax
        next_y = window.winfo_y() + deltay
        window.geometry(f"+{next_x}+{next_y}")

    window.bind("<Button-1>", start_move)
    window.bind("<B1-Motion>", do_move)

    title_bar = tk.Frame(window, bg=PANEL, height=52)
    title_bar.pack(fill=tk.X)
    title_bar.pack_propagate(False)

    title_label = tk.Label(title_bar, text="CONTROL PANEL", font=FONT_TITLE, bg=PANEL, fg=ACCENT)
    title_label.pack(side=tk.LEFT, padx=20)
    tk.Frame(window, bg=ACCENT, height=2).pack(fill=tk.X)

    tab_bar = tk.Frame(window, bg=BG, height=44)
    tab_bar.pack(fill=tk.X, padx=12, pady=(8, 4))
    tab_bar.pack_propagate(False)

    content = tk.Frame(window, bg=BG)
    content.pack(fill=tk.BOTH, expand=True)

    tab_defs = []

    def build_settings_tab(parent):
        body = tk.Frame(parent, bg=BG)
        body.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(body, bg=BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(
            body,
            orient="vertical",
            command=canvas.yview,
            bg=PANEL,
            troughcolor=BG,
            activebackground=ACCENT,
            relief="flat",
            width=10,
        )

        scroll_frame = tk.Frame(canvas, bg=BG)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        scroll_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def resize_scroll_content(event):
            canvas.itemconfigure(scroll_window, width=event.width)

        canvas.bind("<Configure>", resize_scroll_content)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * e.delta / 120), "units"))

        setting_vars = {}
        spotify_devices_live = dict(saved.get("spotify_devices", {}))
        current_section = [None]
        spotify_default_var = None
        spotify_default_combo = None

        def refresh_default_spotify_options():
            if spotify_default_combo is None or spotify_default_var is None:
                return

            options = list(spotify_devices_live.keys())
            spotify_default_combo["values"] = options
            current_value = spotify_default_var.get()
            if current_value in options:
                return
            spotify_default_var.set(options[0] if options else "")

        for key, setting in settings.items():
            if setting.get("hidden"):
                continue

            label_text = t(key)
            raw_desc = t(key + "_description")
            desc_text = raw_desc if raw_desc != key + "_description" else None

            sec = setting.get("section")
            if sec and sec != current_section[0]:
                section_header(scroll_frame, sec)
                current_section[0] = sec

            s_type = setting["type"]

            if s_type == "checkbox":
                var = tk.BooleanVar(value=saved.get(key, False))
                make_checkbox(scroll_frame, label_text, desc_text, var)
                setting_vars[key] = var

            elif s_type == "dropdown":
                if key == "spotify_devices":
                    selected_var = make_spotify_devices_widget(
                        scroll_frame,
                        label_text,
                        desc_text,
                        spotify_devices_live,
                        on_change=refresh_default_spotify_options,
                    )
                    setting_vars[key] = selected_var

                elif key == "default_spotify_device":
                    options = list(spotify_devices_live.keys())
                    spotify_default_var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                    spotify_default_combo = make_dropdown(
                        scroll_frame,
                        label_text,
                        desc_text,
                        spotify_default_var,
                        options,
                    )
                    setting_vars[key] = spotify_default_var

                elif key == "microphone_input":
                    options = [d["name"] for d in get_audio_inputs()]
                    var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                    make_dropdown(scroll_frame, label_text, desc_text, var, options)
                    setting_vars[key] = var

                else:
                    options = setting.get("options", [])
                    var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                    make_dropdown(scroll_frame, label_text, desc_text, var, options)
                    setting_vars[key] = var

            elif s_type == "button":
                action = (setting_actions or {}).get(key)
                make_action_button(scroll_frame, setting.get("name", label_text), on_click=action)

            elif s_type == "text":
                default_value = setting.get("default", "")
                var = tk.StringVar(value=str(saved.get(key, default_value)))
                make_text_input(scroll_frame, label_text, desc_text, var)
                setting_vars[key] = var

        def on_save():
            data = {}
            for k, v in setting_vars.items():
                if k == "spotify_devices":
                    data[k] = dict(spotify_devices_live)
                else:
                    data[k] = v.get()
            window.destroy()
            save_callback(data)

        tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill=tk.X, pady=(16, 0), padx=16)

        save_wrap = tk.Frame(scroll_frame, bg=BG)
        save_wrap.pack(fill=tk.X, pady=20, padx=16)
        save_btn = tk.Button(
            save_wrap,
            text="SAVE SETTINGS",
            command=on_save,
            font=FONT_BTN,
            bg=ACCENT,
            fg="#ffffff",
            activebackground="#3b78ef",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=10,
        )
        save_btn.pack(fill=tk.X)
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#3b78ef"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=ACCENT))
        return None

    tab_defs.append(
        {
            "key": "settings",
            "title": "Settings",
            "build": build_settings_tab,
        }
    )

    tab_defs.append(
        {
            "key": "schedule",
            "title": "Schedule",
            "build": lambda parent: _build_schedule_tab(parent, get_calendar_events, set_calendar_events),
        }
    )

    if isinstance(extra_tabs, list):
        for tab in extra_tabs:
            if not isinstance(tab, dict):
                continue
            if not tab.get("key") or not tab.get("title") or not callable(tab.get("build")):
                continue
            tab_defs.append(tab)

    tab_buttons = {}
    tab_frames = {}
    tab_refresh = {}
    active_tab = {"key": None}

    def set_tab_button_style(key, is_active):
        btn = tab_buttons.get(key)
        if btn is None:
            return
        if is_active:
            btn.config(bg=ACCENT, fg="#ffffff")
        else:
            btn.config(bg=PANEL, fg=SUBTEXT)

    def show_tab(key):
        if key not in tab_frames:
            return

        for tab_key, frame in tab_frames.items():
            if tab_key == key:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()
            set_tab_button_style(tab_key, tab_key == key)

        active_tab["key"] = key
        refresh = tab_refresh.get(key)
        if callable(refresh):
            refresh()

    for index, tab in enumerate(tab_defs):
        key = tab["key"]
        title = tab["title"]

        btn = tk.Button(
            tab_bar,
            text=title,
            font=FONT_BTN,
            bg=PANEL,
            fg=SUBTEXT,
            activebackground=ACCENT,
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=6,
            command=lambda tab_key=key: show_tab(tab_key),
        )
        btn.pack(side=tk.LEFT, padx=(0 if index == 0 else 8, 0))
        tab_buttons[key] = btn

        frame = tk.Frame(content, bg=BG)
        tab_frames[key] = frame
        refresh_hook = tab["build"](frame)
        tab_refresh[key] = refresh_hook

    if initial_tab not in tab_frames:
        initial_tab = "settings"
    show_tab(initial_tab)

    window.mainloop()


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))