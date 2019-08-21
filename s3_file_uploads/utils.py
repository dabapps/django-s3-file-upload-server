from django.conf import settings
from rest_framework.exceptions import ValidationError

def validate_acl_type(data):
    if data and data.get('acl') not in settings.ACCESS_CONTROL_TYPES:
        raise ValidationError('{acl} is not a valid acl type'.format(acl=data.get('acl')))
    return data


def get_file_data_from_request_data(request_data):
    return {
        k: v
        for k, v
        in request_data.items()
        if k != 'acl'
    }

def get_acl_data_from_request_data(request_data):
    return {
        k: v
        for k, v
        in request_data.items()
        if k == 'acl'
    }
