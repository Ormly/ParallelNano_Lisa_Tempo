import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TPRO",
    version="0.0.1",
    author="Marcos Ortego & Mohab Osman",
    author_email="ortego@mail.hs-ulm.de & osman@mail.hs-ulm.de",
    description="Sensor data publishing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ormly/ParallelNano_Lisa_Tempo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "python-daemon",
        "ipcqueue"
    ]
)
