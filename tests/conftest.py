import multiprocessing
from pathlib import Path
import pytest
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions

from my_app import create_app
from my_app import db as _db
from my_app.config import TestingConfig


@pytest.fixture(scope='session')
def app(request):
    """ Returns a session wide Flask app """
    _app = create_app(TestingConfig)
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope='session')
def client(app):
    """ Exposes the Werkzeug test client for use in the tests. """
    return app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Returns a session wide database using a Flask-SQLAlchemy database connection.
    """
    _db.app = app
    _db.create_all()
    # Add the local authority data to the database (this is a workaround you don't need this for your coursework!)
    csv_file = Path(__file__).parent.parent.joinpath("data/household_recycling.csv")
    df = pd.read_csv(csv_file, usecols=['Code', 'Area'])
    df.drop_duplicates(inplace=True)
    df.set_index('Code', inplace=True)
    df.to_sql('area', _db.engine, if_exists='replace')

    yield _db

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db):
    """ Rolls back database changes at the end of each test """
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_

    yield session_

    transaction.rollback()
    connection.close()
    session_.remove()


@pytest.fixture(scope='function')
def user(db):
    """ Creates a user without a profile. """
    from my_app.models import User
    user = User(firstname="Person", lastname='One', email='person1@people.com')
    user.set_password('password1')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def user_with_profile(db):
    """ Creates a user with a profile with a username and bio """
    from my_app.models import User, Profile
    user = User(firstname='Person', lastname='Three', email='person3@people.com')
    user.profile = Profile(username='person3',
                           bio="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam ac tempor metus. "
                               "Aenean mattis, tortor fringilla iaculis pharetra, dui justo imperdiet turpis, "
                               "at faucibus risus eros vitae dui. Nam finibus, nibh eu imperdiet feugiat, nisl lacus "
                               "porta tellus, a tincidunt nibh enim in urna. Aliquam commodo volutpat ligula at "
                               "tempor. In risus mauris, commodo id mi non, feugiat convallis ex. Nam non odio dolor. "
                               "Cras egestas mollis feugiat. Morbi ornare laoreet varius. Pellentesque fringilla "
                               "convallis risus, sit amet laoreet metus interdum et.")
    user.set_password('password3')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='class')
def chrome_driver(request):
    """ Fixture for selenium webdriver with options to support running in GitHub actions"""
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    chrome_driver = webdriver.Chrome(options=options)
    request.cls.driver = chrome_driver
    yield
    chrome_driver.close()


@pytest.fixture(scope='class')
def run_app(app):
    """
    Fixture to run the Flask app
    A better alternative may be to use pytest-flask live_server
    """
    process = multiprocessing.Process(target=app.run, args=())
    process.start()
    yield process
    process.terminate()


def login(client, email, password):
    return client.post('/login/', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout/', follow_redirects=True)
