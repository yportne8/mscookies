from distutils.core import setup

setup(
    name='Microsoft-CookieJar',
    version='1.0.0',
    packages=['ms_coookiejar'],
    package_dir={'ms_cookiejar': 'ms_cookiejar'},
    author='CS Kim',
    author_email='yportne8@gmail.com',
    description='Loads http.cookiejar.FileCookieJars with decrypted cookies from chromium-based browsers running on microsoft windows machines.',
    url='https://github.com/yportne8/Microsoft-CookieJar',
    install_requires=["pycryptodome"],
    license='MIT')