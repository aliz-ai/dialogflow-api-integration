from setuptools import setup, find_packages

REQUIRES = [
    "click",
    "flask",
    "google-cloud-dialogflow-cx",
    "PyYaml"
]

VERSION = "1.0.0"
DESCRIPTION = "Chatbot test"
DESCRIPTION_DETAILS = "A PoC for validating Dialogflow - Userlike integration"

setup(
    name="chatbot",
    version=VERSION,
    description=DESCRIPTION,
    long_description=DESCRIPTION + DESCRIPTION_DETAILS,
    author_email="dev@aliz.ai",
    install_requires=REQUIRES,
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={
        "": ["*.py"],
    },
    entry_points={
        "console_scripts": [
            "chatbot = chatbot.__main__:cli",
        ]
    },
)
