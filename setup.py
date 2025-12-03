from setuptools import setup

setup(
    name="deephawk_product_selector",
    version="1.0.1",
    description="A simple product selection GUI using PySide6",
    author="Abbass ZEN EDDINE",
    install_requires=[
        "PySide6",
        "requests"
    ],
    python_requires=">=3.8",
    py_modules=["main_pyside6"],
    entry_points={
        "gui_scripts": [
            "product-selector = main_pyside6:main"
        ]
    },
)
