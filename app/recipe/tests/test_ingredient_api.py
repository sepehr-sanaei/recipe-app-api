"""
Tests for ingredient APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)

from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return the detail url for an ingredient."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.cilent = APIClient()

    def test_retrieve_ingridients(self):
        """test retrieving ingridients for unauthenticated users."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving ingredients for authenticated users."""
        Ingredient.objects.create(user=self.user, name='Soup')
        Ingredient.objects.create(user=self.user, name='Rice')
        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_limited_to_authenticated_user(self):
        """
        Test that retrieving ingredients only
        return objects limited to user.
        """
        user_2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user_2, name='Soup')
        ingredient = Ingredient.objects.create(user=self.user, name='Rice')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_tags(self):
        """Test updating ingredients."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Soup'
        )
        payload = {'name': 'Rice'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleteing an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Soup'
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        ing1 = Ingredient.objects.create(user=self.user, name='Apple')
        ing2 = Ingredient.objects.create(user=self.user, name='Tomato')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Sample Title',
            time_minutes=100,
            price=Decimal('5.99')
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredients_unique(self):
        """Test filtered ingredients return a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Apple')
        Ingredient.objects.create(user=self.user, name='Banana')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Sample Recipe',
            time_minutes=100,
            price=Decimal('5.77')
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Sample Recipe 2',
            time_minutes=200,
            price=Decimal('6.99')
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
