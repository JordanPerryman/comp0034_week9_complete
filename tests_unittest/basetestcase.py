import pandas as pd
from pathlib import Path

from flask_testing import TestCase

from my_app import create_app, db, config


class BaseTestCase(TestCase):
    """Base test case."""

    def create_app(self):
        app = create_app(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()
        # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
        csv_file = Path(__file__).parent.parent.joinpath("data/household_recycling.csv")
        df = pd.read_csv(csv_file, usecols=['Code', 'Area'])
        df.drop_duplicates(inplace=True)
        df.set_index('Code', inplace=True)
        df.to_sql('area', db.engine, if_exists='replace')

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post(
            '/login/',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(
            '/logout/',
            follow_redirects=True
        )
