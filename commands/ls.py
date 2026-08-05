#~ls

import os
import datetime


def human_size(size):
    """convert bytes into KB, MB, GB..."""

    units = ["B", "KB", "MB", "GB", "TB"]

    index = 0

    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1

    if index == 0:
        return f"{int(size)} {units[index]}"

    return f"{size:.1f} {units[index]}"


def run(term, args):

    show_hidden = False
    long_view = False
    target = term.cwd

    #~parse
    for arg in args:

        if arg.startswith("-"):

            if "a" in arg:
                show_hidden = True

            if "l" in arg:
                long_view = True

        else:

            target = os.path.abspath(
                os.path.join(term.cwd, arg)
            )

    #~validate dir

    if not os.path.exists(target):
        term.write(f"ls: '{target}' does not exist")
        return

    if not os.path.isdir(target):
        term.write(f"ls: '{target}' is not a directory")
        return

    #~pull dir components 

    try:

        entries = sorted(
            os.listdir(target),
            key=str.lower
        )

    except Exception as e:

        term.write(str(e))
        return

    if not entries:
        term.write("(empty)")
        return

    #~print entries

    for item in entries:

        if not show_hidden and item.startswith("."):
            continue

        full = os.path.join(target, item)

        is_dir = os.path.isdir(full)

        icon = "📁" if is_dir else "📄"

        if long_view:

            stat = os.stat(full)

            size = human_size(stat.st_size)

            modified = datetime.datetime.fromtimestamp(
                stat.st_mtime
            ).strftime("%Y-%m-%d %H:%M")

            term.write(
                f"{icon}  {size:>8}   {modified}   {item}"
            )

        else:

            term.write(f"{icon} {item}")