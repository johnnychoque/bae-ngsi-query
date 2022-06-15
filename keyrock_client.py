# -*- coding: utf-8 -*-

# Copyright (c) 2019 Future Internet Consulting and Development Solutions S.L.

# This file is part of BAE NGSI Dataset plugin.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from urlparse import urlparse
from os import environ

from django.conf import settings as django_settings
from django.core.exceptions import PermissionDenied

from wstore.asset_manager.resource_plugins.plugin_error import PluginError

IDM_USER = environ.get('BAE_ASSET_IDM_USER', '')
IDM_PASSWORD = environ.get('BAE_ASSET_IDM_PASSWORD', '')
IDM_URL = environ.get('BAE_ASSET_IDM_URL', '')


class KeyrockClient(object):

    def __init__(self):
        self._login()

    def _login(self):
        body = {
            "name": IDM_USER,
            "password": IDM_PASSWORD
        }

        url = IDM_URL + '/v1/auth/tokens'
        response = requests.post(url, json=body, verify=django_settings.VERIFY_REQUESTS)

        response.raise_for_status()
        self._auth_token = response.headers['x-subject-token']

    def check_ownership(self, app_id, provider):
        path = '/v1/applications/{}/users/{}/roles'.format(app_id, provider)
        role_field = 'role_user_assignments'

        assingments_url = IDM_URL + path

        resp = requests.get(assingments_url, headers={
            'X-Auth-Token': self._auth_token
        }, verify=django_settings.VERIFY_REQUESTS)

        resp.raise_for_status()
        assingments = resp.json()

        for assingment in assingments[role_field]:
            if assingment['role_id'] == 'provider':
                break
        else:
            raise PermissionDenied('You are not the owner of the specified IDM application')

    def check_role(self, app_id, role_name):
        # Get available roles
        path = '/v1/applications/{}/roles'.format(app_id)
        roles_url = IDM_URL + path

        resp = requests.get(roles_url, headers={
            'X-Auth-Token': self._auth_token
        }, verify=django_settings.VERIFY_REQUESTS)

        # Get role id
        resp.raise_for_status()
        roles = resp.json()

        for role in roles['roles']:
            if role['name'].lower() == role_name.lower():
                role_id = role['id']
                break
        else:
            raise PluginError('The provided role is not registered in Keyrock')

        return role_id

    def create_role(self, app_id, role_name):
        path = '/v1/applications/{}/roles'.format(app_id)
        roles_url = IDM_URL + path

        role_body = {
            "role": {
                "name": role_name
            }
        }

        resp = requests.post(roles_url, headers={
            'X-Auth-Token': self._auth_token
        }, json=role_body, verify=django_settings.VERIFY_REQUESTS)
        resp.raise_for_status()

        data = resp.json()
        return data['role']['id']

    def check_permission(self, app_id, perm_name):
        # Get available permissions
        path = '/v1/applications/{}/permissions'.format(app_id)
        perm_url = IDM_URL + path

        resp = requests.get(perm_url, headers={
            'X-Auth-Token': self._auth_token
        }, verify=django_settings.VERIFY_REQUESTS)

        # Get permission id
        resp.raise_for_status()
        perms = resp.json()

        for perm in perms['permissions']:
            if perm['name'].lower() == perm_name.lower():
                perm_id = perm['id']
                break
        else:
            raise PluginError('The provided role is not registered in Keyrock')

        return perm_id

    def create_permission(self, info, perm_name):
        path = '/v1/applications/{}/permissions'.format(info['app_id'])
        perm_url = IDM_URL + path

        perm_body = {
            "permission": {
                "name": perm_name,
                "action": info['action'],
                "resource": info['resource'],
                "is_regex": info['is_regex']
            }
        }

        resp = requests.post(perm_url, headers={
            'X-Auth-Token': self._auth_token
        }, json=perm_body, verify=django_settings.VERIFY_REQUESTS)
        resp.raise_for_status()

        data = resp.json()
        return data['permission']['id']

    def assign_permission(self, app_id, role_id, perm_id):
        assign_url = IDM_URL + '/v1/applications/{}/roles/{}/permissions/{}'.format(app_id, role_id, perm_id)

        # Assign a permission to a role
        resp = requests.put(assign_url, headers={
            'X-Auth-Token': self._auth_token,
            'Content-Type': 'application/json'
        }, verify=django_settings.VERIFY_REQUESTS)

        resp.raise_for_status()

    def check_app(self, app_id):
        path = '/v1/applications/{}'.format(app_id)
        app_url = IDM_URL + path

        resp = requests.get(app_url, headers={
            'X-Auth-Token': self._auth_token
        }, verify=django_settings.VERIFY_REQUESTS)

        if resp.status_code != 200:
            raise PluginError('The provided app id is not registered in Keyrock')

    def grant_permission(self, app_id, user, role):
        # Get ids
        role_id = self.check_role(app_id, role)
        assign_url = IDM_URL + '/v1/applications/{}/users/{}/roles/{}'.format(app_id, user.username, role_id)

        # Assign a role to a user
        resp = requests.post(assign_url, headers={
            'X-Auth-Token': self._auth_token,
            'Content-Type': 'application/json'
        }, verify=django_settings.VERIFY_REQUESTS)

        resp.raise_for_status()

    def revoke_permission(self, app_id, user, role):
        role_id = self.check_role(app_id, role)
        assign_url = IDM_URL + '/v1/applications/{}/users/{}/roles/{}'.format(app_id, user.username, role_id)

        resp = requests.delete(assign_url, headers={
            'X-Auth-Token': self._auth_token,
            'Content-Type': 'application/json'
        }, verify=django_settings.VERIFY_REQUESTS)

        resp.raise_for_status()
