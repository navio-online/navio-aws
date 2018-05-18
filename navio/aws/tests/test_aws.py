import pytest
import re
import sys


class TestAWS:

    def test_import(self):
        import navio.aws


class TestAWSSession:

    def test_import(self):
        from navio.aws import AWSSession


class TestAWSCloudFormation:

    def test_import(self):
        from navio.aws import AWSCloudFormation


class TestAWSCloudFront:

    def test_import(self):
        from navio.aws import AWSCloudFront


class TestAWSLambda:

    def test_import(self):
        from navio.aws import AWSLambda


class TestAWSS3:

    def test_import(self):
        from navio.aws import AWSS3


class TestAWSIAM:

    def test_import(self):
        from navio.aws import AWSIAM


class TestAWSEC2:

    def test_import(self):
        from navio.aws import AWSEC2

class TestAWSACM:

    def test_import(self):
        from navio.aws import AWSACM
