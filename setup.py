import setuptools

# Trigger GitHub Actions workflow with a dummy change
setuptools.setup(
    name="winmail_opener",
    version="1.1.4",
    author="jsbattig",
    author_email="your.email@example.com",  # Replace with a valid email
    description="A simple command-line tool to extract attachments from Winmail.dat files.",
    long_description="A simple command-line tool to extract attachments from Winmail.dat files and display the email body.",
    url="https://github.com/jsbattig/py-winmail-opener",
    py_modules=["winmail_opener"],
    install_requires=[
        "extract_msg",
    ],
    entry_points={
        "console_scripts": [
            "winmail_opener = winmail_opener:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.6',
)
