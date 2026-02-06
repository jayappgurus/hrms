from setuptools import setup, find_packages

setup(
    name='hrms-portal',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django==5.1.5',
        'mysql-connector-python==8.2.0',
        'Pillow>=10.4.0',
        'python-decouple==3.8',
        'django-crispy-forms==2.1',
        'crispy-bootstrap5==0.7',
    ],
)
