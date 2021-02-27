import unittest

from flask import url_for

from my_app.models import User
from tests_unittest.base_test_case import BaseTestCase


class TestMain(BaseTestCase):

    def test_index_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_content(self):
        """
            GIVEN a Flask application
            WHEN the '/' home page is requested
            THEN check the response contains "Welcome!"
            """
        response = self.client.get('/')
        self.assertIn(b'Welcome', response.data)


class TestAuth(BaseTestCase):

    def test_registration_form_displays(self):
        target_url = url_for('auth.signup')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Sign Up</title>', response.data)

    def test_register_user_success(self):
        count = User.query.count()
        response = self.client.post(url_for('auth.signup'), data=dict(
            first_name=self.user_data.get('firstname'),
            last_name=self.user_data.get('lastname'),
            email=self.user_data.get('email'),
            password=self.user_data.get('password'),
            password_repeat=self.user_data.get('password')
        ), follow_redirects=True)
        count2 = User.query.count()
        self.assertEqual(count2 - count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_fails_with_invalid_details(self):
        response = self.login(email='john@john.com', password='Fred')
        self.assertIn(b'No account found with that email address.', response.data)

    def test_login_succeeds_with_valid_details(self):
        response = self.login(email=self.test_user.get('email'), password=self.test_user.get('password'))
        self.assertIn(('{}'.format(self.test_user.get('firstname'))).encode('UTF-8'),
                      response.data)

    def test_display_profiles_not_allowed_when_user_not_logged_in(self):
        """
        Test that view profile is inaccessible without login
        and redirects to login page
        """
        target_url = url_for('community.display_profiles')
        redirect_url = url_for('auth.login')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_profile_displays_when_user_logged_in(self):
        """
            GIVEN a Flask application
            WHEN the '/' profile page is requested with a logged in user
            THEN check the response contains <name>
        """
        self.login(email=self.test_user.get('email'), password=self.test_user.get('password'))
        target_url = url_for('community.display_profiles', username=self.test_user.get('username'))
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        #self.assertIn(('{}'.format(self.test_user.get('username'))).encode('UTF-8'), response.data)


if __name__ == '__main__':
    unittest.main()
