from setuptools import setup
from tendenci import __version__ as version

REQUIRED_PYTHON = (3, 6)

def _is_requirement(line):
    """Returns whether the line is a valid package requirement."""
    line = line.strip()
    return line and not line.startswith("#")

def _read_requirements():
    """Parses the file requirements.txt for pip installation requirements.
    Returns the list of package requirements.
    """
    requirements = []
    with open("requirements.txt", 'r') as fh:
        for line in fh:
            if _is_requirement(line):
                requirements.append(line.strip().strip('\n'))
    return requirements

DESCRIPTION = "Tendenci - The Open Source Association Management System (AMS)"

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='tendenci',
    version=version,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    packages=['tendenci'],
    package_dir={'tendenci': 'tendenci'},
    include_package_data=True,
    author='Tendenci',
    author_email='programmers@tendenci.com',
    url='https://github.com/tendenci/tendenci/',
    license='GPL3',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=_read_requirements(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    entry_points="""
        [console_scripts]
        tendenci=tendenci.bin.tendenci:main
    """
)
