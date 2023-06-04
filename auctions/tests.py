from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from auctions.models import Category

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_login_view_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'invalidpass'
        })
        self.assertTemplateUsed(response, 'auctions/login.html')
        self.assertContains(response, 'Invalid username or password.')

    def test_logout_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_register_view_with_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirmation': 'newpass123'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_register_view_with_passwords_not_matching(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirmation': 'notmatchingpass'
        })
        self.assertTemplateUsed(response, 'auctions/register.html')
        self.assertContains(response, 'Passwords must match.')

    def test_register_view_with_missing_data(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': '',
            'password': '',
            'confirmation': ''
        })
        self.assertTemplateUsed(response, 'auctions/register.html')
        self.assertContains(response, 'Form is not valid.')


class UserModelUnitTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='john@test.com', username='John', password='pass123')

    def test_user_model(self):
        data = self.user
        self.assertTrue(isinstance(data, User))
        self.assertIsInstance(data, User)
        self.assertEqual(str(data.username), 'John')


class CategoryUnitTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(category_name='Books')

    def test_food_category_model(self):
        data = self.category
        self.assertIsInstance(data, Category)
        self.assertEqual(str(data.category_name), 'Books')


class IndexRequestTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
