from rest_framework.exceptions import ValidationError

def validate_acl_type(data):
    if not data:
        return data
    elif data.get('acl') in ['private', 'public-read', 'public-read-write', 'authenticated-read']:
        return data
    raise ValidationError('{acl} is not a valid acl type'.format(acl=data.get('acl')))

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
