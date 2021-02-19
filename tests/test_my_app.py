from my_app.models import User


class TestMyApp:
    def test_index_page_valid(self, client):
        """
        GIVEN a Flask application is running
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid
        """
        response = client.get('/')
        assert response.status_code == 200

    def test_profile_not_allowed_when_user_not_logged_in(self, client):
        """
        GIVEN A user is not logged
        WHEN When they access the profile menu option
        THEN they should be redirected to the login page
        """
        response = client.get('/community/profile', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_signup_succeeds(self, client):
        """
            GIVEN A user is not registered
            WHEN When they submit a valid registration form
            THEN they the should be redirected to a page with a custom welcome message and there should be an
            additional
            record in the user table in the database
            """
        count = User.query.count()
        response = client.post('/signup', data=dict(
            first_name='Person',
            last_name='Two',
            email='person_2@people.com',
            password='password2',
            password_repeat='password2'
        ), follow_redirects=True)
        count2 = User.query.count()
        assert count2 - count == 1
        assert response.status_code == 200
        assert b'Person' in response.data
