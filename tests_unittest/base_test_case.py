# Adapted from https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1 and Flask-Testing
# https://pythonhosted.org/Flask-Testing/

import pandas as pd
from pathlib import Path

import requests
from flask_testing import TestCase, LiveServerTestCase

from my_app import create_app, db, config
from my_app.models import User, Profile


class BaseTestCase(TestCase, LiveServerTestCase):
    """
    Base test case
    Creates test client and setup and teardown for Flask client tests
    """

    user_data = dict(firstname='TestFirstname2', lastname='TestLastname2', email='test2@testmail.org', password='test2')
    profile_data = dict(username='test2', bio='Something about test2.', area='Barnet')
    test_user = dict(firstname='TestFirstname1', lastname='TestLastname1', email='test1@testmail.org',
                     password='test1', username='test1', bio='Something about test1.', area='Barnet')

    def create_app(self):
        app = create_app(config.TestingConfig)
        return app

    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        self.assertEqual(response.status_code, 200)

    def login(self, email, password):
        return self.client.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(
            '/logout',
            follow_redirects=True
        )

    def setUp(self):
        db.session.commit()
        db.drop_all()
        db.create_all()
        # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
        csv_file = Path(__file__).parent.parent.joinpath("data/household_recycling.csv")
        df = pd.read_csv(csv_file, usecols=['Code', 'Area'])
        df.drop_duplicates(inplace=True)
        df.set_index('Code', inplace=True)
        df.to_sql('area', db.engine, if_exists='replace')
        # Add a user and profile to the database
        u = User(firstname='TestFirstname1', lastname='TestLastname1', email='test1@testmail.org')
        u.set_password('test1')
        p = Profile(username='test1', bio='Something about test1.', area='Barnet', user_id=u.id)
        u.profiles.append(p)
        db.session.add(u)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
