from setuptools import setup
with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

setup(
    name='PayPayPy',
    version='1.0.3',
    description='PayPayのログインから情報の取得、リンクの受け取りや送金を行えます',
    url='https://github.com/SpecialAgency-Chat/paypaypy',
    author='神瀬来未',
    author_email='info@vxxx.cf',
    license='GPL-3.0',
    keywords='paypay backend frontend api unofficial private',
    packages=[
        "PayPayPy",
    ],
    install_requires=required,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
    ],
)
