import copy

from django.test import TestCase

from users.forms import SignUpForm
from users.models import User


class SignUpFormTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.form_payload = {"username": "User",
                            "phone": "(11)999111213",
                            "email": "test@email.com",
                            "institution": "Institution_A",
                            "role": "Engineer",
                            "password1": "123456!!!###",
                            "password2": "123456!!!###"}

    def test_successfull_case(self):
        form = SignUpForm(data=self.form_payload)

        self.assertFalse(bool(form.errors))

    def test_password_didnot_match(self):
        form_payload = copy.deepcopy(self.form_payload)
        form_payload["password2"] = f"{form_payload['password1']}++"

        form = SignUpForm(data=form_payload)

        self.assertEqual(form.errors["password2"], ["The two password fields didn’t match."])


class SignupViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.URL_SIGNUP = "/accounts/signup/"
        cls.form_payload = {"username": "User",
                            "phone": "(11)999111213",
                            "email": "test@email.com",
                            "institution": "Institution_A",
                            "role": "Engineer",
                            "password1": "123456!!!###",
                            "password2": "123456!!!###"}

    def test_successful_signup(self):
        response = self.client.post(self.URL_SIGNUP, data=self.form_payload)

        self.assertRedirects(response, '/', status_code=302)
        self.assertEqual(User.objects.count(), 1)

    def test_failed_signup(self):
        form_payload = copy.deepcopy(self.form_payload)
        form_payload["password2"] = f"{form_payload['password1']}++"

        response = self.client.post(self.URL_SIGNUP, data=form_payload)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signup.html')
        self.assertEqual(User.objects.count(), 0)

    def test_success_get_signup_page(self):
        response = self.client.get(self.URL_SIGNUP)

        self.assertTemplateUsed(response, 'users/signup.html')
