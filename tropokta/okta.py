from troposphere import AWSObject


class OktaUser(AWSObject):
    resource_type = "Custom::OktaUser"

    props = {
        'ServiceToken': (basestring, True),
        'firstName': (baseString, True),
        'lastName': (baseString, True),
        'email': (baseString, True),
        'login': (baseString, True)
    }


class OktaGroup(AWSObject):
    resource_type = "Custom::OktaGroup"

    props = {
        'ServiceToken': (basestring, True),
        'name': (basestring, True),
        'description': (basestring, True)
    }


class OktaUserGroupAttachment(AWSObject):
    resource_type = "Custom::OktaUserGroupAttachment"

    props = {
        'ServiceToken': (basestring, True),
        'groupId': (basestring, True),
        'userId': (basestring, True)
    }
