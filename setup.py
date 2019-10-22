from setuptools import setup
import versioneer

requirements = [
    # package requirements go here
]

setup(
    name='preprocessing',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Preprocessing of shapefile data for gerrymandering analysis",
    author="Gerrymandr organization",
    author_email='gerrymandr@gmail.com',
    url='https://github.com/gerrymandr/preprocessing',
    packages=['gerry_preprocess'],
    entry_points={
        'console_scripts': [
            'gerry_preprocess=gerry_preprocess.cli:cli'
        ],
        'gui_scripts': [
            'gerryproc_ui=gerry_preprocess.tk_ui:demo'
        ]
    },
    install_requires=requirements,
    keywords='preprocessing',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ]
)
