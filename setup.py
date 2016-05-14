"""
Leapsight Semantic Dataspace Command Line Tool
"""
from setuptools import find_packages, setup

dependencies = ['click', 'prompt-toolkit', 'requests', 'pygments', 'tabulate', 'xtermcolor']

setup(
    name='lsd-cli',
    version='0.1.4',
    url='https://github.com/frepond/lsd-cli',
    license='BSD',
    author='Federico Repond',
    author_email='federico.repond@leapsight.com',
    description='Leapsight Semantic Dataspace Command Line Tool',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'lsd-cli = lsd_cli.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        # 'Operating System :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
