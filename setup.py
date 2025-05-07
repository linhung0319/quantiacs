from setuptools import setup

setup(
    name="qnt",
    version="0.0.501",
    url="https://quantiacs.com",
    license='MIT',
    packages=['qnt', 'qnt.ta', 'qnt.data', 'qnt.examples'],
    package_data={'qnt': ['*.ipynb']},
    install_requires=[
        'scipy>=1.14.0',
        'pandas==2.2.3',
        'xarray==2025.3.1',
        'numpy<2.3.0',
        'tabulate>=0.9.0',
        'bottleneck>=1.4.2',
        'numba==0.61.2',
        'progressbar2>=3.55,<4',
        'cftime==1.6.4',
        'plotly==6.0.1',
        'matplotlib==3.10.1'
    ]
)