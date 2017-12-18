import boto3, botocore
import os, uuid, fnmatch, re
import sh, mimetypes, copy
import uuid
from urlparse import urlparse
from navio.aws.services._session import AWSSession
from concurrent import futures

import __builtin__

class AWSCloudFront(AWSSession):

  def __init__(self, **kwargs):
    super(self.__class__, self).__init__(kwargs['profile_name'])
    __builtin__.aws_cloudfront = self
    self.distribution_id = kwargs.get('distribution_id')

  def invalidate(self, **kwargs):
    cloudfront = self.session.client('cloudfront')
    resp = cloudfront.create_invalidation(
        DistributionId = self.distribution_id,
        InvalidationBatch = {
          'CallerReference': uuid.uuid4().hex,
          'Paths': {
            'Quantity': len(kwargs.get('files')),
            'Items': kwargs.get('files')
          }
        }
      )

