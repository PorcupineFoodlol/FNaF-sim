from setuptools import setup
setup(
    name='fred1sim',
    version='0.0.1',
    entry_points={
        'console_scripts': [
            'fred1sim=fred1sim:main'
        ]
    }
)