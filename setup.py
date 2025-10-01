from setuptools import setup, find_packages

setup(
    name='market-trend-predictor',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'flask',
    ],
    extras_require={
        'dev': [
            'pytest',
            'flake8',
            'black',
        ],
    },
    author='Gabriel Demetrios Lafis',
    author_email='gabriel.lafis@example.com',
    description='An advanced market trend prediction system.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/GabrielDemetriosLafis/Market-Trend-Predictor',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)

