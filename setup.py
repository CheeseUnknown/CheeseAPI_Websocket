import setuptools

with open('./README.md', 'r', encoding = 'utf-8') as f:
    longDescription = f.read()

setuptools.setup(
    name = 'CheeseAPI_Websocket',
    version = '0.1.4',
    author = 'Cheese Unknown',
    author_email = 'cheese@cheese.ren',
    description = '一款基于CheeseAPI的升级款Websocket插件',
    long_description = longDescription,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/CheeseUnknown/CheeseAPI_Websocket',
    license = 'MIT',
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11'
    ],
    keywords = 'api framework backend asyncio',
    python_requires = '>=3.11',
    install_requires = [
        'CheeseAPI',
        'redis'
    ],
    packages = setuptools.find_packages()
)
