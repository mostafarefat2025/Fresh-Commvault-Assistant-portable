import socket

from client_checker import ClientChecker
from group_manager import GroupManager
from install_logger import InstallLogger


class DeploymentEngine:

    def __init__(self):

        self.hostname = socket.gethostname()

        try:
            self.ip = socket.gethostbyname(
                self.hostname
            )

        except Exception:
            self.ip = "Unknown"

    def get_client_info(self):

        group_info = GroupManager.get_group(
            self.ip
        )

        return {
            "hostname": self.hostname,
            "ip": self.ip,
            "factory": group_info["factory"],
            "group": group_info["group"],
            "client_status": ClientChecker.get_status()
        }

    def validate(self):

        info = self.get_client_info()

        InstallLogger.write(
            f"Hostname: {info['hostname']}"
        )

        InstallLogger.write(
            f"IP: {info['ip']}"
        )

        InstallLogger.write(
            f"Factory: {info['factory']}"
        )

        InstallLogger.write(
            f"Group: {info['group']}"
        )

        InstallLogger.write(
            f"Status: {info['client_status']}"
        )

        return info

    def is_new_client(self):

        return (
            info := self.get_client_info()
        )["client_status"] == "New Client"


if __name__ == "__main__":

    engine = DeploymentEngine()

    info = engine.validate()

    print("\n===== CLIENT INFORMATION =====\n")

    for key, value in info.items():

        print(
            f"{key}: {value}"
        )