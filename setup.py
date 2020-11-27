import setuptools

setuptools.setup(
    name="qt_grbl-dek", # Replace with your own username
    version="0.0.1",
    author="David Konerding",
    author_email="dek@konerding.com",
    description="A small example package",
    url="https://github.com/dakoner/qt_grbl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
