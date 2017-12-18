"""
Amazon AWS boto3 helper libs
"""

__version__ = "0.1.16"
__license__ = "MIT License"
__website__ = "https://oss.navio.tech/navio-aws/"
__download_url__ = 'https://github.com/naviotech/navio-aws/archive/{}.tar.gz'.format(__version__),

from navio.aws.services._iam import AWSIAM
from navio.aws.services._session import AWSSession
from navio.aws.services._cloudformation import AWSCloudFormation
from navio.aws.services._lambda import AWSLambda
from navio.aws.services._s3 import AWSS3
from navio.aws.services._cloudfront import AWSCloudFront

import pkgutil
__path__ = pkgutil.extend_path(__path__,__name__)

__all__ = ['AWSLambda', 'AWSCloudFormation', 'AWSIAM', 'AWSS3', 'AWSCloudFront', 'AWSSession']
