import boto3, botocore

class AWSSession(object):

  def __init__(self, profile_name):
    self.profile_name = profile_name

    if profile_name in boto3.session.Session().available_profiles:
      self.session = boto3.session.Session(profile_name = self.profile_name)
    else:
      self.session = boto3.session.Session()

  def client(self, name):
    return self.session.client(name)
