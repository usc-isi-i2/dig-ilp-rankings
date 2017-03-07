try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'digILPRankings',
    'description': 'digILPRankings',
    'author': 'Rahul Kapoor',
    'url': 'https://github.com/usc-isi-i2/dig-ilp-rankings',
    'download_url': 'https://github.com/usc-isi-i2/dig-ilp-rankings',
    'author_email': 'rahulkap@isi.edu',
    'version': '0.3.9',
    'install_requires': ['digExtractor>=0.3.0'],
    # these are the subdirs of the current directory that we care about
    'packages': ['digIlpRankings'],
    'scripts': [],
}

setup(**config)
