from setuptools import setup, find_packages

setup(
    name="smart-home-automation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pytest>=6.2.5",
    ],
    entry_points={
        'console_scripts': [
            'smart-home=app:main',
        ],
    },
    python_requires=">=3.8",
    author="Akıllı Ev Ekibi",
    author_email="info@akilliev.com",
    description="Makine öğrenmesi tabanlı akıllı ev otomasyon sistemi",
    keywords="akıllı ev, otomasyon, makine öğrenmesi, IoT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)