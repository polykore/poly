import os
import sys
import shutil
import time
import threading
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk

# set dark theme n appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# smooth typography font constants
FONT_FAMILY = "Segoe UI Variable Display" if os.name == "nt" else "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 12, "normal")
FONT_BUTTON = (FONT_FAMILY, 13, "bold")

class PolyInstallerApp(ctk.CTk):
    def __init__(self, payload_dir=None):
        super().__init__()

        # frameless n unmovable borderless setup wizard
        self.overrideredirect(True)
        self.geometry("660x460")

        # center window on primary screen
        self.center_window(660, 460)

        # set initial window opacity for smooth fade-in
        self.attributes("-alpha", 0.0)

        # resolve paths for standalone exe packaging (sys._MEIPASS)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        if payload_dir and os.path.exists(payload_dir):
            self.payload_dir = payload_dir
        else:
            self.payload_dir = os.path.join(self.base_dir, "dist", "PolyTerminal")
            if not os.path.exists(self.payload_dir):
                self.payload_dir = os.path.join(self.base_dir, "bin", "Release")

        default_install_path = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "Programs", "PolyTerminal")
        self.install_dir_var = tk.StringVar(value=default_install_path)

        self.create_desktop_shortcut_var = tk.BooleanVar(value=True)
        self.create_start_menu_var = tk.BooleanVar(value=True)
        self.add_to_path_var = tk.BooleanVar(value=True)
        self.launch_after_install_var = tk.BooleanVar(value=True)

        self._current_progress = 0.0
        self._target_progress = 0.0

        self.setup_ui()

        # trigger smooth fade-in window animation
        self.after(20, self.animate_fade_in)

    def center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def animate_fade_in(self, alpha=0.0):
        if alpha < 1.0:
            alpha += 0.08
            if alpha > 1.0:
                alpha = 1.0
            self.attributes("-alpha", alpha)
            self.after(15, lambda: self.animate_fade_in(alpha))

    def animate_fade_out(self, callback):
        def fade(alpha=1.0):
            if alpha > 0.0:
                alpha -= 0.08
                if alpha < 0.0:
                    alpha = 0.0
                self.attributes("-alpha", alpha)
                self.after(15, lambda: fade(alpha))
            else:
                callback()
        fade()

    def setup_ui(self):
        # header panel with close button
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#161B22", height=80)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        logo_path = os.path.join(self.base_dir, "logoExe.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(self.base_dir, "logo.png")

        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(54, 54))
                self.logo_label = ctk.CTkLabel(self.header_frame, image=ctk_img, text="")
                self.logo_label.pack(side="left", padx=20, pady=13)
            except Exception:
                pass

        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.pack(side="left", fill="both", expand=True, pady=12)

        self.header_title = ctk.CTkLabel(self.title_frame, text="poly terminal v1 setup wizard", font=FONT_TITLE, text_color="#58A6FF", anchor="w")
        self.header_title.pack(fill="x", pady=(4, 0))

        self.header_sub = ctk.CTkLabel(self.title_frame, text="poly, your terminal", font=FONT_SUBTITLE, text_color="#8B949E", anchor="w")
        self.header_sub.pack(fill="x")

        # custom close button for frameless window
        self.close_btn = ctk.CTkButton(
            self.header_frame,
            text="✕",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="transparent",
            hover_color="#E81123",
            text_color="#8B949E",
            font=(FONT_FAMILY, 14, "bold"),
            command=self.close_app
        )
        self.close_btn.pack(side="right", padx=15, pady=22)

        # main container frame
        self.main_frame = ctk.CTkFrame(self, fg_color="#0D1117", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        self.show_page_welcome()

    def close_app(self):
        self.animate_fade_out(self.destroy)

    def show_page_welcome(self):
        self.animate_page_transition(self._build_page_welcome)

    def _build_page_welcome(self):
        welcome_label = ctk.CTkLabel(self.main_frame, text="select poly installation directory", font=FONT_BODY_BOLD, text_color="#E6EDF3")
        welcome_label.pack(anchor="w", padx=30, pady=(25, 10))

        # folder selection frame
        dir_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        dir_frame.pack(fill="x", padx=30, pady=5)

        self.dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.install_dir_var, font=FONT_BODY, height=38, corner_radius=8, border_color="#30363D", fg_color="#161B22")
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(dir_frame, text="browse...", width=95, height=38, font=FONT_BUTTON, corner_radius=8, command=self.browse_folder, fg_color="#21262D", hover_color="#30363D")
        browse_btn.pack(side="right")

        # options frame
        options_label = ctk.CTkLabel(self.main_frame, text="shortcut and integration options", font=FONT_BODY_BOLD, text_color="#E6EDF3")
        options_label.pack(anchor="w", padx=30, pady=(25, 10))

        cb_desktop = ctk.CTkCheckBox(self.main_frame, text="create desktop shortcut", variable=self.create_desktop_shortcut_var, font=FONT_BODY, fg_color="#238636", hover_color="#2EA043", corner_radius=6)
        cb_desktop.pack(anchor="w", padx=40, pady=6)

        cb_start = ctk.CTkCheckBox(self.main_frame, text="create start menu shortcut", variable=self.create_start_menu_var, font=FONT_BODY, fg_color="#238636", hover_color="#2EA043", corner_radius=6)
        cb_start.pack(anchor="w", padx=40, pady=6)

        cb_path = ctk.CTkCheckBox(self.main_frame, text="add poly to user PATH environment variable", variable=self.add_to_path_var, font=FONT_BODY, fg_color="#238636", hover_color="#2EA043", corner_radius=6)
        cb_path.pack(anchor="w", padx=40, pady=6)

        # bottom action bar
        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom", padx=30, pady=25)

        cancel_btn = ctk.CTkButton(action_frame, text="cancel", width=105, height=40, font=FONT_BUTTON, corner_radius=8, fg_color="#21262D", hover_color="#30363D", command=self.close_app)
        cancel_btn.pack(side="left")

        install_btn = ctk.CTkButton(action_frame, text="install now", width=140, height=40, font=FONT_BUTTON, corner_radius=8, fg_color="#238636", hover_color="#2EA043", command=self.start_installation)
        install_btn.pack(side="right")

    def browse_folder(self):
        folder_selected = tk.filedialog.askdirectory(initialdir=self.install_dir_var.get())
        if folder_selected:
            self.install_dir_var.set(folder_selected)

    def show_page_installing(self):
        self.animate_page_transition(self._build_page_installing)

    def _build_page_installing(self):
        title_label = ctk.CTkLabel(self.main_frame, text="installing poly terminal...", font=FONT_BODY_BOLD, text_color="#E6EDF3")
        title_label.pack(anchor="w", padx=30, pady=(35, 10))

        self.status_label = ctk.CTkLabel(self.main_frame, text="preparing files...", font=FONT_BODY, text_color="#8B949E")
        self.status_label.pack(anchor="w", padx=30, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=14, corner_radius=7, progress_color="#3FB950", fg_color="#161B22")
        self.progress_bar.pack(fill="x", padx=30, pady=20)
        self.progress_bar.set(0.0)

        self.detail_label = ctk.CTkLabel(self.main_frame, text="", font=(FONT_FAMILY, 11, "normal"), text_color="#6E7681")
        self.detail_label.pack(anchor="w", padx=30, pady=5)

    def show_page_finished(self):
        self.animate_page_transition(self._build_page_finished)

    def _build_page_finished(self):
        success_icon = ctk.CTkLabel(self.main_frame, text="✔", font=(FONT_FAMILY, 48, "bold"), text_color="#3FB950")
        success_icon.pack(pady=(25, 5))

        title_label = ctk.CTkLabel(self.main_frame, text="poly terminal installed successfully!", font=FONT_BODY_BOLD, text_color="#E6EDF3")
        title_label.pack(pady=5)

        sub_label = ctk.CTkLabel(self.main_frame, text=f"installed to: {self.install_dir_var.get()}", font=FONT_SUBTITLE, text_color="#8B949E")
        sub_label.pack(pady=5)

        cb_launch = ctk.CTkCheckBox(self.main_frame, text="launch poly terminal now", variable=self.launch_after_install_var, font=FONT_BODY, fg_color="#238636", hover_color="#2EA043", corner_radius=6)
        cb_launch.pack(pady=20)

        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom", padx=30, pady=25)

        finish_btn = ctk.CTkButton(action_frame, text="finish 🚀", width=140, height=40, font=FONT_BUTTON, corner_radius=8, fg_color="#238636", hover_color="#2EA043", command=self.on_finish)
        finish_btn.pack(side="right")

    def animate_page_transition(self, build_func):
        # smooth micro-animation: clear main frame n build new content smoothly
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        build_func()

    def start_installation(self):
        self.show_page_installing()
        threading.Thread(target=self.run_install_process, daemon=True).start()

    def run_install_process(self):
        try:
            target_dir = self.install_dir_var.get()
            os.makedirs(target_dir, exist_ok=True)

            self.update_status("copying application files...", 0.1)

            # check payload folder
            if not os.path.exists(self.payload_dir):
                self.update_status("error: build payload not found!", 0.0)
                return

            files = []
            for root, dirs, filenames in os.walk(self.payload_dir):
                for f in filenames:
                    files.append(os.path.join(root, f))

            total_files = len(files)
            for i, src_file in enumerate(files):
                rel_path = os.path.relpath(src_file, self.payload_dir)
                dst_file = os.path.join(target_dir, rel_path)

                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                shutil.copy2(src_file, dst_file)

                progress = 0.1 + (0.7 * ((i + 1) / max(1, total_files)))
                self.update_status(f"copying {rel_path}...", progress)
                time.sleep(0.01) # smooth progress pacing

            exe_path = os.path.join(target_dir, "PolyTerminal.exe")
            ico_path = os.path.join(target_dir, "app_icon.ico")

            # create desktop shortcut
            if self.create_desktop_shortcut_var.get():
                self.update_status("creating desktop shortcut...", 0.85)
                desktop_folder = os.path.join(os.environ["USERPROFILE"], "Desktop")
                shortcut_path = os.path.join(desktop_folder, "Poly Terminal.lnk")
                self.create_windows_shortcut(exe_path, shortcut_path, ico_path)

            # create start menu shortcut
            if self.create_start_menu_var.get():
                self.update_status("creating start menu shortcut...", 0.90)
                start_menu_folder = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Poly Terminal")
                os.makedirs(start_menu_folder, exist_ok=True)
                shortcut_path = os.path.join(start_menu_folder, "Poly Terminal.lnk")
                self.create_windows_shortcut(exe_path, shortcut_path, ico_path)

            # add to path
            if self.add_to_path_var.get():
                self.update_status("configuring PATH environment variable...", 0.95)
                self.add_directory_to_user_path(target_dir)

            self.update_status("installation complete!", 1.0)
            self.after(500, self.show_page_finished)

        except Exception as ex:
            self.update_status(f"installation error: {str(ex)}", 0.0)

    def update_status(self, text, progress):
        self.after(0, lambda: self._apply_status_update(text, progress))

    def _apply_status_update(self, text, progress):
        if hasattr(self, "status_label"):
            self.status_label.configure(text=text)
        self._target_progress = progress
        self._smooth_progress_step()

    def _smooth_progress_step(self):
        if hasattr(self, "progress_bar"):
            diff = self._target_progress - self._current_progress
            if abs(diff) > 0.005:
                self._current_progress += diff * 0.2
                self.progress_bar.set(self._current_progress)
                self.after(15, self._smooth_progress_step)
            else:
                self._current_progress = self._target_progress
                self.progress_bar.set(self._current_progress)

    def create_windows_shortcut(self, target_exe, shortcut_path, icon_path=None):
        try:
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{target_exe}'
            $Shortcut.WorkingDirectory = '{os.path.dirname(target_exe)}'
            if (Test-Path '{icon_path}') {{
                $Shortcut.IconLocation = '{icon_path}'
            }}
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def add_directory_to_user_path(self, target_dir):
        try:
            ps_script = f"""
            $oldPath = [Environment]::GetEnvironmentVariable('Path', 'User')
            if ($oldPath -notlike '*{target_dir}*') {{
                $newPath = "$oldPath;{target_dir}"
                [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            }}
            """
            subprocess.run(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception:
            pass

    def on_finish(self):
        if self.launch_after_install_var.get():
            target_exe = os.path.join(self.install_dir_var.get(), "PolyTerminal.exe")
            if os.path.exists(target_exe):
                subprocess.Popen([target_exe], cwd=self.install_dir_var.get())
        self.close_app()

if __name__ == "__main__":
    app = PolyInstallerApp()
    app.mainloop()
