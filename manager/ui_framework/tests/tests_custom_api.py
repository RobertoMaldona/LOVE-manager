"""Test the UI Framework Custom API."""
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from rest_framework import status
from api.models import Token
from ui_framework.models import View
from ui_framework.tests.utils import BaseTestCase


class AuthorizedCrudTestCase(BaseTestCase):
    """Test that authorized users can use the CRUD API."""

    def setUp(self):
        """Set testcase. Inherits from utils.BaseTestCase."""
        # Arrange
        super().setUp()
        self.login_url = reverse("login")
        self.username = "test"
        self.password = "password"
        self.user = User.objects.create_user(
            username=self.username,
            password="password",
            email="test@user.cl",
            first_name="First",
            last_name="Last",
        )
        data = {"username": self.username, "password": self.password}
        self.client.post(self.login_url, data, format="json")
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_workspaces_with_view_name(self):
        """Test that authorized users can retrieve the list of available workspaces, with views ids and names."""
        # Arrange
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_workspace")
        )
        expected_data = [
            {
                **w,
                "views": [
                    {
                        "id": v_pk,
                        "name": v.name,
                        "thumbnail": None
                        if v.thumbnail.name == "" or v.thumbnail.name is None
                        else settings.MEDIA_URL + str(v.thumbnail.name),
                    }
                    for v_pk in w["views"]
                    for v in [View.objects.get(pk=v_pk)]
                ],
            }
            for w in self.workspaces_data
        ]
        # Act
        url = reverse("workspace-with-view-name")
        response = self.client.get(url)
        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Retrieving list of workspaces did not return status 200",
        )
        retrieved_data = [dict(data) for data in response.data]
        self.assertEqual(
            retrieved_data,
            expected_data,
            "Retrieved list of workspaces is not as expected",
        )

    def test_get_full_workspace(self):
        """Test that authorized users can retrieve a workspace with all its views fully subserialized."""
        # Arrange
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_workspace")
        )
        w = self.workspaces_data[0]
        expected_data = {**w, "views": self.views_data[0:2]}

        # Act
        url = reverse("workspace-full", kwargs={"pk": w["id"]})
        response = self.client.get(url)
        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Retrieving list of workspaces did not return status 200",
        )
        retrieved_data = dict(response.data)
        self.assertEqual(
            retrieved_data,
            expected_data,
            "Retrieved list of workspaces is not as expected",
        )
