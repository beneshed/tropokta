from setuptools import setup

setup(
    name='tropokta',
    versoin='0.0.1-alpha',
    description='Custom Okta Resources for AWS Cloudformation',
    author='Ben Waters',
    author_email='bsawyerwaters@gmail.com',
    url="https://github.com/thebenwaters/tropokta",
    license="MIT",
    packages=['tropokta'],
    install_requires=[
        'troposphere'
    ],
    use_2to3=True
)