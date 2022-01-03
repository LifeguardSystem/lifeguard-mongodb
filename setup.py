from setuptools import find_packages, setup

setup(
    name="lifeguard-mongodb",
    version="0.0.8",
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
