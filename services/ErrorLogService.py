import os
import datetime
import threading
import traceback


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'data', 'logs')


def get_log_path(day=None):
    day = day or datetime.datetime.now()
    os.makedirs(LOGS_DIR, exist_ok=True)
    return os.path.join(LOGS_DIR, f"{day.strftime('%Y-%m-%d')}.log")


def _write_log(level, title, description="", error_type=None):
    now = datetime.datetime.now().astimezone()
    line_parts = [
        now.strftime('%Y-%m-%d %H:%M:%S%z'),
        level,
    ]

    if error_type:
        line_parts.append(str(error_type))

    if title:
        line_parts.append(str(title))

    line = " | ".join(line_parts)
    if description:
        description = str(description).strip()
        if description:
            line = f"{line}\n{description}"

    with open(get_log_path(now), 'a', encoding='utf-8') as log_file:
        log_file.write(line + "\n\n")


def add_log_entry(title="", description="", error_type=None, level="ERROR"):
    _write_log(level=level, title=title, description=description, error_type=error_type)


def add_info_log(title="", description=""):
    _write_log(level="INFO", title=title, description=description)


def install_exception_hooks():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            return

        add_log_entry(
            title="Uncaught exception",
            description="".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
            error_type=getattr(exc_type, '__name__', str(exc_type)),
        )

    def handle_thread_exception(args):
        add_log_entry(
            title=f"Uncaught thread exception in {args.thread.name}",
            description="".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)),
            error_type=getattr(args.exc_type, '__name__', str(args.exc_type)),
        )

    import sys

    sys.excepthook = handle_exception
    threading.excepthook = handle_thread_exception
