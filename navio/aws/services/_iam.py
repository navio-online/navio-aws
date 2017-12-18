import boto3, botocore
import os, uuid
from botocore.exceptions import ClientError
from pyntaws.services._session import AWSSession
from pyntaws._common import generatePassword


import __builtin__

class AWSIAM(AWSSession):

  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(kwargs['profile_name'])
    __builtin__.aws_iam = self

  def create_access_key(self, **kwargs):
    resp = self.session.client('iam').create_access_key(
      UserName = kwargs.get('username')
    )

    if 'print_credentials' in kwargs and bool(kwargs['print_credentials']):
      print """
[{}.ci]
aws_access_key_id = {}
aws_secret_access_key = {}
      """.format(self.profile_name, resp['AccessKeyId'], resp['SecretAccessKey'])
    else:
      return resp['AccessKey']

  def create_password(self, **kwargs):
    aws_iam = self.session.client('iam')

    account_alias = self.get_signin_url()

    login_profile = None

    try:
      aws_iam.delete_login_profile(UserName = kwargs.get('username'))
      login_profile = aws_iam.get_login_profile(UserName = kwargs.get('username'))
    except ClientError as e:
      if e.response["Error"]["Code"] == "NoSuchEntity":
        pass
      else:
        raise e

    password = generatePassword()

    if not login_profile:
      aws_iam.create_login_profile(
        UserName = kwargs.get('username'),
        Password = password,
        PasswordResetRequired = True
      )
    else:
      aws_iam.update_profile(
        UserName = kwargs.get('username'),
        Password = password,
        PasswordResetRequired = True
      )

    if 'print_password' in kwargs and bool(kwargs['print_password']):
      print """
Signin URL: https://{}.signin.aws.amazon.com/console
Username: {}
Password: {}
""".format(account_alias, kwargs.get('username'), password)
    else:
      return password      

  def get_signin_url(self):
    aws_iam = self.session.client('iam')
    resp = aws_iam.list_account_aliases()

    if len(resp['AccountAliases']) != 1:
      raise Exception('Account aliases not equal to 1')
    
    return resp['AccountAliases'][0]

