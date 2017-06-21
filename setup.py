from setuptools import setup

setup(
    name='trace-logger',
    version='1.0',
    description='trace logger maker',
    long_description=open('README.md').read(),
    url='https://github.com/lxkaka/trace-logger',
    author='lxkaka',
    author_email='linxiaoking@gmail.com',
    packages=['trace_logger'],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)