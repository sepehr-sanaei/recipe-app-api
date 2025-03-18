"""
Test for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Test model."""

    def test_user_create_with_email_successful(self):
        """Test creating a user with email is successful."""
        email = 'test@example.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test if the new user's email is being normalized."""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@Example.com', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'Pass1234')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a user without an email raises a value error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'Test1234')

    def test_create_superuser(self):
        """Test creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'Test1234',
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
