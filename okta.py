import os
import json
import logging
from enum import Enum
from urllib.parse import urljoin
import uuid
from base64 import b64decode

from botocore.vendored import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALLOWED_USER_PROPERTIES = ['firstName', 'lastName', 'login', 'email']

ALLOWED_GROUP_PROPERTIES = ['name', 'description']

ALLOWED_USER_GROUP_ATTACHMENT_PROPERTIES = ['groupId', 'userId']

ENCRYPTED = os.environ['OKTA_TOKEN']
# Decrypt code should run once and variables stored outside of the function
# handler so that these are decrypted once per container
DECRYPTED = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED))['Plaintext'].decode()


class ReturnValue(Enum):
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


HEADERS = {
    'Authorization': 'SSWS {}'.format(DECRYPTED),
    'Content-Type': 'application/json'
}


def make_post(url, data=None):
    if data:
        return requests.post(
            headers=HEADERS,
            url=urljoin(os.getenv('OKTA_URL'), url),
            data=json.dumps(data)
        )
    return requests.post(
        headers=HEADERS,
        url=urljoin(os.getenv('OKTA_URL'), url)
    )


def make_delete(url):
    return requests.delete(
        headers=HEADERS,
        url=urljoin(os.getenv('OKTA_URL'), url)
    )


def make_put(url):
    return requests.put(
        headers=HEADERS,
        url=urljoin(os.getenv('OKTA_URL'), url)
    )


def create_okta_group(properties):
    logger.info('Creating Okta Group')
    data = {
        'profile': {
            'name': properties.get('name'),
            'description': properties.get('description')
        }
    }
    response = make_post(url='/api/v1/groups', data=data)
    if response.status_code != 200:
        return ReturnValue.FAILED.value, response.text, None
    _id = response.json().get('id')
    return ReturnValue.SUCCESS.value, 'DEFAULT', _id


def delete_okta_group(properties):
    logger.info('Deleting Okta Group')
    response = make_delete(url='/api/v1/groups/{}'.format(properties.get('PhysicalResourceId')))
    if response.status_code != 204:
        return ReturnValue.FAILED.value, response.text, properties.get('PhysicalResourceId')
    return ReturnValue.SUCCESS.value, 'DEFAULT', None


def create_okta_user(properties):
    logger.info('Creating Okta User')
    data = {
        'profile': {
            'firstName': properties.get('firstName'),
            'lastName': properties.get('lastName'),
            'email': properties.get('email'),
            'login': properties.get('login')
        }
    }
    response = make_post(url='/api/v1/users?activate=true', data=data)
    if response.status_code != 200:
        return ReturnValue.FAILED.value, response.text, str(uuid.uuid4())
    _id = response.json().get('id')
    return ReturnValue.SUCCESS.value, 'DEFAULT', _id


def delete_okta_user(properties):
    logger.info('Deleting Okta User')
    _ = make_post(url='/api/v1/users/{}/lifecycle/deactivate'.format(properties.get('PhysicalResourceId')))
    response = make_delete(url='/api/v1/users/{}'.format(properties.get('PhysicalResourceId')))
    if response.status_code != 200:
        return ReturnValue.FAILED.value, response.text, properties.get('PhysicalResourceId')
    return ReturnValue.SUCCESS.value, 'DEFAULT', None


def create_okta_user_group_attachment(properties):
    logger.info("Adding User to Group")
    group_id = properties.get('groupId')
    user_id = properties.get('userId')
    response = make_put(url='/api/v1/groups/{group_id}/users/{user_id}'.format(group_id=group_id,
                                                     user_id=user_id))
    if response.status_code != 204:
        return ReturnValue.FAILED.value, response.text, str(uuid.uuid4())
    return ReturnValue.SUCCESS.value, 'DEFAULT', '{}_{}'.format(group_id, user_id)


def delete_okta_user_group_attachment(properties):
    logger.info("Adding User to Group")
    group_id = properties.get('groupId')
    user_id = properties.get('userId')
    response = make_delete(url='/api/v1/groups/{group_id}/users/{user_id}'.format(group_id=group_id,
                                                     user_id=user_id))
    if response.status_code != 204:
        return ReturnValue.FAILED.value, response.text, str(uuid.uuid4())
    return ReturnValue.SUCCESS.value, 'DEFAULT', '{}_{}'.format(group_id, user_id)


user_requests = {
    'Create': create_okta_user,
    'Delete': delete_okta_user
}

group_requests = {
    'Create': create_okta_group,
    'Delete': delete_okta_group
}

user_group_attachment_requests = {
    'Create': create_okta_user_group_attachment,
    'Delete': delete_okta_user_group_attachment
}

request_types = {
    'Custom::OktaUser': user_requests,
    'Custom::OktaGroup': group_requests,
    'Custom::OktaUserGroupAttachment': user_group_attachment_requests
#     'Custom::ExistingOktaUser': user_requests,
#    'Custom::ExistingOktaGroup': group_requests,
}


def lambda_handler(event, context):
    logger.info(event)
    logger.info('Received CF event')
    request_type, response_url = event.get('RequestType'), event.get('ResponseURL')
    stack_id, request_id, logical_resource_id, physical_resource_id, resource_type = event.get('StackId', None), \
                                                                                     event.get('RequestId', None), \
                                                                                     event.get('LogicalResourceId',
                                                                                               None), \
                                                                                     event.get('PhysicalResourceId',
                                                                                               None), \
                                                                                     event.get('ResourceType', None)
    properties = {}
    return_properties = {
        'StackId': stack_id,
        'RequestId': request_id,
        'LogicalResourceId': logical_resource_id,
        'PhysicalResourceId': physical_resource_id
    }
    function_group = request_types.get(resource_type)
    non_empty_return_properties = {}
    for key, value in return_properties.items():
        if value is not None:
            non_empty_return_properties[key] = value
    for key, value in event.get('ResourceProperties').items():
        if 'OktaUser' in resource_type:
            if key in ALLOWED_USER_PROPERTIES:
                properties[key] = value
        if 'OktaGroup' in resource_type:
            if key in ALLOWED_GROUP_PROPERTIES:
                properties[key] = value
        if 'OktaUserGroup' in resource_type:
            if key in ALLOWED_USER_GROUP_ATTACHMENT_PROPERTIES:
                properties[key] = value
    func = function_group.get(request_type)
    if physical_resource_id:
        properties['PhysicalResourceId'] = physical_resource_id
    success, reason, _id = func(properties)
    non_empty_return_properties['Status'] = success
    non_empty_return_properties['Reason'] = reason
    if _id:
        non_empty_return_properties['PhysicalResourceId'] = _id
    requests.put(
        url=response_url,
        data=json.dumps(non_empty_return_properties)
    )
