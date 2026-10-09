import os
import socket
import subprocess


class InstallerEngine:

    def get_hostname(self):
        return socket.gethostname()

    def get_ip(self):
        try:
            return socket.gethostbyname(
                socket.gethostname()
            )
        except:
            return "Unknown"

    def detect_factory(self):

        ip = self.get_ip()

        if ip.startswith("10.5."):
            return "Obour", "Obour Workstations"

        elif ip.startswith("10.6."):
            return "Borg El Arab", "Borg Workstations"

        elif ip.startswith("10.7."):
            return "Beni Suef", "Beni Suef Workstations"

        return "Unknown", "Default Group"

    def is_console_installed(self):

        paths = [
            r"C:\Program Files\Commvault",
            r"C:\Program Files\Commvault ContentStore"
        ]

        for path in paths:

            if os.path.exists(path):
                return True

        return False

    def is_client_installed(self):

        try:

            result = subprocess.run(
                ["sc", "query", "GxCVD"],
                capture_output=True,
                text=True
            )

            return (
                "RUNNING" in result.stdout
                or
                "STOPPED" in result.stdout
            )

        except:
            return False

    def get_info(self):

        factory, group = self.detect_factory()

        return {
            "hostname": self.get_hostname(),
            "ip": self.get_ip(),
            "factory": factory,
            "group": group,
            "console": self.is_console_installed(),
            "client": self.is_client_installed()
        }