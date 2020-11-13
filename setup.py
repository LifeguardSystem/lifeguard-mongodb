from setuptools import setup, find_packages
from lifeguard_mongodb import VERSION

setup(
    name="lifeguard-mongodb",
    version=VERSION,
    url="https://github.com/LifeguardSystem/lifeguard-mongodb",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=[],
    include_package_data=True,
    description="Lifeguard integration with MongoDB",
    install_requires=["lifeguard", "pymongo"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
