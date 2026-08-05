#~main ui

import tkinter as tk
from tkinter import colorchooser, ttk
from tkinter.scrolledtext import ScrolledText

import importlib
import importlib.util
import traceback
import os
import sys
import subprocess
import re
import getpass
import time
import threading

from PIL import Image
import pystray

from settings import load_settings, save_settings

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


class Terminal:

    VERSION = "5.0"


    def __init__(self, root):

        self.root = root

        self.settings = load_settings()

        self.username = getpass.getuser()

        self.cwd = os.getcwd()

        self.history = []

        self.history_index = 0

        self.aliases = {}

        self.variables = {}

        self.running_command = False

        self.current_process = None

        self.tray = None

        self.hidden = False


        self.setup_window()

        self.setup_menu()

        self.setup_ui()

        self.setup_tray()


        self.write(
            f"Poly Terminal {self.VERSION}",
            False
        )

        self.write(
            f"Welcome {self.username}",
            False
        )

        self.write(
            "Type 'help' for commands.",
            False
        )

        self.write(
            "",
            False
        )



    #~window

    def setup_window(self):

        self.root.title(
            "Python Terminal"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.configure(
            bg="#0d1117"
        )


        #~custom logo

        try:

            self.logo = tk.PhotoImage(
                file="logo.png"
            )

            self.root.iconphoto(
                True,
                self.logo
            )

        except Exception:

            self.logo = None



        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.hide_window
        )



    #~sys tray

    def setup_tray(self):

        def tray_thread():

            try:

                if os.path.exists(
                    "logo.png"
                ):

                    image = Image.open(
                        "logo.png"
                    )

                else:

                    image = Image.new(
                        "RGB",
                        (64,64),
                        "black"
                    )


                menu = pystray.Menu(

                    pystray.MenuItem(
                        "Show",
                        self.show_window
                    ),

                    pystray.MenuItem(
                        "Hide",
                        self.hide_window
                    ),

                    pystray.MenuItem(
                        "Exit",
                        self.exit_app
                    )

                )


                self.tray = pystray.Icon(

                    "Python Terminal",

                    image,

                    "Python Terminal",

                    menu

                )


                self.tray.run()


            except Exception as e:

                print(
                    "Tray error:",
                    e
                )



        threading.Thread(

            target=tray_thread,

            daemon=True

        ).start()



    def hide_window(self):

        self.hidden = True

        self.root.withdraw()



    def show_window(self):

        self.hidden = False

        self.root.after(

            0,

            self.root.deiconify

        )


    def exit_app(self):

        if self.tray:

            self.tray.stop()


        self.root.destroy()

        
    #~menu

    def setup_menu(self):

        menu = tk.Menu(
            self.root
        )

        self.root.config(
            menu=menu
        )


        terminal = tk.Menu(
            menu,
            tearoff=False
        )


        terminal.add_command(
            label="Settings",
            command=self.open_settings
        )


        terminal.add_command(
            label="Clear",
            command=self.clear
        )


        terminal.add_separator()


        terminal.add_command(
            label="Minimise",
            command=self.hide_window
        )


        terminal.add_command(
            label="Exit",
            command=self.exit_app
        )


        menu.add_cascade(
            label="Terminal",
            menu=terminal
        )



    #~ui

    def setup_ui(self):

        main = tk.Frame(
            self.root,
            bg="#0d1117"
        )


        main.pack(
            fill=tk.BOTH,
            expand=True,
            padx=12,
            pady=12
        )


        self.output = ScrolledText(

            main,

            bg=self.settings.get(
                "background",
                "#050505"
            ),

            fg=self.settings.get(
                "foreground",
                "#ffffff"
            ),

            insertbackground=self.settings.get(
                "cursor",
                "#58a6ff"
            ),

            font=(

                self.settings.get(
                    "font",
                    "Cascadia Mono"
                ),

                self.settings.get(
                    "font_size",
                    12
                )

            ),

            borderwidth=0,

            highlightthickness=0,

            padx=15,

            pady=15,

            state="disabled"

        )


        self.output.pack(
            fill=tk.BOTH,
            expand=True
        )



        bar = tk.Frame(

            main,

            bg="#0d1117"

        )


        bar.pack(

            fill=tk.X,

            pady=10

        )



        self.prompt = tk.Label(

            bar,

            bg="#0d1117",

            fg="#58a6ff",

            font=(

                "Cascadia Mono",

                12

            )

        )


        self.prompt.pack(

            side=tk.LEFT

        )



        self.entry = tk.Entry(

            bar,

            bg="#161b22",

            fg="white",

            insertbackground=self.settings.get(

                "cursor",

                "#58a6ff"

            ),

            relief="flat",

            font=(

                "Cascadia Mono",

                12

            )

        )


        self.entry.pack(

            side=tk.LEFT,

            fill=tk.X,

            expand=True,

            padx=10,

            ipady=8

        )



        self.entry.bind(

            "<Return>",

            self.execute

        )


        self.entry.bind(

            "<Up>",

            self.history_up

        )


        self.entry.bind(

            "<Down>",

            self.history_down

        )


        self.root.bind(

            "<Alt_L>",

            self.stop_command

        )



        self.entry.focus()



        self.status = tk.Label(

            self.root,

            bg="#161b22",

            fg="#8b949e",

            anchor="w",

            padx=10

        )


        self.status.pack(

            fill=tk.X,

            side=tk.BOTTOM

        )


        self.update_prompt()

        self.update_status()



    #~prompt

    def update_prompt(self):

        folder = os.path.basename(
            self.cwd
        )


        self.prompt.config(

            text=f"{self.username}@terminal:~/{folder} ❯"

        )

    #~output

    def write(self, text, delay=None):

        text = ANSI_ESCAPE.sub('', str(text))

        self.output.config(
            state="normal"
        )


        if delay is None:

            delay = self.settings.get(
                "slow_type",
                True
            )


        speed = self.settings.get(
            "typing_speed",
            0.01
        )


        for line in str(text).split("\n"):


            if delay:

                for char in line:


                    if not self.running_command:

                        break


                    self.output.insert(
                        tk.END,
                        char
                    )


                    self.output.see(
                        tk.END
                    )


                    self.root.update()


                    time.sleep(
                        speed
                    )


            else:

                self.output.insert(
                    tk.END,
                    line
                )


            self.output.insert(
                tk.END,
                "\n"
            )


        self.output.see(
            tk.END
        )


        self.output.config(
            state="disabled"
        )



    def clear(self):

        self.output.config(
            state="normal"
        )


        self.output.delete(
            "1.0",
            tk.END
        )


        self.output.config(
            state="disabled"
        )



    #~interupt system

    def stop_command(self, event=None):

        if hasattr(self, "current_process") and self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass
            self.current_process = None

        if self.running_command:

            self.running_command = False

            self.write(
                "^C Command stopped",
                False
            )

        return "break"



    #~cmd system

    def execute(self, event=None):

        raw_input = self.entry.get()

        if not raw_input.strip() and not (self.running_command and hasattr(self, "current_process") and self.current_process):
            return

        # handle interactive stdin routing to active process
        if self.running_command and hasattr(self, "current_process") and self.current_process and self.current_process.poll() is None:
            self.entry.delete(0, tk.END)
            self.write(raw_input, False)
            try:
                if self.current_process.stdin:
                    self.current_process.stdin.write(raw_input + "\n")
                    self.current_process.stdin.flush()
            except Exception as e:
                self.write(f"Stdin error: {e}", False)
            return

        command = raw_input.strip()

        self.history.append(
            command
        )

        self.history_index = len(
            self.history
        )

        self.entry.delete(
            0,
            tk.END
        )

        self.running_command = True

        self.write(
            f"$ {command}",
            False
        )

        threading.Thread(
            target=self.run,
            args=(command,),
            daemon=True
        ).start()



    def get_commands_dirs(self):
        dirs = []
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        ext_cmds = os.path.join(base_dir, "commands")
        if os.path.isdir(ext_cmds):
            dirs.append(ext_cmds)

        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            bundle_cmds = os.path.join(sys._MEIPASS, "commands")
            if os.path.isdir(bundle_cmds) and bundle_cmds not in dirs:
                dirs.append(bundle_cmds)

        cwd_cmds = os.path.join(self.cwd, "commands")
        if os.path.isdir(cwd_cmds) and cwd_cmds not in dirs:
            dirs.append(cwd_cmds)

        return dirs



    def find_custom_command(self, cmd_name):
        dirs = self.get_commands_dirs()
        filename = f"{cmd_name.lower()}.py"
        for d in dirs:
            filepath = os.path.join(d, filename)
            if os.path.isfile(filepath):
                return filepath
        return None



    def run(self, command):

        parts = command.split()

        if not parts:
            self.running_command = False
            return

        cmd = parts[0].lower()
        args = parts[1:]

        filepath = self.find_custom_command(cmd)

        if filepath:
            try:
                spec = importlib.util.spec_from_file_location(f"custom_cmd_{cmd}", filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.run(self, args)
                return
            except Exception:
                self.write(traceback.format_exc(), False)
                return
            finally:
                self.running_command = False
                self.update_prompt()
                self.update_status()

        try:
            module = importlib.import_module(
                f"commands.{cmd}"
            )
            importlib.reload(module)
            module.run(self, args)
            return
        except ModuleNotFoundError:
            pass
        except Exception:
            self.write(traceback.format_exc(), False)
            self.running_command = False
            self.update_prompt()
            self.update_status()
            return
        finally:
            if not self.running_command:
                self.update_prompt()
                self.update_status()

        self.run_system_command(command)



    def run_system_command(self, command):

        cwd = self.cwd if os.path.exists(self.cwd) else os.getcwd()
        env = os.environ.copy()

        try:
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            while self.running_command and self.current_process:
                line = self.current_process.stdout.readline()
                if not line:
                    break
                self.write(line.rstrip("\r\n"), delay=False)

            if self.current_process:
                self.current_process.wait()

        except Exception as e:
            self.write(f"System execution error: {e}", delay=False)

        finally:
            self.current_process = None
            self.running_command = False
            self.update_prompt()
            self.update_status()



    #~history

    def history_up(self,event):

        if not self.history:

            return


        self.history_index = max(

            0,

            self.history_index - 1

        )


        self.entry.delete(

            0,

            tk.END

        )


        self.entry.insert(

            0,

            self.history[

                self.history_index

            ]

        )



    def history_down(self,event):

        if not self.history:

            return


        self.history_index = min(

            len(self.history),

            self.history_index + 1

        )


        self.entry.delete(

            0,

            tk.END

        )



    #~status

    def update_status(self):

        self.status.config(

            text=f"Python Terminal {self.VERSION} | {self.cwd}"

        )

    #~rounded edges

    def rounded_button(self, parent, text, command):

        canvas = tk.Canvas(

            parent,

            width=260,

            height=50,

            bg="#0d1117",

            highlightthickness=0

        )


        canvas.pack(
            pady=8
        )


        normal = "#21262d"

        hover = "#30363d"



        left = canvas.create_oval(

            0,

            0,

            50,

            50,

            fill=normal,

            outline=""

        )


        right = canvas.create_oval(

            210,

            0,

            260,

            50,

            fill=normal,

            outline=""

        )


        middle = canvas.create_rectangle(

            25,

            0,

            235,

            50,

            fill=normal,

            outline=""

        )


        label = canvas.create_text(

            130,

            25,

            text=text,

            fill="white",

            font=(

                "Cascadia Mono",

                11

            )

        )


        def enter(event):

            for item in (
                left,
                right,
                middle
            ):

                canvas.itemconfig(

                    item,

                    fill=hover

                )


            canvas.itemconfig(

                label,

                fill="#58a6ff"

            )



        def leave(event):

            for item in (
                left,
                right,
                middle
            ):

                canvas.itemconfig(

                    item,

                    fill=normal

                )


            canvas.itemconfig(

                label,

                fill="white"

            )



        def click(event):

            command()



        canvas.bind(

            "<Enter>",

            enter

        )


        canvas.bind(

            "<Leave>",

            leave

        )


        canvas.bind(

            "<Button-1>",

            click

        )


        return canvas




    #~settings window

    def open_settings(self):

        window = tk.Toplevel(

            self.root

        )


        window.title(

            "Terminal Settings"

        )


        window.geometry(

            "520x600"

        )


        window.configure(

            bg="#0d1117"

        )



        tk.Label(

            window,

            text="Terminal Settings",

            bg="#0d1117",

            fg="white",

            font=(

                "Cascadia Mono",

                16

            )

        ).pack(

            pady=20

        )


        #~theme system


        theme = tk.LabelFrame(

            window,

            text="Theme",

            bg="#0d1117",

            fg="white",

            padx=10,

            pady=10

        )


        theme.pack(

            fill="x",

            padx=20,

            pady=10

        )



        def choose_color(setting):

            colour = colorchooser.askcolor()[1]


            if colour:

                self.settings[setting] = colour


                self.apply_theme()



        self.rounded_button(

            theme,

            "Background Colour",

            lambda:

            choose_color(
                "background"
            )

        )


        self.rounded_button(

            theme,

            "Text Colour",

            lambda:

            choose_color(
                "foreground"
            )

        )


        self.rounded_button(

            theme,

            "Cursor Colour",

            lambda:

            choose_color(
                "cursor"
            )

        )



        #~typing


        typing = tk.LabelFrame(

            window,

            text="Typing Effect",

            bg="#0d1117",

            fg="white",

            padx=10,

            pady=10

        )


        typing.pack(

            fill="x",

            padx=20,

            pady=10

        )



        slow = tk.BooleanVar(

            value=self.settings.get(

                "slow_type",

                True

            )

        )



        tk.Checkbutton(

            typing,

            text="Enable slow typing",

            variable=slow,

            bg="#0d1117",

            fg="white",

            selectcolor="#161b22"

        ).pack(

            pady=10

        )



        tk.Label(

            typing,

            text="Typing Speed",

            bg="#0d1117",

            fg="white"

        ).pack()



        speed = ttk.Scale(

            typing,

            from_=0.001,

            to=0.1,

            value=self.settings.get(

                "typing_speed",

                0.01

            )

        )


        speed.pack(

            fill="x",

            padx=20,

            pady=10

        )


        #~save

        def save():

            self.settings["slow_type"] = slow.get()


            self.settings["typing_speed"] = speed.get()


            save_settings(

                self.settings

            )


            self.apply_theme()


            window.destroy()



        self.rounded_button(

            window,

            "Save Settings",

            save

        )




    #~apply theme

    def apply_theme(self):

        self.output.configure(

            bg=self.settings.get(

                "background",

                "#050505"

            ),

            fg=self.settings.get(

                "foreground",

                "#ffffff"

            )

        )


        self.entry.configure(

            bg=self.settings.get(

                "background",

                "#161b22"

            ),

            fg=self.settings.get(

                "foreground",

                "#ffffff"

            ),

            insertbackground=self.settings.get(

                "cursor",

                "#58a6ff"

            )

        )


        self.prompt.configure(

            fg=self.settings.get(

                "cursor",

                "#58a6ff"

            )

        )


        save_settings(

            self.settings

        )

    #~shutdown

    def close(self):

        save_settings(
            self.settings
        )


        if self.tray:

            try:

                self.tray.stop()

            except:

                pass


        self.root.destroy()



    #~reload settings


    def reload_settings(self):

        self.settings = load_settings()

        self.apply_theme()


#-im pretty sure we scrapped this for the winUI version but still cool if yall wanna steal this code lol

#-script written by soliale
#-https://github.com/soliale