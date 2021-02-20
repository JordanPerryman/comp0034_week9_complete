import pytest


@pytest.mark.usefixtures('chrome_driver', 'run_app')
class TestMyAppBrowser:
    def test_app_is_running(self, app):
        self.driver.implicitly_wait(10)
        self.driver.get("http://127.0.0.1:5000/")
        assert self.driver.title == 'Home page'

    def test_signup_succeeds(self):
        """
        Test that a user can create an account using the signup form if all fields are filled out correctly,
        and that they are redirected to the index page.
        """

        # Click signup menu link
        self.driver.find_element_by_id("signup-nav").click()
        self.driver.implicitly_wait(10)

        # Test person data
        first_name = "First"
        last_name = "Last"
        email = "email@ucl.ac.uk"
        password = "password1"
        password_repeat = "password1"

        # Fill in registration form
        self.driver.find_element_by_id("first_name").send_keys(first_name)
        self.driver.find_element_by_id("last_name").send_keys(last_name)
        self.driver.find_element_by_id("email").send_keys(email)
        self.driver.find_element_by_id("password").send_keys(password)
        self.driver.find_element_by_id("password_repeat").send_keys(password_repeat)
        self.driver.find_element_by_id("submit").click()
        self.driver.implicitly_wait(10)

        # Assert that browser redirects to index page
        assert self.driver.current_url == 'http://127.0.0.1:5000/'

        # Assert success message is flashed on the index page
        message = self.driver.find_element_by_class_name("list-unstyled").find_element_by_tag_name("li").text
        assert f"Hello, {first_name} {last_name}. You are signed up." in message
