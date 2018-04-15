from setuptools import setup

setup(
    name='tropokta',
    version='0.0.2a1',
    description='Custom Okta Resources for AWS Cloudformation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ben Waters',
    author_email='bsawyerwaters@gmail.com',
    url="https://github.com/thebenwaters/tropokta",
    license="MIT",
    packages=['tropokta'],
    install_requires=[
        'troposphere'
    ],
    use_2to3=True,
    classifiers=[
    'Development Status :: 3 - Alpha',
    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    ],
    keywords='okta cf cloudformation'
)