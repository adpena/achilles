import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="achilles",
    version="0.0.193",
    author="Alejandro Peña",
    author_email="adpena@gmail.com",
    description="Distributed/parallel computing in modern Python based on the multiprocessing.Pool API (map, imap, imap_unordered).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adpena/achilles",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=["dill", "python-dotenv", "twisted", "pyyaml", "multiprocess"],
)
