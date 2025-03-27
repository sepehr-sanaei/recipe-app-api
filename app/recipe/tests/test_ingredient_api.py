"""
Tests for ingredient APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

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
