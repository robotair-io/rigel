
import setuptools

with open('./README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='rigel',
    version='0.0.16',
    author='Pedro Melo',
    author_email='pedro.m.melo@inesctec.pt',
    description='Containerize and deploy your ROS application using Docker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Click',
        'docker',
        'jinja2',
        'pyyaml',
        'rich'
    ],
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'rigel=main:main'
        ]
    },
    include_package_data=True
)
