from setuptools import setup

setup(name='ploev',
      version='0.2.0',
      description='Python library for ProPokerTools Odds Oracle',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3.6',
          'Topic :: Utilities',
      ],
      url='https://github.com/vyvojer/ploev',
      author='Alexey Londkevich',
      author_email='vyvojer@gmail.com',
      license='GPLv3+',
      packages=['ploev'],
      package_data={
          'ploev': ['ploev.ini',]
      },
      install_requires=['pyparsing'],
      zip_safe=False)