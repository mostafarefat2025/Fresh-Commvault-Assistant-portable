from pywinauto import Desktop, timings


class InstallerAutomation:
    PAGE_TITLES = (
        "Language Selection",
        "License Agreement",
        "Choose the Installation type",
        "Install Option",
        "Select Windows Packages",
        "Installation Path",
        "Laptop Options",
        "Installation Summary",
        "Installation Progress",
        "Client Computer Information",
        "Server Information",
        "Server Authentication",
    )

    def __init__(self, status_callback=None, page_timeout=120, install_timeout=3600):
        self.status_callback = status_callback or (lambda message: None)
        self.page_timeout = page_timeout
        self.install_timeout = install_timeout
        self.window = None

    def run_to_server_authentication(self, commserve):
        self.window = Desktop(backend="uia").window(title="Commvault Installer")
        self.window.wait("visible", timeout=self.page_timeout)

        page = self._wait_for_any_page(self.PAGE_TITLES)
        if page == "Language Selection":
            self._select_language()
            page = self._click_next(
                "License Agreement",
                acceptable_pages=("Choose the Installation type",),
            )

        if page == "License Agreement":
            page = self._wait_for_license_acceptance()
            if page == "License Agreement":
                page = self._click_next("Choose the Installation type")

        if page == "Choose the Installation type":
            self._select_radio("rbInstallOnThisMachine")
            page = self._click_next("Install Option")

        if page == "Install Option":
            self._select_radio("rbAdvancedSelection")
            page = self._click_next("Select Windows Packages")

        if page == "Select Windows Packages":
            self._configure_packages()
            page = self._click_next("Installation Path")

        if page == "Installation Path":
            page = self._click_next("Laptop Options")

        if page == "Laptop Options":
            self._configure_laptop_options()
            page = self._click_next("Installation Summary")

        if page == "Installation Summary":
            self.status_callback("Starting the Commvault client installation.")
            page = self._click_next("Installation Progress")

        if page == "Installation Progress":
            self.status_callback("Waiting for installation to finish.")
            page = self._wait_for_page(
                "Client Computer Information",
                timeout=self.install_timeout,
            )

        if page == "Client Computer Information":
            page = self._click_next("Server Information")

        if page == "Server Information":
            self._set_commserve(commserve)

            try:
                page = self._click_next("Server Authentication", timeout=20)
            except timings.TimeoutError:
                self.status_callback(
                    "CommServe did not validate or is unreachable. Stopped at Server Information."
                )
                return "Stopped at Server Information; connect to the company network or VPN and continue manually."

        if page == "Server Authentication":
            self.status_callback("Reached Server Authentication; technician credentials are still required.")
            return "Stopped at Server Authentication before entering credentials."

        raise RuntimeError(f"Unexpected installer page: {page}.")

    def _wait_for_page(self, page_title, timeout=None):
        return self._wait_for_any_page((page_title,), timeout=timeout)

    def _visible_page(self):
        visible_titles = {
            element.window_text()
            for element in self.window.descendants(control_type="Text")
            if element.is_visible()
        }
        current_page = None
        for title in self.PAGE_TITLES:
            if title in visible_titles:
                current_page = title
        return current_page

    def _wait_for_any_page(self, page_titles, timeout=None):
        found_page = {"title": None}

        def page_is_visible():
            current_page = self._visible_page()
            if current_page in page_titles:
                found_page["title"] = current_page
                return True
            return False

        timings.wait_until(
            timeout=timeout or self.page_timeout,
            retry_interval=0.2,
            func=page_is_visible,
            value=True,
        )
        self.status_callback(f"Installer page: {found_page['title']}")
        return found_page["title"]

    def _wait_for_license_acceptance(self):
        if self._visible_page() != "License Agreement":
            return self._visible_page()

        checkbox = self.window.child_window(
            auto_id="checkboxAcceptLicense",
            control_type="CheckBox",
        )
        checkbox.wait("exists enabled", timeout=self.page_timeout)
        self.status_callback("Waiting for the technician to accept the license agreement.")

        def license_is_resolved():
            if self._visible_page() != "License Agreement":
                return True
            try:
                return checkbox.get_toggle_state() == 1
            except Exception:
                return self._visible_page() != "License Agreement"

        timings.wait_until(
            timeout=self.install_timeout,
            retry_interval=0.25,
            func=license_is_resolved,
            value=True,
        )
        return self._visible_page()

    def _select_language(self):
        language = self.window.child_window(
            auto_id="cbLanguageName",
            control_type="ComboBox",
        )
        language.wait("exists enabled", timeout=self.page_timeout)
        expected_language = "English (United States)"
        if language.selected_text() != expected_language:
            language.select(expected_language)
            timings.wait_until(
                timeout=5,
                retry_interval=0.2,
                func=language.selected_text,
                value=expected_language,
            )

        if language.selected_text() != expected_language:
            raise RuntimeError(f"Could not select installer language '{expected_language}'.")

    def _select_radio(self, auto_id):
        radio = self.window.child_window(auto_id=auto_id, control_type="RadioButton")
        radio.wait("exists enabled", timeout=self.page_timeout)
        if not radio.is_selected():
            radio.select()
            timings.wait_until(
                timeout=5,
                retry_interval=0.2,
                func=radio.is_selected,
                value=True,
            )

        if not radio.is_selected():
            raise RuntimeError(f"Could not select radio button '{auto_id}'.")

    def _set_checkbox_state(self, title, checked):
        checkbox = self.window.child_window(title=title, control_type="CheckBox")
        checkbox.wait("exists enabled", timeout=self.page_timeout)
        expected_state = int(checked)
        if checkbox.get_toggle_state() != expected_state:
            checkbox.click_input()
            timings.wait_until(
                timeout=5,
                retry_interval=0.2,
                func=checkbox.get_toggle_state,
                value=expected_state,
            )

        if checkbox.get_toggle_state() != expected_state:
            raise RuntimeError(f"Could not set '{title}' to {checked}.")

    def _configure_packages(self):
        self._set_checkbox_state("File System Core", True)
        self._set_checkbox_state("File System", True)
        self._set_checkbox_state("Restore Only", False)

    def _configure_laptop_options(self):
        expected = {
            "Configure for Laptop Backup": True,
            "Create Laptop Edge Monitor shortcut": False,
            "Create Migration Assistant shortcut": False,
            "Configure as Network Gateway": False,
            "Create Process Manager shortcut": True,
        }
        for title, checked in expected.items():
            self._set_checkbox_state(title, checked)

    def _click_next(self, expected_page, timeout=None, acceptable_pages=()):
        timeout = timeout or self.page_timeout
        expected_pages = (expected_page, *acceptable_pages)
        button = self.window.child_window(auto_id="buttonNext", control_type="Button")
        button.wait("exists enabled", timeout=timeout)
        invoke_failed = False
        try:
            button.invoke()
        except Exception as error:
            invoke_failed = True
            self.status_callback(f"UI Automation invoke failed for Next: {error}; using a UI click.")

        if not invoke_failed:
            try:
                next_page = self._wait_for_any_page(
                    expected_pages,
                    timeout=min(3, timeout),
                )
                self.status_callback(f"Next advanced to {next_page}.")
                return next_page
            except timings.TimeoutError:
                self.status_callback(
                    f"Next did not advance to {expected_page}; trying a UI click."
                )

        button.click_input()
        next_page = self._wait_for_any_page(expected_pages, timeout=timeout)
        self.status_callback(f"Next advanced to {next_page}.")
        return next_page

    def _set_commserve(self, commserve):
        fields = [
            field
            for field in self.window.descendants(control_type="Edit")
            if field.is_visible() and field.is_enabled()
        ]
        if len(fields) != 1:
            raise RuntimeError(f"Expected one CommServe field, found {len(fields)}.")
        fields[0].set_edit_text(commserve)
