"""
Glance
------

Highlight stack traces in the terminal for easier glancing.


Links
`````

* `Website <http://github.com/joeyespo/glance>`_

"""

import os
from setuptools import setup, find_packages


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='glance',
    version='0.0.1',
    description='Highlight stack traces in the terminal for easier glancing.',
    long_description=__doc__,
    author='Joe Esposito',
    author_email='joe@joeyespo.com',
    url='http://github.com/joeyespo/glance',
    license='MIT',
    platforms='any',
    packages=find_packages(),
    install_requires=read('requirements.txt').splitlines(),
    zip_safe=False,
    entry_points={'console_scripts': ['glance = glance:main']},
)
