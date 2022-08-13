import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    readme = f.read()

with open(os.path.join(here, "permasigner", "__version__.py"), encoding="utf-8") as f:
    version = f.read()

version = version.split('=')[-1].strip().strip('"').strip("'")


with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requires = f.readlines()


setup(
    name='permasigner',
    version=version,
    description=('Permanently signs IPAs on jailbroken iDevices (persists on stock).'),
    license='BSD-3-Clause',
    url='https://github.com/itsnebulalol/permasigner',
    python_requires=">=3.7",
    packages=find_packages(),
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
    scripts=['bin/permasigner'],
    keywords='python, windows, macos, linux, docker, cli, open-source, ios, command-line-app, cli-app, hacktoberfest, procursus, permasign, permasigner',
    include_package_data=True,
    author='Nebula',
    install_requires=requires,
    author_email='me@itsnebula.net',
    zip_safe=True,
)
