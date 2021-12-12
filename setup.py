import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi-cognito",
    version="2.0.0",
    author="Marko Mirosavljev",
    author_email="mirosavljevm023@gmail.com",
    description="Basic AWS cognito authentication package for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/markomirosavljev/fastapi-cognito",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Intended Audience :: Developers"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    py_modules=["fastapi_cognito"],
    install_requires=["fastapi",
                      "cognitojwt[sync]",
                      "pyYAML"],
    python_requires=">=3.8",
)
