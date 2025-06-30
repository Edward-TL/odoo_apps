from setuptools import setup, find_packages

setup(
    author = "Edward Toledo Lopez",
    description = "A traduction of Oddo's RPC into classes.",
    name = "odoo_apps",
    version = "0.3.1",
    packages=find_packages(
        include=[
            "requests (>=2.32.3,<3.0.0)",
            "pandas (>=2.2.3,<3.0.0)",
            "openpyxl (>=3.1.5,<4.0.0)",
            "python-dotenv (>=1.1.0,<2.0.0)",
            "pydantic (>=2.11.4,<3.0.0)",
            "pytest (>=8.3.5,<9.0.0)",
            "pytz (>=2025.2,<2026.0)",
            "flask (>=3.1.1,<4.0.0)"
        ]
    )
)
