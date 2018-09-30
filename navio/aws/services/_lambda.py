import boto3
import botocore
import os
import shutil
import zipfile
from boto3.s3.transfer import S3Transfer
from navio.aws.services._session import AWSSession
from navio.aws._common import execute, ls, which
from subprocess import check_call, CalledProcessError
from datetime import datetime

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


class AWSLambda(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(kwargs['profile_name'])
        self.profile_name = kwargs['profile_name']
        self.function_name = kwargs['function_name']
        self.language = kwargs.get('language', 'python')
        self.s3_filename = kwargs['s3_filename']
        self.pip_requirements = kwargs.get('pip_requirements', None)
        self.pip_requirements_file = kwargs.get('pip_requirements_file', None)
        self.npm_requirements = kwargs.get('npm_requirements', None)
        self.npm_package_json = kwargs.get('npm_package_json', None)

        if self.language not in ['python', 'nodejs']:
            raise Exception('Unsupportable language: {}'.format(self.language))

        url = urlparse(kwargs['s3_uri'])
        self.s3_bucket = url.netloc
        self.s3_key = url.path

        if self.s3_key.endswith('/'):
            self.s3_key = "%s%s" % (
                self.s3_key, os.path.basename(self.s3_filename))

        if self.s3_key.startswith('/'):
            self.s3_key = self.s3_key[1:]

    def validate(self):
        self.install_deps(['--user'])
        errors = list()
        files = ls('./src/main/python', '*.py')

        if not which('pylint'):
            print('pylint command not found,'
                  ' skipping code validation via PyLint')
            return True

        if len(files) == 0:
            print("No python files for validation")
            return True
        else:
            print("Validating files via pylint: %s" % files)

        for filename in files:
            try:
                execute('pylint', '--extension-pkg-whitelist=pymssql',
                        '--errors-only', filename)
            except Exception as e:
                errors.append(filename)

        if len(errors) > 0:
            print("There are errors in python files: %s" % errors)
            raise Exception(
                "Lambda validation error. Check output for details.")

        return True

    def package(self):
        print('[ Packaging lambda deployment package ]')
        shutil.rmtree('target/distrib/', ignore_errors=True)

        source_dir = None

        if self.language == 'python':
            if os.path.isdir('src/main/python'):
                source_dir = 'src/main/python'
            elif os.path.isdir('src/python'):
                source_dir = 'src/python'
            else:
                raise Exception('Source dir not found: src/python')
        elif self.language == 'nodejs':
            if os.path.isdir('src/main/nodejs'):
                source_dir = 'src/main/nodejs'
            elif os.path.isdir('src/nodejs'):
                source_dir = 'src/nodejs'
            else:
                raise Exception('Source dir not found: src/nodejs')

        files = ls(source_dir, '*.py')
        cwd = os.getcwd()
        print('[ Files ]')
        for name in files:
            print(name[len(cwd)+1:])

        shutil.copytree(source_dir, 'target/distrib/',
                        ignore=shutil.ignore_patterns('*.pyc', 'tmp*'))

        if self.language == 'python':
            self.install_pip_deps(['--target', 'target/distrib/'])
        elif self.language == 'nodejs':
            self.install_npm_deps(['--prefix', 'target/distrib/', '-g'])

        zipf = zipfile.ZipFile(
            'target/{}'.format(self.s3_filename), 'w', zipfile.ZIP_DEFLATED)

        basedir_len = len(os.path.abspath(
            os.path.join(os.getcwd(), 'target/distrib')))

        for name in ls('target/distrib/'):
            zipf.write(name, name[basedir_len:])

        zipf.close()

        return True

    def install_pip_deps(self, pip_args=None):
        print('[ Installing lambda dependencies (via pip) ]')
        print('[ Dependencies ]')

        args = ['install', '--upgrade']

        if pip_args:
            if type(pip_args) != list:
                raise "pip_args argument should be of a list() type"

            for pip_arg in pip_args:
                if pip_arg == '--user' and os.getenv('VIRTUAL_ENV', False):
                    # skip --user when inside virtualenv
                    pass
                else:
                    args.append(pip_arg)

        if type(self.pip_requirements) == list:
            for req in self.pip_requirements:
                print('Installing {}'.format(req))
                execute('pip', args, req)
        if type(self.pip_requirements_file) == str:
            print('Installing from {}'.format(self.pip_requirements_file))
            args.append('-r')
            execute('pip', args, self.pip_requirements_file)

        if type(self.pip_requirements) is None and type(self.pip_requirements_file) is None:
            print("Your lambda doesn't have any pip dependencies")

    def install_npm_deps(self, npm_args=None):
        print('[ Installing lambda dependencies (via npm) ]')
        print('[ Dependencies ]')

        args = ['install']

        if npm_args:
            if type(npm_args) != list:
                raise "npm_args argument should be of a list() type"

            for npm_arg in npm_args:
                args.append(npm_arg)

        if type(self.npm_requirements) == list:
            for req in self.npm_requirements:
                print('Installing {}'.format(req))
                execute('npm', 'install', args, req)
        if type(self.npm_package_json) == str:
            print('Installing from {}'.format(self.npm_package_json))
            execute('npm', 'install', args, os.path.dirname(self.npm_package_json))

        if type(self.npm_requirements) is None and type(self.npm_requirements_file) is None:
            print("Your lambda doesn't have any npm dependencies")

    def upload(self):
        s3 = self.session.client('s3')
        lambda_package = os.path.normpath(os.path.join(
            os.getcwd(), 'target/', self.s3_filename))
        print("Uploading %s to temporary location s3://%s/%s" %
              (lambda_package, self.s3_bucket, self.s3_key))
        S3Transfer(s3).upload_file(
            lambda_package,
            self.s3_bucket,
            self.s3_key,
            extra_args={'ACL': 'bucket-owner-full-control'}
        )

    def update_code(self, **kwargs):
        lambdas = self.session.client('lambda')
        if kwargs and 'function_name' in kwargs:
            function_name = kwargs['function_name']
        else:
            function_name = self.function_name
        print("Updating function {name} "
              "code from s3://{bucket}/{key}".format(
                  name=function_name,
                  bucket=self.s3_bucket,
                  key=self.s3_key))
        resp = lambdas.update_function_code(
            FunctionName=function_name,
            S3Bucket=self.s3_bucket,
            S3Key=self.s3_key,
            Publish=False
        )

    def update_dev_alias(self):
        lambdas = self.session.client('lambda')
        print('Updating function {} DEV alias to version $LATEST'.format(
            self.function_name))
        lambdas.update_alias(
            FunctionName=self.function_name,
            FunctionVersion='$LATEST',
            Name='DEV',
            Description='Updated by pynt at {} UTC'.format(
                datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S"))
        )

        pass

    def update_prod_alias(self):
        lambdas = self.session.client('lambda')
        resp = lambdas.publish_version(
            FunctionName=self.function_name,
        )

        print('Updating function {} PROD alias to version {}'.format(
            self.function_name, resp['Version']))
        lambdas.update_alias(
            FunctionName=self.function_name,
            FunctionVersion=resp['Version'],
            Name='PROD',
            Description='Updated by pynt at {} UTC'.format(
                datetime.utcnow().strftime("%Y-%b-%d %H:%M:%S"))
        )

    def test_local_python(self, event={}, **kwargs):
        lambdas = self.session.client('lambda')
        if kwargs and 'function_name' in kwargs:
            function_name = kwargs['function_name']
        else:
            function_name = self.function_name
        resp = lambdas.get_function(
            FunctionName=function_name
        )

        sep = resp['Configuration']['Handler'].rfind('.')
        py_file_name = resp['Configuration']['Handler'][:sep]
        py_method_name = resp['Configuration']['Handler'][sep+1:]

        import logging
        logging.basicConfig()
        logger = logging.getLogger('lambda')
        logger.setLevel('DEBUG')

        import sys
        import platform
        if platform.system() == 'Windows':
            sys.path.append('src\\main\\python')
        else:
            sys.path.append('src/main/python')

        import importlib
        mod = importlib.import_module(py_file_name)
        result = getattr(mod, py_method_name)(event, {})
