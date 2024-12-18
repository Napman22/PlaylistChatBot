from setuptools import setup, find_packages

requires = [
    'flask',
    'spotipy',
    'html5lib',
    'requests',
    'requests_html',
    'beautifulsoup4',
    'youtube_dl',
    'pathlib',
    'pandas'
    'openai'
]

setup(
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires
)
