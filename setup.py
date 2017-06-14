import setuptools

setuptools.setup(
    name="nbperiodicrunner",
    version='0.0.1',
    url="https://github.com/data-8/nbperiodicrunner",
    author="Data 8 @ UC Berkeley",
    description="Simple Jupyter extension to periodically runs cli apps for a certain time interval..",
    packages=setuptools.find_packages(),
    install_requires=[
        'notebook', 'tornado'
    ],
    package_data={'nbpuller': ['static/*']},
)
