import tkinter as tk
from tkinter import ttk

# ── Palette ────────────────────────────────────────────────────────────────────
BG      = "#0d0e1c"
PANEL   = "#13152a"
CARD    = "#1a1d35"
ACCENT  = "#5b7fff"
ACCENT2 = "#a78bfa"
TEXT    = "#e4e6f0"
SUBTEXT = "#6b7096"
BORDER  = "#252840"

FONT_TITLE = ("Courier New", 13, "bold")
FONT_LABEL = ("Courier New", 10, "bold")
FONT_SUB   = ("Courier New", 9)
FONT_BTN   = ("Courier New", 10, "bold")


# ── Internal helpers ───────────────────────────────────────────────────────────

def _section_header(parent, text):
    f = tk.Frame(parent, bg=BG)
    f.pack(fill=tk.X, pady=(16, 4), padx=4)
    tk.Label(f, text=text.upper(), font=("Courier New", 8, "bold"),
             bg=BG, fg=ACCENT2).pack(side=tk.LEFT, padx=4)
    tk.Frame(f, bg=BORDER, height=1).pack(side=tk.LEFT, fill=tk.X,
                                           expand=True, padx=(6, 4))


def _make_checkbox(parent, title, description, var):
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

def _make_dropdown(parent, title, description, var, options):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    tk.Label(row, text=title, font=FONT_LABEL, bg=CARD, fg=TEXT, anchor="w").pack(fill=tk.X)
    if description:
        tk.Label(row, text=description, font=FONT_SUB, bg=CARD, fg=SUBTEXT, anchor="w").pack(fill=tk.X)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("S.TCombobox",
                    fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground=TEXT, arrowcolor=ACCENT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    style.map("S.TCombobox", fieldbackground=[("readonly", PANEL)])

    combo = ttk.Combobox(row, textvariable=var, values=options,
                          state="readonly", style="S.TCombobox", font=FONT_SUB)
    combo.pack(fill=tk.X, pady=(6, 0))

def _make_action_button(parent, label):
    row = tk.Frame(parent, bg=CARD, padx=16, pady=10)
    row.pack(fill=tk.X, pady=(0, 2))

    btn = tk.Button(row, text=label, font=FONT_BTN,
                     bg=PANEL, fg=ACCENT, activebackground=ACCENT,
                     activeforeground=TEXT, relief="flat", cursor="hand2", pady=6)
    btn.pack(fill=tk.X)
    btn.bind("<Enter>", lambda e: btn.config(bg=ACCENT, fg=TEXT))
    btn.bind("<Leave>", lambda e: btn.config(bg=PANEL, fg=ACCENT))
    return btn


def _make_spotify_devices_widget(parent, title, description, devices_dict, on_change):
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
    style.configure("S.TCombobox",
                    fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, selectbackground=ACCENT,
                    selectforeground=TEXT, arrowcolor=ACCENT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
    style.map("S.TCombobox", fieldbackground=[("readonly", PANEL)])

    combo = ttk.Combobox(dd_row, textvariable=selected_var,
                         state="readonly", style="S.TCombobox", font=FONT_SUB)
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
            _refresh_real_name_hint()

    del_btn = tk.Button(dd_row, text="✕  Remove", font=FONT_SUB,
                        bg=PANEL, fg="#ff4d6d",
                        activebackground="#ff4d6d", activeforeground=TEXT,
                        relief="flat", cursor="hand2", padx=10, pady=4,
                        command=delete_selected)
    del_btn.pack(side=tk.RIGHT)
    del_btn.bind("<Enter>", lambda e: del_btn.config(bg="#ff4d6d", fg=TEXT))
    del_btn.bind("<Leave>", lambda e: del_btn.config(bg=PANEL, fg="#ff4d6d"))

    hint_var = tk.StringVar()
    hint_label = tk.Label(outer, textvariable=hint_var, font=FONT_SUB,
                          bg=CARD, fg=SUBTEXT, anchor="w")
    hint_label.pack(fill=tk.X, pady=(2, 0))

    def _refresh_real_name_hint(*_):
        alias = selected_var.get()
        if alias and alias in devices_dict:
            hint_var.set(f"  → real name: {devices_dict[alias]}")
        else:
            hint_var.set("")

    selected_var.trace_add("write", _refresh_real_name_hint)
    _refresh_real_name_hint()

    tk.Frame(outer, bg=BORDER, height=1).pack(fill=tk.X, pady=(12, 8))

    tk.Label(outer, text="ADD NEW DEVICE", font=("Courier New", 8, "bold"),
             bg=CARD, fg=ACCENT2, anchor="w").pack(fill=tk.X, pady=(0, 6))

    alias_var    = tk.StringVar()
    realname_var = tk.StringVar()
    error_var    = tk.StringVar()

    def _styled_entry(parent_frame, textvar, placeholder):
        e = tk.Entry(parent_frame, textvariable=textvar,
                     font=FONT_SUB, bg=PANEL, fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT)
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
        e.bind("<FocusIn>",  _on_focus_in)
        e.bind("<FocusOut>", _on_focus_out)
        return e

    PLACEHOLDER_ALIAS    = "Internal name (e.g. Living Room)"
    PLACEHOLDER_REALNAME = "Real device name (e.g. Sonos Era 100)"

    _styled_entry(outer, alias_var,    PLACEHOLDER_ALIAS)
    _styled_entry(outer, realname_var, PLACEHOLDER_REALNAME)

    error_label = tk.Label(outer, textvariable=error_var, font=FONT_SUB,
                            bg=CARD, fg="#ff4d6d", anchor="w")
    error_label.pack(fill=tk.X)

    def add_device():
        alias    = alias_var.get().strip()
        realname = realname_var.get().strip()

        if not alias or alias == PLACEHOLDER_ALIAS:
            error_var.set("⚠  Internal name is required.")
            return
        if not realname or realname == PLACEHOLDER_REALNAME:
            error_var.set("⚠  Real device name is required.")
            return
        if alias in devices_dict:
            error_var.set(f"⚠  '{alias}' already exists.")
            return

        error_var.set("")
        devices_dict[alias] = realname
        refresh_combo()
        selected_var.set(alias)
        on_change()

        # Reset form
        alias_var.set(PLACEHOLDER_ALIAS)
        realname_var.set(PLACEHOLDER_REALNAME)

    add_btn = tk.Button(outer, text="＋  Add Device", font=FONT_BTN,
                         bg=ACCENT, fg="#ffffff",
                         activebackground="#6b8fff", activeforeground="#ffffff",
                         relief="flat", cursor="hand2", pady=6,
                         command=add_device)
    add_btn.pack(fill=tk.X, pady=(6, 0))
    add_btn.bind("<Enter>", lambda e: add_btn.config(bg="#6b8fff"))
    add_btn.bind("<Leave>", lambda e: add_btn.config(bg=ACCENT))

    return selected_var


def open_settings_window(t, get_saved_settings, get_audio_inputs, settings: dict, save_callback):
    saved = get_saved_settings()

    window = tk.Tk()
    window.title("Settings")
    window.overrideredirect(True)
    window.geometry("700x640")
    window.configure(bg=BG)
    window.resizable(True, True)

    def start_move(event):
        window.x = event.x
        window.y = event.y
    def do_move(event):
        deltax = event.x - window.x
        deltay = event.y - window.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")
    window.bind("<Button-1>", start_move)
    window.bind("<B1-Motion>", do_move)

    # ── Title bar ──────────────────────────────────────────────────────────────
    title_bar = tk.Frame(window, bg=PANEL, height=52)
    title_bar.pack(fill=tk.X)
    title_bar.pack_propagate(False)

    tk.Label(title_bar, text="⚙  SETTINGS", font=FONT_TITLE,
             bg=PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=20)

    close_btn = tk.Button(title_bar, text="✕", font=("Courier New", 12),
        bg=PANEL, fg=SUBTEXT, activebackground="#ff4d6d",
        activeforeground=TEXT, relief="flat",
        cursor="hand2", command=window.destroy, padx=12)
    close_btn.pack(side=tk.RIGHT)
    close_btn.bind("<Enter>", lambda e: close_btn.config(fg=TEXT, bg="#ff4d6d"))
    close_btn.bind("<Leave>", lambda e: close_btn.config(fg=SUBTEXT, bg=PANEL))

    tk.Frame(window, bg=ACCENT, height=2).pack(fill=tk.X)

    # ── Scrollable body ────────────────────────────────────────────────────────
    body = tk.Frame(window, bg=BG)
    body.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(body, bg=BG, highlightthickness=0, bd=0)
    scrollbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview,
                              bg=PANEL, troughcolor=PANEL,
                              activebackground=ACCENT)

    scroll_frame = tk.Frame(canvas, bg=BG)
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(int(-1 * e.delta / 120), "units"))

    setting_vars = {}
    spotify_devices_live = dict(saved.get("spotify_devices", {}))
    current_section = [None]

    for key, setting in settings.items():
        if setting.get("hidden"):
            continue

        label_text = t(key)
        raw_desc   = t(key + "_description")
        desc_text  = raw_desc if raw_desc != key + "_description" else None

        sec = setting.get("section")
        if sec and sec != current_section[0]:
            _section_header(scroll_frame, sec)
            current_section[0] = sec

        s_type = setting["type"]

        if s_type == "checkbox":
            var = tk.BooleanVar(value=saved.get(key, False))
            _make_checkbox(scroll_frame, label_text, desc_text, var)
            setting_vars[key] = var

        elif s_type == "dropdown":
            if key == "spotify_devices":
                selected_var = _make_spotify_devices_widget(
                    scroll_frame,
                    label_text,
                    desc_text,
                    spotify_devices_live,
                    on_change=lambda: None,
                )
                setting_vars[key] = selected_var

            elif key == "microphone_input":
                options = [d["name"] for d in get_audio_inputs()]
                var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                _make_dropdown(scroll_frame, label_text, desc_text, var, options)
                setting_vars[key] = var

            else:
                options = setting.get("options", [])
                var = tk.StringVar(value=saved.get(key, options[0] if options else ""))
                _make_dropdown(scroll_frame, label_text, desc_text, var, options)
                setting_vars[key] = var

        elif s_type == "button":
            _make_action_button(scroll_frame, setting.get("name", label_text))

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
    save_btn = tk.Button(save_wrap, text="SAVE SETTINGS", command=on_save,
                          font=FONT_BTN, bg=ACCENT, fg="#ffffff",
                          activebackground="#6b8fff", activeforeground="#ffffff",
                          relief="flat", cursor="hand2", pady=10)
    save_btn.pack(fill=tk.X)
    save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#6b8fff"))
    save_btn.bind("<Leave>", lambda e: save_btn.config(bg=ACCENT))

    window.mainloop()