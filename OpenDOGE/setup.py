from setuptools import setup, find_packages

setup(
    name="opendoge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.7.0",
    ],
) 