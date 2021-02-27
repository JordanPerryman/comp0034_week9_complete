# Adapted from https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1 and part 2

import requests
from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver

from my_app import db, create_app, config


class TestBase(LiveServerTestCase):
    """
    Base test class for the selenium tests
    """

    def create_app(self):
        app = create_app(config.TestingConfig)
        app.config['LIVESERVER_PORT'] = 8943
        return app

    def setUp(self):
        """ Creates the chrome driver and adds tables to the database plus the country data """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1200x600")
        self.driver = webdriver.Chrome(options=options)
        self.driver.create_options()
        self.driver.get(self.get_server_url())

    def tearDown(self):
        """ Quit the webriver and drop tables from database """
        db.drop_all()
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        self.assertEqual(response.status_code, 200)


class TestRegistration(TestBase):

    def test_registration_succeeds(self):
        """
        Test that a user can create an account using the signup form if all fields are filled out correctly, and that
        they will be redirected to the index page
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
        self.assertIn(url_for('main.index'), self.driver.current_url)

        # Assert success message is flashed on the index page
        message = self.driver.find_element_by_id("messages").find_element_by_tag_name("li").text
        self.assertIn(f"Hello, {first_name} {last_name}. You are signed up.", message)
