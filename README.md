# tropokta
Custom AWS Cloudformation Resource for Okta Users and Groups

_CAUTION_

* This is ALPHA and has only been testing on a developer instance of Okta and a test AWS account *
_DO NOT USE IN PRODUCTION WITHOUT TESTING_

Install
---
To just use as a custom resource

Make sure to fill out the environment variables
  * OKTA_URL
  * OKTA_TOKEN *encrypted*

Follow online instructions on generating an Okta API Token

```
# Replace YOUR_S3_ARTIFACTS_BUCKET
aws cloudformation package --template-file template.yaml --output-template-file cfn-transformed-template.yaml --s3-bucket YOUR_S3_ARTIFACTS_BUCKET
aws cloudformation deploy --template-file ./cfn-transformed-template.yaml --stack-name okta-cf-resource
```

Now you have
  * Custom::OktaUser
  * Custom::OktaGroup
  * Custom::OktaUserGroupAttachment

Available in CloudFormation

If you install tropokta with

```
python setup.py install
```

You can do the following within troposphere
```
from troposphere import Template
from tropokta.okta import OktaUser

t = Template()

user = t.add_resource(OktaUser(
    firstName="test",
    lastName="user",
    email="test@test.com",
    login="test@test.com"
    ))

print(t.to_json())
```

TO DO
---
[] Tests

