import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi-cognito",
    version="0.0.1",
    author="Marko Mirosavljev",
    author_email="marko.mirosavljev@cyterma.com",
    description="Basic AWS cognito authentication package for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://gitlab.com/cyterma/normius/fastapi-cognito",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "Provider :: Amazon Web Services",
        "Authentication :: AWS Cognito",
        "License :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where='src'),
    py_modules=['fastapi_cognito', 'exceptions'],
    install_requires=['fastapi',
                      'cognitojwt[sync]'],
    python_requires=">=3.8",
)
