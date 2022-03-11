import setuptools
from glob import glob

setuptools.setup(
    name="SmartPXE",
    version="0.5.1",
    author="lcp",
    author_mail="lcp@linux98.com",
    description="SmartPXE Devops Management",
    url="https://www.linux98.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    python_requires=">=3.8.0",
    data_files=[
        ('', ['requirements']),
        ('', glob('service_conf/**')),
        ('', glob('frontends/**/*', recursive=True))
    ],
    py_modules=['manage']
)
