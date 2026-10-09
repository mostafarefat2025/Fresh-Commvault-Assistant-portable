import os
import unittest
from unittest.mock import MagicMock, call, patch

from pywinauto import timings

from install_manager import run_setup
from installer_automation import InstallerAutomation
from main import App, get_application_dir


class ConsoleAppTests(unittest.TestCase):

    @patch("main.sys.frozen", True, create=True)
    @patch("main.sys.executable", r"C:\portable\Fresh Commvault Assistant.exe")
    def test_application_dir_uses_exe_folder_when_frozen(self):
        self.assertEqual(get_application_dir(), r"C:\portable")

    @patch("main.sys.frozen", False, create=True)
    def test_application_dir_uses_source_folder_when_not_frozen(self):
        expected = os.path.dirname(os.path.abspath(__file__))
        self.assertEqual(get_application_dir(), expected)

    def test_page_wait_accepts_duplicate_visible_heading_text(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        automation.status_callback = MagicMock()
        visible_heading = MagicMock()
        visible_heading.window_text.return_value = "Installation Path"
        visible_heading.is_visible.return_value = True
        hidden_duplicate = MagicMock()
        hidden_duplicate.window_text.return_value = "Installation Path"
        hidden_duplicate.is_visible.return_value = False
        automation.window = MagicMock()
        automation.window.descendants.return_value = [visible_heading, hidden_duplicate]

        automation._wait_for_page("Installation Path")

        automation.status_callback.assert_called_once_with("Installer page: Installation Path")

    def test_language_selection_chooses_english(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        language = MagicMock()
        language.selected_text.side_effect = ["Deutsch (Deutschland)", "English (United States)", "English (United States)"]
        automation.window = MagicMock()
        automation.window.child_window.return_value = language

        automation._select_language()

        language.select.assert_called_once_with("English (United States)")

    def test_radio_selection_selects_when_needed_and_verifies(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        radio = MagicMock()
        radio.is_selected.side_effect = [False, True, True]
        automation.window = MagicMock()
        automation.window.child_window.return_value = radio

        automation._select_radio("rbAdvancedSelection")

        radio.select.assert_called_once_with()

    def test_radio_selection_does_not_click_selected_option(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        radio = MagicMock()
        radio.is_selected.return_value = True
        automation.window = MagicMock()
        automation.window.child_window.return_value = radio

        automation._select_radio("rbInstallOnThisMachine")

        radio.select.assert_not_called()

    def test_checkbox_state_clicks_when_required_and_verifies(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        checkbox = MagicMock()
        checkbox.get_toggle_state.side_effect = [0, 1, 1]
        automation.window = MagicMock()
        automation.window.child_window.return_value = checkbox

        automation._set_checkbox_state("File System", True)

        checkbox.click_input.assert_called_once_with()

    def test_checkbox_state_does_not_toggle_correct_existing_state(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        checkbox = MagicMock()
        checkbox.get_toggle_state.return_value = 1
        automation.window = MagicMock()
        automation.window.child_window.return_value = checkbox

        automation._set_checkbox_state("File System Core", True)

        checkbox.click_input.assert_not_called()

    def test_package_selection_matches_recorded_wizard(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation._set_checkbox_state = MagicMock()

        automation._configure_packages()

        self.assertEqual(
            automation._set_checkbox_state.call_args_list,
            [
                call("File System Core", True),
                call("File System", True),
                call("Restore Only", False),
            ],
        )

    def test_laptop_options_match_latest_reference_image(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation._set_checkbox_state = MagicMock()

        automation._configure_laptop_options()

        self.assertEqual(
            automation._set_checkbox_state.call_args_list,
            [
                call("Configure for Laptop Backup", True),
                call("Create Laptop Edge Monitor shortcut", False),
                call("Create Migration Assistant shortcut", False),
                call("Configure as Network Gateway", False),
                call("Create Process Manager shortcut", True),
            ],
        )

    @patch("installer_automation.Desktop")
    def test_automation_resumes_from_installation_type(self, mock_desktop):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.window = MagicMock()
        mock_desktop.return_value.window.return_value = automation.window
        automation.status_callback = MagicMock()
        automation.page_timeout = 5
        automation.install_timeout = 10
        automation._wait_for_any_page = MagicMock(return_value="Choose the Installation type")
        automation._wait_for_page = MagicMock(return_value="Client Computer Information")
        automation._wait_for_license_acceptance = MagicMock()
        automation._select_language = MagicMock()
        automation._select_radio = MagicMock()
        automation._configure_packages = MagicMock()
        automation._configure_laptop_options = MagicMock()
        automation._set_commserve = MagicMock()
        automation._click_next = MagicMock(side_effect=[
            "Install Option",
            "Select Windows Packages",
            "Installation Path",
            "Laptop Options",
            "Installation Summary",
            "Installation Progress",
            "Server Information",
            "Server Authentication",
        ])

        result = automation.run_to_server_authentication("commvault.i.fresh.com.eg")

        self.assertEqual(
            automation._click_next.call_args_list,
            [
                call("Install Option"),
                call("Select Windows Packages"),
                call("Installation Path"),
                call("Laptop Options"),
                call("Installation Summary"),
                call("Installation Progress"),
                call("Server Information"),
                call("Server Authentication", timeout=20),
            ],
        )
        automation._set_commserve.assert_called_once_with("commvault.i.fresh.com.eg")
        self.assertIn("credentials", result)

    @patch("installer_automation.Desktop")
    def test_unreachable_commserve_stops_at_server_information(self, mock_desktop):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.window = MagicMock()
        mock_desktop.return_value.window.return_value = automation.window
        automation.status_callback = MagicMock()
        automation.page_timeout = 5
        automation.install_timeout = 10
        automation._wait_for_any_page = MagicMock(return_value="Choose the Installation type")
        automation._wait_for_page = MagicMock(return_value="Client Computer Information")
        automation._wait_for_license_acceptance = MagicMock()
        automation._select_language = MagicMock()
        automation._select_radio = MagicMock()
        automation._configure_packages = MagicMock()
        automation._configure_laptop_options = MagicMock()
        automation._set_commserve = MagicMock()
        automation._click_next = MagicMock(side_effect=[
            "Install Option",
            "Select Windows Packages",
            "Installation Path",
            "Laptop Options",
            "Installation Summary",
            "Installation Progress",
            "Server Information",
            timings.TimeoutError("CommServe unreachable"),
        ])

        result = automation.run_to_server_authentication("commvault.i.fresh.com.eg")

        self.assertIn("Server Information", result)
        automation._set_commserve.assert_called_once_with("commvault.i.fresh.com.eg")

    def test_next_uses_uia_button_invoke(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        automation.status_callback = MagicMock()
        automation._wait_for_any_page = MagicMock(return_value="Laptop Options")
        button = MagicMock()
        automation.window = MagicMock()
        automation.window.child_window.return_value = button

        automation._click_next("Laptop Options")

        button.invoke.assert_called_once_with()
        button.click_input.assert_not_called()

    def test_next_falls_back_to_click_when_invoke_does_not_advance(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        automation.status_callback = MagicMock()
        automation._wait_for_any_page = MagicMock(
            side_effect=[timings.TimeoutError("page did not change"), None]
        )
        button = MagicMock()
        automation.window = MagicMock()
        automation.window.child_window.return_value = button

        automation._click_next("Laptop Options")

        button.invoke.assert_called_once_with()
        button.click_input.assert_called_once_with()

    def test_next_falls_back_to_ui_click_when_invoke_fails(self):
        automation = InstallerAutomation.__new__(InstallerAutomation)
        automation.page_timeout = 5
        automation.status_callback = MagicMock()
        automation._wait_for_any_page = MagicMock(return_value="Laptop Options")
        button = MagicMock()
        button.invoke.side_effect = RuntimeError("invoke unavailable")
        automation.window = MagicMock()
        automation.window.child_window.return_value = button

        automation._click_next("Laptop Options")

        button.click_input.assert_called_once_with()

    @patch("main.messagebox.showinfo")
    @patch("main.console_manager.open_console", return_value=True)
    @patch("main.messagebox.showerror")
    def test_open_console_success(self, mock_show_error, mock_open_console, mock_show_info):
        app = App.__new__(App)
        app.write_log = MagicMock()

        app.open_console()

        mock_open_console.assert_called_once_with()
        mock_show_info.assert_called_once()
        mock_show_error.assert_not_called()

    @patch("main.messagebox.showerror")
    @patch("main.console_manager.open_console", return_value=False)
    @patch("main.messagebox.showinfo")
    def test_open_console_not_found(self, mock_show_info, mock_open_console, mock_show_error):
        app = App.__new__(App)
        app.write_log = MagicMock()

        app.open_console()

        mock_open_console.assert_called_once_with()
        mock_show_error.assert_called_once()
        mock_show_info.assert_not_called()

    @patch("main.messagebox.showerror")
    @patch("main.filedialog.askopenfilename")
    @patch("main.os.path.isfile", return_value=False)
    def test_automatic_install_does_not_prompt_for_missing_setup(
        self, mock_isfile, mock_askopenfilename, mock_show_error
    ):
        app = App.__new__(App)
        app.write_log = MagicMock()

        app.install_client(automatic=True)

        mock_askopenfilename.assert_not_called()
        mock_show_error.assert_called_once()

    @patch("main.threading.Thread")
    @patch("main.messagebox.showinfo")
    @patch("main.run_setup", return_value=True)
    @patch("main.os.path.isfile", return_value=True)
    def test_install_client_launches_bundled_commvault_launcher(
        self, mock_isfile, mock_run_setup, mock_show_info, mock_thread
    ):
        app = App.__new__(App)
        app.write_log = MagicMock()
        app.progress = MagicMock()

        app.install_client()

        launcher_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "WinX64",
            "LaunchInstaller.exe",
        )
        mock_run_setup.assert_called_once_with(launcher_path)
        mock_show_info.assert_not_called()
        mock_thread.assert_called_once()

    @patch("install_manager.ctypes.WinDLL")
    @patch("install_manager.os.path.exists", return_value=True)
    def test_run_setup_silent_mode(self, mock_exists, mock_win_dll):
        shell_execute = MagicMock(return_value=42)
        mock_win_dll.return_value.ShellExecuteW = shell_execute

        result = run_setup("C:/temp/setup.exe", silent=True)

        self.assertTrue(result)
        shell_execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
