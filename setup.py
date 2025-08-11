from setuptools import setup, find_packages

setup(
    name="pip_list",
    version="0.1.0",
    description="List installed pip packages with their installed size, supports sorting and filtering.",
    author="Mayank Kumar Poddar",
    license="MIT",
    url="https://github.com/mynkpdr/pip-list",
    author_email="mayankpdr@gmail.com",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pip-list = pip_list.cli:main',
        ],
    },
    python_requires='>=3.6',
)
