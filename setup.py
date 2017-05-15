from setuptools import setup

setup(
    name='eagleeye-py',
    version='1.0',
    description='ealeeye logger maker',
    long_description=open('README.md').read(),
    url='http://gitlab.alibaba-inc.com/linxiao.wlx/eagleeye-py/',
    author='linxiao.wlx',
    author_email='linxiao.wlx@alibaba-inc.com',
    packages=['eagleeye'],
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