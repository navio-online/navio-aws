from setuptools import setup
import navio.builder
setup(
    name="navio-aws",
    version=navio.aws.__version__,
    author="Peter Salnikov",
    author_email="peter@navio.tech",
    url=navio.aws.__website__,
    packages=["navio", "navio.aws"],
    license="MIT License",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords=['framework'],
    description="Amazon AWS boto3 helper libs.",
    long_description=open("README.rst").read()+"\n"+open("CHANGES.rst").read()
)
