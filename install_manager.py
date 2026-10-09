import os
import subprocess
import ctypes


def run_setup(setup_path, silent=False, install_args=None):
    if not os.path.exists(setup_path):
        return False

    parameters = install_args
    if silent and not parameters:
        parameters = '/s /v "/qn"'

    if os.name == "nt":
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

        result = shell_execute(
            None,
            "runas",
            os.path.abspath(setup_path),
            parameters,
            None,
            1,
        )
        if result <= 32:
            raise OSError(f"Windows could not start the installer (ShellExecute error {result}).")
    else:
        cmd = [setup_path]
        if silent and parameters:
            cmd.extend(parameters.split())
        subprocess.Popen(cmd)

    return True