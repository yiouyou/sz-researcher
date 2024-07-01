from setuptools import find_packages, setup

exclude_packages = ["selenium", "webdriver", "fastapi", "fastapi.*", "uvicorn", "jinja2", "sz-researcher"]

with open(r"README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    reqs = [line.strip() for line in f if not any(pkg in line for pkg in exclude_packages)]

setup(
    name="sz-researcher",
    version="0.7.4",
    description="sz-researcher是一款为中文研究而设计的自主智能体，适用于多种任务。",
    package_dir={'sz_researcher': 'sz_researcher'},
    packages=find_packages(exclude=exclude_packages),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yiouyou/sz-researcher",
    author="Zack Song",
    author_email="zhuosong@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=reqs,
)

