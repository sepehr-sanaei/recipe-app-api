"""
Test for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample Recipe Title",
            time_minutes=5,
            price=Decimal('5.50'),
            description="Sample recipe description",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a new tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(
            name='Sample Tag',
            user=user
        )
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient'
        )

        self.assertEqual(str(ingredient), ingredient.name)
