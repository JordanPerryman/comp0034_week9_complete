from pathlib import Path
import pandas as pd
import requests
from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver

from my_app import db, create_app, config


class TestBase(LiveServerTestCase):

    def create_app(self):
        app = create_app(config.TestingConfig)
        # Default port is 5000 which would conflict with Flask
        app.config['LIVESERVER_PORT'] = 8943
        return app

    def setUp(self):
        """ Creates the chrome driver and adds tables to the database plus the country data """
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())
        db.create_all()
        # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
        csv_file = Path(__file__).parent.parent.joinpath("data/household_recycling.csv")
        df = pd.read_csv(csv_file, usecols=['Code', 'Area'])
        df.drop_duplicates(inplace=True)
        df.set_index('Code', inplace=True)
        df.to_sql('area', db.engine, if_exists='replace')

    def tearDown(self):
        """ Quit the webriver and drop tables from database """
        db.drop_all()
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        # response = urllib2.urlopen(self.get_server_url()) # urllib2 no longer available to install
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
        message = self.driver.find_element_by_class_name("alert list-unstyled").find_element_by_tag_name("li").text
        self.assertIn(f"Hello, {first_name} {last_name}. You are signed up.", message)
