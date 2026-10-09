import os
import ctypes
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import console_manager
from installer_engine import InstallerEngine
from install_manager import run_setup
from installer_automation import InstallerAutomation
from config import COMM_SERVE


def get_application_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def relaunch_as_admin():
    if os.name != "nt" or ctypes.windll.shell32.IsUserAnAdmin():
        return False

    shell_execute = ctypes.WinDLL("shell32", use_last_error=True).ShellExecuteW
    shell_execute.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_int,
    ]
    shell_execute.restype = ctypes.c_void_p
    command_args = list(sys.argv[1:]) if getattr(sys, "frozen", False) else [
        os.path.abspath(__file__),
        *sys.argv[1:],
    ]
    parameters = subprocess.list2cmdline(command_args)
    result = shell_execute(
        None,
        "runas",
        sys.executable,
        parameters,
        get_application_dir() if not getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(sys.executable)),
        1,
    )
    if result <= 32:
        raise OSError(f"Windows could not restart the assistant as administrator (ShellExecute error {result}).")

    return True


class App:

    def __init__(self):

        self.engine = InstallerEngine()
        self.info = self.engine.get_info()

        self.root = tk.Tk()
        self.root.title("Fresh Commvault Assistant")
        self.root.geometry("900x700")

        self.build_ui()
        if not self.info["client"]:
            self.root.after(500, lambda: self.install_client(automatic=True))

        self.root.mainloop()

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="Fresh Commvault Assistant",
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=20)

        info_text = (
            f"Computer Name : {self.info['hostname']}\n\n"
            f"IP Address : {self.info['ip']}\n\n"
            f"Factory : {self.info['factory']}\n\n"
            f"Group : {self.info['group']}\n\n"
            f"Console Installed : {self.info['console']}\n\n"
            f"Client Installed : {self.info['client']}"
        )

        info_label = tk.Label(
            self.root,
            text=info_text,
            justify="left",
            font=("Segoe UI", 11)
        )
        info_label.pack(pady=15)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=500,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        install_btn = tk.Button(
            self.root,
            text="Install Client",
            width=25,
            height=2,
            command=self.install_client
        )
        install_btn.pack(pady=10)

        console_btn = tk.Button(
            self.root,
            text="Open Commvault",
            width=25,
            height=2,
            command=self.open_console
        )
        console_btn.pack(pady=10)

        self.logs = tk.Text(
            self.root,
            height=12,
            width=90
        )
        self.logs.pack(padx=20, pady=20)

        self.write_log("Assistant Started")
        self.write_log(f"Factory: {self.info['factory']}")
        self.write_log(f"Group: {self.info['group']}")

    def write_log(self, message):

        self.logs.insert(
            tk.END,
            message + "\n"
        )

        self.logs.see(tk.END)

    def install_client(self, automatic=False):

        setup_path = os.path.join(
            get_application_dir(),
            "WinX64",
            "LaunchInstaller.exe",
        )
        if not os.path.isfile(setup_path):
            if automatic:
                self.write_log("WinX64\\LaunchInstaller.exe was not found; automatic install was not started.")
                messagebox.showerror(
                    "Installer Error",
                    "WinX64\\LaunchInstaller.exe was not found. Place the WinX64 installer folder beside the assistant and restart the program."
                )
                return

            setup_path = filedialog.askopenfilename(
                title="Select LaunchInstaller.exe",
                initialdir=os.path.join(get_application_dir(), "WinX64"),
                filetypes=[
                    ("Commvault Installer", "LaunchInstaller.exe")
                ]
            )

        if not setup_path:
            return

        self.write_log(f"Selected: {setup_path}")

        try:
            started = run_setup(setup_path)
        except OSError as error:
            self.write_log(f"Could not start installer: {error}")
            messagebox.showerror(
                "Installer Error",
                f"Could not start the installer. You may have cancelled the administrator permission prompt.\n\n{error}"
            )
            return

        if started:

            self.progress["value"] = 5

            self.write_log(
                "Commvault installer started; automation is beginning."
            )
            threading.Thread(
                target=self._run_installer_automation,
                daemon=True,
            ).start()

        else:

            self.write_log(
                "Setup.exe Not Found"
            )

    def _run_installer_automation(self):
        def report(message):
            self.root.after(0, lambda: self.write_log(message))

        try:
            automation = InstallerAutomation(status_callback=report)
            result = automation.run_to_server_authentication(COMM_SERVE)
            report(result)
        except Exception as error:
            report(f"Installer automation stopped: {error}")

    def open_console(self):

        self.write_log("Open Console Clicked")

        launched = console_manager.open_console()

        if launched:
            self.write_log("Commvault Console Started Successfully")
            messagebox.showinfo(
                "Commvault",
                "Console started successfully."
            )
            return

        self.write_log("Commvault Console Not Found")
        messagebox.showerror(
            "Commvault",
            "Commvault Console was not found on this machine."
        )


if __name__ == "__main__":
    try:
        if not relaunch_as_admin():
            App()
    except OSError as error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Administrator Permission Required", str(error))
        root.destroy()