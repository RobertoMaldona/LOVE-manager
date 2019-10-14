"""Test the UI Framework API."""
import json
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import serializers, status
from rest_framework.test import APIClient
from api.models import Token
from ui_framework.models import Workspace, View, WorkspaceView


class WorkspaceCrudTestCase(TestCase):
    """Test the workspace CRUD API."""

    def setUp(self):
        """Testcase setup."""
        # Arrange
        self.client = APIClient()
        self.login_url = reverse('login')
        self.username = 'test'
        self.password = 'password'
        self.user = User.objects.create_user(
            username=self.username,
            password='password',
            email='test@user.cl',
            first_name='First',
            last_name='Last',
        )
        self.setup_ts = timezone.now()
        self.setup_ts_str = serializers.DateTimeField().to_representation(self.setup_ts)

        with freeze_time(self.setup_ts):
            self.views_data = [
                {
                    'name': 'My View 1',
                    'data': json.dumps({"data_name": "My View 1"}),
                },
                {
                    'name': 'My View 2',
                    'data': json.dumps({"data_name": "My View 2"}),
                },
                {
                    'name': 'My View 3',
                    'data': json.dumps({"data_name": "My View 3"}),
                },
                {
                    'name': 'My View 4',
                    'data': json.dumps({"data_name": "My View 4"}),
                }
            ]
            self.workspaces_data = [
                {'name': 'My Workspace 1'},
                {'name': 'My Workspace 2'},
                {'name': 'My Workspace 3'},
            ]
            self.views = []
            self.workspaces = []
            for i in range(0, len(self.views_data)):
                self.views.append(View.objects.create(**self.views_data[i]))

            for i in range(0, len(self.workspaces_data)):
                aux = Workspace.objects.create(**self.workspaces_data[i])
                self.workspaces_data[i]['id'] = aux.id
                self.workspaces.append(aux)
                self.workspaces[i].views.add(self.views[i])
                self.workspaces[i].views.add(self.views[i + 1])
        self.old_count = Workspace.objects.count()

    def client_login(self):
        """Perform a login for the APIClient."""
        data = {'username': self.username, 'password': self.password}
        self.client.post(self.login_url, data, format='json')
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_list_workspaces(self):
        """Test that the list of workspaces can be retrieved through the API."""
        # Arrange
        self.client_login()

        # Act
        response = self.client.get(reverse('workspace-list'))

        # Assert
        expected_data = []
        for i in range(0, len(self.workspaces_data)):
            expected_data.append({
                'id': self.workspaces_data[i]['id'],
                'name': self.workspaces_data[i]['name'],
                'creation_timestamp': self.setup_ts_str,
                'update_timestamp': self.setup_ts_str,
                'views': [v.pk for v in self.views[i: i + 2]],
            })

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = [dict(w) for w in response.data]
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_create_workspaces(self):
        """Test that a workspace can be created through the API."""
        # Arrange
        self.client_login()
        given_data = {
            'name': 'My New Workspace',
            'views': [],
        }

        # Act
        response = self.client.post(reverse('workspace-list'), given_data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'The request failed')
        self.new_count = Workspace.objects.count()
        self.assertEqual(self.old_count + 1, self.new_count, 'A new object should have been created in the DB')
        new_workspace = Workspace.objects.get(name=given_data['name'])
        new_workspace_views = [v.pk for v in new_workspace.views.all()]
        self.assertEqual(new_workspace_views, given_data['views'], 'Retrieved views are not as expected')

    def test_retrieve_workspaces(self):
        """Test that a workspace can be retrieved through the API."""
        # Arrange
        self.client_login()
        workspace_data = self.workspaces_data[0]
        # Act
        response = self.client.get(reverse('workspace-detail', kwargs={'pk': workspace_data['id']}))

        # Assert
        expected_data = {
            'id': workspace_data['id'],
            'name': workspace_data['name'],
            'creation_timestamp': self.setup_ts_str,
            'update_timestamp': self.setup_ts_str,
            'views': [v.pk for v in self.views[0:2]],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = dict(response.data)
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_update_workspaces(self):
        """Test that a workspace can be updated through the API."""
        # Arrange
        self.client_login()
        workspace = self.workspaces[0]
        given_data = {
            'name': 'My New Workspace',
        }
        # Act
        self.update_ts = timezone.now()
        self.update_ts_str = serializers.DateTimeField().to_representation(self.update_ts)
        with freeze_time(self.update_ts):
            response = self.client.put(reverse('workspace-detail', kwargs={'pk': workspace.pk}), given_data)

        # Assert
        expected_data = {
            'id': workspace.id,
            'name': given_data['name'],
            'creation_timestamp': self.setup_ts_str,
            'update_timestamp': self.update_ts_str,
            'views': [v.pk for v in self.views[0:2]],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = dict(response.data)
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_delete_workspaces(self):
        """Test that a workspace can be deleted through the API."""
        # Arrange
        self.client_login()
        workspace_pk = self.workspaces[0].pk
        # Act
        response = self.client.delete(reverse('workspace-detail', kwargs={'pk': workspace_pk}))

        # Assert
        self.new_count = Workspace.objects.count()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'The request failed')
        self.assertEqual(self.old_count - 1, self.new_count, 'The number of objects in the DB have decreased by 1')
        with self.assertRaises(Exception):
            Workspace.objects.get(pk=workspace_pk)


class ViewCrudTestCase(TestCase):
    """Test the view CRUD API."""

    def setUp(self):
        """Testcase setup."""
        # Arrange
        self.client = APIClient()
        self.login_url = reverse('login')
        self.username = 'test'
        self.password = 'password'
        self.user = User.objects.create_user(
            username=self.username,
            password='password',
            email='test@user.cl',
            first_name='First',
            last_name='Last',
        )
        self.setup_ts = timezone.now()
        self.setup_ts_str = serializers.DateTimeField().to_representation(self.setup_ts)

        with freeze_time(self.setup_ts):
            self.views_data = [
                {
                    'name': 'My View 1',
                    'data': json.dumps({"data_name": "My View 1"}),
                },
                {
                    'name': 'My View 2',
                    'data': json.dumps({"data_name": "My View 2"}),
                },
                {
                    'name': 'My View 3',
                    'data': json.dumps({"data_name": "My View 3"}),
                },
                {
                    'name': 'My View 4',
                    'data': json.dumps({"data_name": "My View 4"}),
                }
            ]
            self.workspaces_data = [
                {'name': 'My Workspace 1'},
                {'name': 'My Workspace 2'},
                {'name': 'My Workspace 3'},
            ]
            self.views = []
            self.workspaces = []
            for i in range(0, len(self.views_data)):
                aux = View.objects.create(**self.views_data[i])
                self.views_data[i]['id'] = aux.id
                self.views.append(aux)

            for i in range(0, len(self.workspaces_data)):
                aux = Workspace.objects.create(**self.workspaces_data[i])
                self.workspaces_data[i]['id'] = aux.id
                self.workspaces.append(aux)
                self.workspaces[i].views.add(self.views[i], through_defaults={'view_name': 'v{}'.format(i)})
                self.workspaces[i].views.add(self.views[i + 1], through_defaults={'view_name': 'v{}'.format(i)})
        self.old_count = View.objects.count()

    def client_login(self):
        """Perform a login for the APIClient."""
        data = {'username': self.username, 'password': self.password}
        self.client.post(self.login_url, data, format='json')
        self.token = Token.objects.get(user__username=self.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_list_views(self):
        """Test that the list of views can be retrieved through the API."""
        # Arrange
        self.client_login()

        # Act
        response = self.client.get(reverse('view-list'))

        # Assert
        expected_data = [
            {
                'id': view['id'],
                'creation_timestamp': self.setup_ts_str,
                'update_timestamp': self.setup_ts_str,
                'name': view['name'],
                'data': view['data'],
            } for view in self.views_data
        ]
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = [dict(v) for v in response.data]
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_create_views(self):
        """Test that a view can be created through the API."""
        # Arrange
        self.client_login()
        given_data = {
            "name": "My New View",
            "views": [],
            "data": '{"data_name": "My New View"}'
        }

        # Act
        response = self.client.post(reverse('view-list'), given_data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'The request failed')
        self.new_count = View.objects.count()
        self.assertEqual(self.old_count + 1, self.new_count, 'A new object should have been created in the DB')
        new_view = View.objects.get(name=given_data['name'])
        self.assertEqual(new_view.data, json.loads(given_data['data']), 'Retrieved data is not as expected')

    def test_retrieve_views(self):
        """Test that a view can be retrieved through the API."""
        # Arrange
        self.client_login()
        data = self.views_data[0]
        # Act
        response = self.client.get(reverse('view-detail', kwargs={'pk': data['id']}))

        # Assert
        expected_data = {
            'id': data['id'],
            'name': data['name'],
            'creation_timestamp': self.setup_ts_str,
            'update_timestamp': self.setup_ts_str,
            'data': data['data'],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = dict(response.data)
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_update_views(self):
        """Test that a view can be updated through the API."""
        # Arrange
        self.client_login()
        data = self.views_data[0]
        given_data = {
            "name": "My New Workspace",
            "data": '{"data_name": "My New View"}'
        }
        # Act
        self.update_ts = timezone.now()
        self.update_ts_str = serializers.DateTimeField().to_representation(self.update_ts)
        with freeze_time(self.update_ts):
            response = self.client.put(reverse('view-detail', kwargs={'pk': data['id']}), given_data)

        # Assert
        expected_data = {
            'id': data['id'],
            'name': given_data['name'],
            'creation_timestamp': self.setup_ts_str,
            'update_timestamp': self.update_ts_str,
            'data': json.loads(given_data['data']),
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'The request failed')
        retrieved_data = dict(response.data)
        self.assertEqual(retrieved_data, expected_data, 'Retrieved data is not as expected')

    def test_delete_views(self):
        """Test that a view can be deleted through the API."""
        # Arrange
        self.client_login()
        view_pk = self.views[0].pk
        # Act
        response = self.client.delete(reverse('view-detail', kwargs={'pk': view_pk}))

        # Assert
        self.new_count = View.objects.count()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'The request failed')
        self.assertEqual(self.old_count - 1, self.new_count, 'The number of objects in the DB have decreased by 1')
        with self.assertRaises(Exception):
            View.objects.get(pk=view_pk)
