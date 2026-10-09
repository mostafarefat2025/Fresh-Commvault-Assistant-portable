import tkinter as tk
from tkinter import messagebox

from main import App


class LoginWindow:

    def __init__(self):

        self.root = tk.Tk()

        self.root.title(
            "Fresh Commvault Assistant Login"
        )

        self.root.geometry(
            "400x250"
        )

        self.create_ui()

        self.root.mainloop()

    def create_ui(self):

        tk.Label(
            self.root,
            text="Username"
        ).pack(pady=5)

        self.username = tk.Entry(
            self.root,
            width=30
        )

        self.username.pack()

        tk.Label(
            self.root,
            text="Password"
        ).pack(pady=5)

        self.password = tk.Entry(
            self.root,
            width=30,
            show="*"
        )

        self.password.pack()

        tk.Button(
            self.root,
            text="Login",
            command=self.login
        ).pack(pady=20)

    def login(self):

        if not self.username.get():
            messagebox.showerror(
                "Error",
                "Enter Username"
            )
            return

        if not self.password.get():
            messagebox.showerror(
                "Error",
                "Enter Password"
            )
            return

        self.root.destroy()

        App()


if __name__ == "__main__":
    LoginWindow()