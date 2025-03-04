import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def register_url():
    return reverse('users:register')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def test_user_email():
    return 'test_user@example.com'


@pytest.fixture
def test_user_password():
    return 'test_password12345'


@pytest.fixture
def test_user(user_model, test_user_email, test_user_password):
    """Create and return a test user"""
    User = user_model
    return User.objects.create_user(
        email=test_user_email,
        password=test_user_password
    )


@pytest.fixture
def user_model():
    return get_user_model()


@pytest.mark.django_db
class TestAuthAPI:
    """
    Tests Auth endpoints.
    """

    def test_register_user(
        self, api_client, register_url, user_model, test_user_email, test_user_password
    ):
        User = user_model

        assert not User.objects.filter(email=test_user_email).exists()

        new_user = {"email": test_user_email, "password": test_user_password}
        response = api_client.post(register_url, new_user)

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert User.objects.filter(email=test_user_email).exists()

    def test_cannot_register_user_email_already_exists(
        self, api_client, register_url, user_model, test_user, test_user_password
    ):
        User = user_model
        initial_user_count = User.objects.count()
        new_user = {"email": test_user.email, "password": test_user_password}
        response = api_client.post(register_url, new_user)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data["email"] == ["custom user with this email already exists."]
        assert User.objects.count() == initial_user_count

    def test_login_user(self, api_client, login_url, user_model, test_user, test_user_password):
        User = user_model

        assert User.objects.filter(email=test_user.email).exists()

        user_data = {"email": test_user.email, "password": test_user_password}
        response = api_client.post(login_url, user_data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_cannot_login_user_not_exists(
        self, api_client, login_url, user_model, test_user_email, test_user_password
    ):
        User = user_model

        assert not User.objects.filter(email=test_user_email).exists()

        user_data = {"email": test_user_email, "password": test_user_password}
        response = api_client.post(login_url, user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
