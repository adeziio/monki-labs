import os
import shutil
import time

from pathlib import Path

from dotenv import (
    load_dotenv
)

from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException
)
from selenium.webdriver.common.by import (
    By
)

from selenium.webdriver.common.keys import (
    Keys
)

from ai.providers.veo_watermark_remover import (
    VeoWatermarkRemover,
    validate_video_file
)


class SnapGenAiError(
    RuntimeError
):

    """
    Raised for any SnapGenAI automation failure: missing
    credentials, login failure, generation failure, download
    failure, timeouts, and browser problems. The message is always
    safe to surface directly in job state and never contains
    credentials.

    Errors with retryable=False (missing credentials, login
    failures) will not be retried by the generation retry wrapper.
    """

    def __init__(
        self,
        message,
        retryable=True
    ):

        super().__init__(
            message
        )

        self.retryable = retryable


XPATH_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

XPATH_LOWER = "abcdefghijklmnopqrstuvwxyz"

PROMPT_SELECTORS = [
    "textarea",
    "input[type='text']"
]

SUBMIT_SELECTORS = [
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'generate')]",
    "//button[@type='submit']",
    "//input[@type='submit']"
]

DOWNLOAD_SELECTORS = [
    "//a[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'download')]",
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'download')]",
    "//a[contains(@href, '.mp4')]"
]

LOGIN_EMAIL_SELECTORS = [
    "input[type='email']",
    "input[name='username']",
    "input[autocomplete='username']",
    "input[placeholder*='email' i]"
]

LOGIN_PASSWORD_SELECTORS = [
    "input[type='password']",
    "input[name='password']",
    "input[autocomplete='current-password']"
]

LOGIN_SUBMIT_SELECTORS = [
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'continue')]",
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'sign in')]",
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'log in')]",
    "//button[contains(translate(normalize-space(.), "
    f"'{XPATH_UPPER}', '{XPATH_LOWER}'), 'submit')]",
    "//button[@type='submit']",
    "//input[@type='submit']"
]

LOGIN_URL_MARKERS = (
    "login",
    "signin",
    "sign-in",
    "sign_in",
    "auth",
    "signup",
    "register"
)

PARTIAL_SUFFIXES = (
    ".crdownload",
    ".part",
    ".tmp"
)


def parse_selector(
    selector
):

    """
    Treats selectors starting with "//" as XPath and everything
    else as CSS, so every selector in config/ai_models.json works
    with the same syntax used on the page.
    """

    selector = str(
        selector
    ).strip()

    if selector.startswith("//"):

        return (
            By.XPATH,
            selector
        )

    return (
        By.CSS_SELECTOR,
        selector
    )


class SnapGenAiProvider:

    """
    Browser-automation backend for SnapGenAI
    (https://snapgen.ai/).

    Workflow: open the site -> enter the episode prompt -> click
    Generate -> complete login in a popup/tab when it appears using
    credentials from the environment -> resubmit the prompt when
    authentication dropped the original submission -> wait for the
    generation to finish using element state (no fixed sleeps) ->
    download the video through the browser's download manager ->
    remove the Veo watermark with VeoWatermarkRemover (standard CPU
    mode) and validate the cleaned result.

    The Chrome profile is persisted across runs so the
    authenticated session/cookies are reused when practical.
    Credentials come only from snapgenai_email / snapgenai_password
    in .env and are never logged or included in error messages.

    All connection details come from config/ai_models.json ->
    models.video_model.snapgenai.
    """

    DEFAULT_BASE_URL = "https://snapgen.ai/"

    DEFAULT_PROFILE_DIRECTORY = (
        "media/browser_profile/snapgenai"
    )

    DEFAULT_DOWNLOAD_DIRECTORY = (
        "media/downloads/snapgenai"
    )

    def __init__(
        self,
        config,
        progress_callback=None
    ):

        self.config = config

        self.video_config = (
            config["ai_models"]
            ["models"]
            ["video_model"]
        )

        # Callers may already have loaded .env; loading again is
        # harmless and keeps the provider usable standalone.

        load_dotenv()

        self.settings = (
            self.video_config.get(
                "snapgenai",
                {}
            )
        )

        if not isinstance(
            self.settings,
            dict
        ):

            self.settings = {}

        self.progress_callback = (
            progress_callback
        )

        self.watermark_remover = VeoWatermarkRemover(
            config,
            notify=self._notify
        )

    def _notify(
        self,
        message
    ):

        if self.progress_callback is None:

            return

        try:

            self.progress_callback(
                str(
                    message
                )
            )

        except Exception:

            pass

    def _setting(
        self,
        name,
        default=""
    ):

        return self.settings.get(
            name,
            default
        )

    def _seconds(
        self,
        name,
        default
    ):

        try:

            value = float(
                self._setting(
                    name,
                    default
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return float(
                default
            )

        if value <= 0:

            return float(
                default
            )

        return value

    def _flag(
        self,
        name,
        default=False
    ):

        value = self._setting(
            name,
            default
        )

        if isinstance(
            value,
            bool
        ):

            return value

        return str(
            value
        ).strip().lower() in (
            "1",
            "true",
            "yes",
            "on"
        )

    def _base_url(
        self
    ):

        base_url = str(
            self._setting(
                "base_url",
                self.DEFAULT_BASE_URL
            )
        ).strip()

        return (
            base_url
            or self.DEFAULT_BASE_URL
        )

    def _headless(
        self
    ):

        # Default is False so the browser stays visible while the
        # automation is being developed and tested.

        return self._flag(
            "headless",
            False
        )

    def _profile_directory(
        self
    ):

        profile_directory = Path(
            str(
                self._setting(
                    "profile_directory",
                    self.DEFAULT_PROFILE_DIRECTORY
                )
            )
        ).resolve()

        profile_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        return profile_directory

    def _download_directory(
        self
    ):

        download_directory = Path(
            str(
                self._setting(
                    "download_directory",
                    self.DEFAULT_DOWNLOAD_DIRECTORY
                )
            )
        ).resolve()

        download_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        return download_directory

    def _credentials(
        self
    ):

        email = os.getenv(
            "snapgenai_email",
            ""
        ).strip()

        password = os.getenv(
            "snapgenai_password",
            ""
        ).strip()

        if not email or not password:

            raise SnapGenAiError(
                "SnapGenAI credentials are missing. "
                "Set snapgenai_email and "
                "snapgenai_password in .env.",
                retryable=False
            )

        return (
            email,
            password
        )

    def _selectors(
        self,
        name,
        fallbacks
    ):

        selectors = []

        configured = str(
            self._setting(
                name,
                ""
            )
        ).strip()

        if configured:

            selectors.append(
                configured
            )

        selectors.extend(
            fallbacks
        )

        return selectors

    def _prompt_selectors(
        self
    ):

        return self._selectors(
            "prompt_selector",
            PROMPT_SELECTORS
        )

    def _submit_selectors(
        self
    ):

        return self._selectors(
            "submit_selector",
            SUBMIT_SELECTORS
        )

    def _download_selectors(
        self
    ):

        return self._selectors(
            "download_selector",
            DOWNLOAD_SELECTORS
        )

    def _login_email_selectors(
        self
    ):

        return self._selectors(
            "login_email_selector",
            LOGIN_EMAIL_SELECTORS
        )

    def _login_password_selectors(
        self
    ):

        return self._selectors(
            "login_password_selector",
            LOGIN_PASSWORD_SELECTORS
        )

    def _login_submit_selectors(
        self
    ):

        return self._selectors(
            "login_submit_selector",
            LOGIN_SUBMIT_SELECTORS
        )

    def _find_visible(
        self,
        driver,
        selectors
    ):

        for selector in selectors:

            by, value = parse_selector(
                selector
            )

            try:

                elements = driver.find_elements(
                    by,
                    value
                )

            except WebDriverException:

                continue

            for element in elements:

                try:

                    if (
                        element.is_displayed()
                        and element.is_enabled()
                    ):

                        return element

                except WebDriverException:

                    continue

        return None

    def _safe_click(
        self,
        driver,
        element
    ):

        try:

            element.click()

        except WebDriverException:

            driver.execute_script(
                "arguments[0].click();",
                element
            )

    def _create_driver(
        self,
        download_directory
    ):

        options = webdriver.ChromeOptions()

        # A persistent profile keeps the authenticated
        # session/cookies between runs.

        options.add_argument(
            f"--user-data-dir={self._profile_directory()}"
        )

        if self._headless():

            options.add_argument(
                "--headless=new"
            )

            options.add_argument(
                "--disable-gpu"
            )

        options.add_argument(
            "--window-size=1280,1600"
        )

        options.add_argument(
            "--no-first-run"
        )

        options.add_argument(
            "--no-default-browser-check"
        )

        options.add_experimental_option(
            "excludeSwitches",
            ["enable-automation"]
        )

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": str(
                    download_directory
                ),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
        )

        try:

            driver = webdriver.Chrome(
                options=options
            )

        except WebDriverException as error:

            raise SnapGenAiError(
                "Could not start Chrome for SnapGenAI "
                "automation. Make sure Google Chrome is "
                "installed and not already running with "
                f"the same profile. ({error})",
                retryable=False
            )

        driver.set_page_load_timeout(
            self._seconds(
                "page_timeout_seconds",
                60
            )
        )

        return driver

    def _open_generation_page(
        self,
        driver
    ):

        base_url = (
            self._base_url()
        )

        self._notify(
            f"Opening {base_url}..."
        )

        driver.get(
            base_url
        )

        page_timeout = self._seconds(
            "page_timeout_seconds",
            60
        )

        deadline = time.monotonic() + page_timeout

        while time.monotonic() < deadline:

            if driver.find_elements(
                By.TAG_NAME,
                "body"
            ):

                return

            time.sleep(0.5)

        raise SnapGenAiError(
            f"The SnapGenAI page did not load within "
            f"{page_timeout:g} seconds."
        )

    def _enter_prompt(
        self,
        driver,
        prompt
    ):

        self._notify(
            "Entering the episode prompt..."
        )

        timeout = self._seconds(
            "page_timeout_seconds",
            60
        )

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            element = self._find_visible(
                driver,
                self._prompt_selectors()
            )

            if element is not None:

                try:

                    element.clear()

                    element.send_keys(
                        prompt
                    )

                except WebDriverException:

                    time.sleep(0.5)

                    continue

                if self._prompt_entered(
                    element,
                    prompt
                ):

                    return

            time.sleep(0.5)

        raise SnapGenAiError(
            "Could not enter the prompt into the "
            "SnapGenAI generation page. Adjust "
            "models.video_model.snapgenai."
            "prompt_selector in config/ai_models.json "
            "if the page uses a different field."
        )

    def _prompt_entered(
        self,
        element,
        prompt
    ):

        # Best-effort verification: read the value (inputs) or the
        # text (contenteditable fields) and confirm the prompt is
        # present before submitting.

        try:

            current = (
                element.get_attribute("value")
                or element.text
                or ""
            )

        except WebDriverException:

            return True

        return prompt.strip() in current.strip()

    def _submit_generation(
        self,
        driver
    ):

        self._notify(
            "Submitting the generation request..."
        )

        timeout = self._seconds(
            "submit_timeout_seconds",
            30
        )

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            element = self._find_visible(
                driver,
                self._submit_selectors()
            )

            if element is not None:

                self._safe_click(
                    driver,
                    element
                )

                return

            time.sleep(0.5)

        raise SnapGenAiError(
            "Could not find the Generate/Submit button "
            "on the SnapGenAI page. Adjust "
            "models.video_model.snapgenai."
            "submit_selector in config/ai_models.json "
            "if the page uses a different button."
        )

    def _login_fields_present(
        self,
        driver
    ):

        # Email OR password counts as a login form, so stepwise
        # login flows (email first, password afterwards) are also
        # detected.

        if self._find_visible(
            driver,
            self._login_email_selectors()
        ) is not None:

            return True

        return self._find_visible(
            driver,
            self._login_password_selectors()
        ) is not None

    def _window_is_login(
        self,
        driver
    ):

        try:

            url = str(
                driver.current_url
                or ""
            ).lower()

        except WebDriverException:

            return False

        if any(
            marker in url
            for marker in LOGIN_URL_MARKERS
        ):

            return True

        return self._login_fields_present(
            driver
        )

    def _wait_for_login_popup(
        self,
        driver,
        original_handle
    ):

        # Bounded, event-based wait for a login tab/popup that may
        # appear after the generation request is submitted.

        timeout = self._seconds(
            "login_popup_wait_seconds",
            15
        )

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            try:

                handles = driver.window_handles

            except WebDriverException:

                handles = []

            for handle in handles:

                if handle == original_handle:

                    continue

                driver.switch_to.window(
                    handle
                )

                if self._window_is_login(
                    driver
                ):

                    return handle

            driver.switch_to.window(
                original_handle
            )

            time.sleep(0.5)

        return None

    def _login_form_visible(
        self,
        driver
    ):

        timeout = self._seconds(
            "login_form_probe_seconds",
            5
        )

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            if self._login_fields_present(
                driver
            ):

                return True

            time.sleep(0.5)

        return False

    def _complete_login(
        self,
        driver,
        email,
        password
    ):

        # Credentials are passed only to the browser form fields;
        # they never appear in notifications or error messages.

        self._notify(
            "Login required - signing in to "
            "SnapGenAI..."
        )

        timeout = self._seconds(
            "login_timeout_seconds",
            120
        )

        deadline = time.monotonic() + timeout

        email_field = self._wait_for_login_field(
            driver,
            self._login_email_selectors(),
            deadline
        )

        if email_field is None:

            raise SnapGenAiError(
                "A login page appeared but the SnapGenAI "
                "email field could not be found. Adjust "
                "models.video_model.snapgenai."
                "login_email_selector in "
                "config/ai_models.json if the page uses "
                "a different field.",
                retryable=False
            )

        self._fill_login_field(
            email_field,
            email
        )

        password_field = self._find_visible(
            driver,
            self._login_password_selectors()
        )

        if password_field is not None:

            # Single-step form: email and password on the same
            # page, one submit at the end.

            self._fill_login_field(
                password_field,
                password
            )

            self._click_login_submit(
                driver,
                password_field
            )

        else:

            # Stepwise form: submit the email (Continue), then
            # wait for the password step to appear. Some accounts
            # sign in directly after the email step - that is
            # handled by the completion check below.

            self._click_login_submit(
                driver,
                email_field
            )

            while time.monotonic() < deadline:

                if not self._login_fields_present(
                    driver
                ):

                    self._notify(
                        "Signed in to SnapGenAI."
                    )

                    return

                password_field = self._find_visible(
                    driver,
                    self._login_password_selectors()
                )

                if password_field is not None:

                    break

                time.sleep(0.5)

            if password_field is None:

                raise SnapGenAiError(
                    "SnapGenAI login did not reach the "
                    "password step after submitting the "
                    "email address.",
                    retryable=False
                )

            self._fill_login_field(
                password_field,
                password
            )

            self._click_login_submit(
                driver,
                password_field
            )

        while time.monotonic() < deadline:

            if not self._login_fields_present(
                driver
            ):

                self._notify(
                    "Signed in to SnapGenAI."
                )

                return

            time.sleep(0.5)

        raise SnapGenAiError(
            "SnapGenAI login failed - the login form "
            "did not clear after submission. Check the "
            "configured credentials.",
            retryable=False
        )

    def _wait_for_login_field(
        self,
        driver,
        selectors,
        deadline
    ):

        while time.monotonic() < deadline:

            element = self._find_visible(
                driver,
                selectors
            )

            if element is not None:

                return element

            time.sleep(0.5)

        return None

    def _fill_login_field(
        self,
        element,
        value
    ):

        try:

            element.clear()

            element.send_keys(
                value
            )

        except WebDriverException as error:

            raise SnapGenAiError(
                "Could not fill the SnapGenAI login "
                f"form. ({error})",
                retryable=False
            )

    def _click_login_submit(
        self,
        driver,
        fallback_field
    ):

        submit_button = self._find_visible(
            driver,
            self._login_submit_selectors()
        )

        if submit_button is not None:

            self._safe_click(
                driver,
                submit_button
            )

            return

        # No recognizable submit control: press Enter in the
        # field, or submit its form as a last resort.

        try:

            fallback_field.send_keys(
                Keys.ENTER
            )

        except WebDriverException:

            fallback_field.submit()

    def _handle_login_if_needed(
        self,
        driver,
        email,
        password
    ):

        original_handle = (
            driver.current_window_handle
        )

        popup_handle = self._wait_for_login_popup(
            driver,
            original_handle
        )

        if popup_handle is not None:

            driver.switch_to.window(
                popup_handle
            )

            self._complete_login(
                driver,
                email,
                password
            )

            driver.close()

            driver.switch_to.window(
                original_handle
            )

            return True

        if self._login_form_visible(
            driver
        ):

            self._complete_login(
                driver,
                email,
                password
            )

            return True

        return False

    def _submission_was_lost(
        self,
        driver,
        prompt
    ):

        # After authentication the generation page may have been
        # reloaded with the original submission gone. When the
        # prompt field still holds the untouched prompt, the
        # request never went through and must be submitted again.

        element = self._find_visible(
            driver,
            self._prompt_selectors()
        )

        if element is None:

            return False

        try:

            current = (
                element.get_attribute("value")
                or element.text
                or ""
            )

        except WebDriverException:

            return False

        return (
            current.strip() == prompt.strip()
        )

    def _wait_for_generation(
        self,
        driver
    ):

        timeout = self._seconds(
            "generation_timeout_seconds",
            1800
        )

        deadline = time.monotonic() + timeout

        poll_interval = self._seconds(
            "poll_interval_seconds",
            3
        )

        failure_selector = str(
            self._setting(
                "failure_selector",
                ""
            )
        ).strip()

        self._notify(
            "Waiting for SnapGenAI generation "
            "to finish..."
        )

        started_at = time.monotonic()

        while True:

            if self._find_visible(
                driver,
                self._download_selectors()
            ) is not None:

                self._notify(
                    "Generation finished - "
                    "download is available."
                )

                return

            if failure_selector:

                if self._find_visible(
                    driver,
                    [failure_selector]
                ) is not None:

                    raise SnapGenAiError(
                        "SnapGenAI reported a "
                        "generation failure on the "
                        "page."
                    )

            if time.monotonic() >= deadline:

                raise SnapGenAiError(
                    "Timed out waiting for SnapGenAI "
                    f"generation after {timeout:g} "
                    "seconds."
                )

            elapsed = int(
                time.monotonic() - started_at
            )

            if (
                elapsed
                and elapsed % 60 < poll_interval
            ):

                self._notify(
                    f"Still generating... "
                    f"({elapsed}s elapsed)"
                )

            time.sleep(
                poll_interval
            )

    def _snapshot(
        self,
        directory
    ):

        return {
            path
            for path in directory.iterdir()
            if path.is_file()
        }

    def _download_result(
        self,
        driver,
        download_directory
    ):

        self._notify(
            "Downloading the generated video..."
        )

        before = self._snapshot(
            download_directory
        )

        element = self._find_visible(
            driver,
            self._download_selectors()
        )

        if element is None:

            raise SnapGenAiError(
                "Generation finished but no download "
                "button or link was found on the page. "
                "Adjust models.video_model.snapgenai."
                "download_selector in "
                "config/ai_models.json if the page "
                "uses a different control."
            )

        self._safe_click(
            driver,
            element
        )

        timeout = self._seconds(
            "download_timeout_seconds",
            300
        )

        deadline = time.monotonic() + timeout

        poll_interval = self._seconds(
            "download_poll_interval_seconds",
            2
        )

        stable_size = None

        stable_polls = 0

        while time.monotonic() < deadline:

            new_files = (
                self._snapshot(download_directory)
                - before
            )

            completed = [
                path
                for path in new_files
                if path.suffix.lower()
                not in PARTIAL_SUFFIXES
            ]

            if completed:

                latest = max(
                    completed,
                    key=(
                        lambda path: (
                            path.stat().st_mtime
                        )
                    )
                )

                size = latest.stat().st_size

                if (
                    size > 0
                    and size == stable_size
                ):

                    stable_polls += 1

                    # Require the file size to settle across
                    # two consecutive polls so partially
                    # written downloads are never accepted.

                    if stable_polls >= 2:

                        validate_video_file(
                            latest
                        )

                        self._notify(
                            f"Video downloaded: "
                            f"{latest.name}"
                        )

                        return latest

                else:

                    stable_size = size

                    stable_polls = 0

            time.sleep(
                poll_interval
            )

        raise SnapGenAiError(
            "Timed out waiting for the SnapGenAI "
            f"video download after {timeout:g} "
            "seconds."
        )

    def generate_clip(
        self,
        prompt,
        output_path
    ):

        """
        Full SnapGenAI workflow for one clip: browser generation ->
        download -> Veo watermark removal (standard CPU mode) ->
        validated cleaned video at output_path. The downloaded
        original is kept until the cleaned output has been
        successfully created.
        """

        prompt = str(
            prompt
        ).strip()

        if not prompt:

            raise SnapGenAiError(
                "The SnapGenAI prompt is empty.",
                retryable=False
            )

        email, password = (
            self._credentials()
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        download_directory = (
            self._download_directory()
        )

        driver = self._create_driver(
            download_directory
        )

        try:

            self._open_generation_page(
                driver
            )

            self._enter_prompt(
                driver,
                prompt
            )

            self._submit_generation(
                driver
            )

            logged_in = (
                self._handle_login_if_needed(
                    driver,
                    email,
                    password
                )
            )

            if (
                logged_in
                or self._submission_was_lost(
                    driver,
                    prompt
                )
            ):

                # Authentication navigated away from the
                # generation page and dropped the original
                # submission - return to the generation page
                # and submit the prompt again.

                self._notify(
                    "Returning to the generation page "
                    "after sign-in..."
                )

                self._open_generation_page(
                    driver
                )

                self._enter_prompt(
                    driver,
                    prompt
                )

                self._submit_generation(
                    driver
                )

            self._wait_for_generation(
                driver
            )

            downloaded_file = (
                self._download_result(
                    driver,
                    download_directory
                )
            )

        finally:

            try:

                driver.quit()

            except WebDriverException:

                pass

        staging_path = (
            output_path.parent
            / (
                "_snapgenai_download"
                + (
                    downloaded_file.suffix
                    or ".mp4"
                )
            )
        )

        if staging_path.exists():

            try:

                staging_path.unlink()

            except OSError as error:

                raise SnapGenAiError(
                    f"Could not replace the previous "
                    f"download {staging_path.name}: "
                    f"{error}"
                )

        try:

            shutil.move(
                str(
                    downloaded_file
                ),
                str(
                    staging_path
                )
            )

        except OSError as error:

            raise SnapGenAiError(
                f"Could not store the downloaded video "
                f"in the episode folder: {error}"
            )

        # The remover keeps the original intact and the cleaned
        # output is validated before this call returns, so the
        # original download is only discarded after a verified
        # success.

        cleaned_path = (
            self.watermark_remover
            .remove_watermark(
                staging_path,
                output_path
            )
        )

        try:

            staging_path.unlink()

        except OSError as error:

            self._notify(
                f"Could not remove the original "
                f"download {staging_path.name}: "
                f"{error}"
            )

        return cleaned_path
