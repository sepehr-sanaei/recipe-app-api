"""
Tests for tags APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    """Create and return tag detail URL."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='test@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagApiTest(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self):
        self.client = APIClient()

    def test_list_tags_for_unauthenticated_users(self):
        """Test listing tag names for unauthenticated users."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Test Authenticated API Requests."""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        Tag.objects.create(user=self.user, name='Vagrant')
        Tag.objects.create(user=self.user, name='Docker')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limited_to_user(self):
        """Test that retrieved tags are limited to current user."""
        new_user = create_user(email='new@example.com')
        Tag.objects.create(user=new_user, name='Hello')
        tag = Tag.objects.create(user=self.user, name='Good')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tags(self):
        """Test updating tags."""
        tag = Tag.objects.create(user=self.user, name='Sample Tag')
        payload = {'name': 'New Tag'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tags(self):
        """Test deleting tags."""
        tag = Tag.objects.create(user=self.user, name='Sample')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())

    def test_filter_Tags_assigned_to_recipes(self):
        """Test listing Tags by those assigned to recipes."""
        tag1 = Tag.objects.create(user=self.user, name='Apple')
        tag2 = Tag.objects.create(user=self.user, name='Tomato')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Sample Title',
            time_minutes=100,
            price=Decimal('5.99')
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_Tags_unique(self):
        """Test filtered Tags return a unique list."""
        tag = Tag.objects.create(user=self.user, name='Apple')
        Tag.objects.create(user=self.user, name='Banana')
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
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
