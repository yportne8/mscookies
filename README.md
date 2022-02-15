# MS-Cookies

MS-Cookies (mscookies) is a stripped down fork of browser_cookie3. Browser_cookie3 currently does not work on Chromium-based browsers running
on Windows machines due to a recent update to Chromium. The update changed the location of the Cookies file from the user profile directory to one of its
sub-directories (Network). This fork updates its predecessor by including fail-safes around future file/directory changes. The decryption algo remains 
more-or-less the same, although its been streamlined for use with Chromium-Based browsers running on Windows machines only.

## Installation via PyPi:
```
pip install mscookies
```

## Installation from source:
```
git clone https://github.com/yportne8/MS-Cookies.git
cd MS-Cookies
python setup.py install
```

### Identify the main directory for locally installed Chromium-based Browsers.
```python
>>> from mscookies import Cookies
>>> Cookies.CHROMIUM_BASED
['Opera', 'Opera Next', 'Opera Developer', 
 'Edge', 'Edge Beta', 'Edge Dev', 'Edge Canary',
 'Chrome', 'Chrome Beta', 'Chrome Dev', 'Chrome Canary',
 'Chromium', 'Chromium Beta', 'Chromium Dev', 'Chromium Canary',
 'Brave-Browser', 'Brave-Browser-Beta', 'Brave-Browser-Nightly']
>>> Cookies.browser_paths()
{'Chromium': 'C:\\Users\\username\\AppData\\Local\\Chromium',
 'Chrome': 'C:\\Users\\username\\AppData\\Local\\Google\\Chrome', 
 'Edge': 'C:\\Users\\username\\AppData\\Local\\Microsoft\\Edge', 
 'Edge Beta': 'C:\\Users\\username\\AppData\\Local\\Microsoft\\Edge Beta'}
```

### Determine what profiles are stored within a browser.
```python
>>> from mscookies import Browser
>>> browser = Browser(browser_name="edge beta")
>>> browser.profiles()
{'Default': WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta/User Data/Default'),
 'Profile 1': WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta/User Data/Profile 1')}
```

### User Data paths
Along with the static browser_paths function, the Cookies object retains all paths from the parent classes Profile and Browser.
```python
>>> from mscookies import Cookies
>>> cookies = Cookies(browser_name="edge beta", profile_name="default")
>>> cookies.browser_path
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta')
>>> cookies.profile_path
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta/User Data/Default')
>>> cookies.local_state
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta/User Data/Local State')
>>> cookies.picture
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge Beta/User Data/Edge Profile Picture.png')
```

### Cookies file
A temporary copy of the Cookies file is created on init of class Cookies.
```python
>>> from mscookies import Cookies
>>> cookies = Cookies("edge beta", "default")
>>> cookies.cookies
WindowsPath('C:/Users/username/AppData/Local/Temp/Cookies')
```

### Cookiejar and Cookies functions
The cookiejar and cookies functions implements a modified version of class http.cookiejar.CookieJar. This approach allows for greater utility than using http.cookiejar.LWPCookieJar, at least when saving the cookiejar as a txt file.
```python
>>> cookiejar = cookies.cookiejar()
>>> saved_to_path = cookiejar.save()
Cookies save to C:\Users\username\AppData\Local\Microsoft\Edge\User Data\Default\Cookies.txt
>>> print(saved_to_path)
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge/User Data/Default/Cookies.txt')
>>> cookiejar.path = Path(Path.home(), "Cookies.txt")
>>> cookiejar.save()
Cookies save to C:\Users\username\Cookies.txt
WindowsPath('C:/Users/username/Cookies.txt')
>>> cookie = cookies.cookiejar("google.com")
>>> cookie.save()
Cookies save to C:\Users\username\AppData\Local\Microsoft\Edge\User Data\Default\google.com Cookies.txt
WindowsPath('C:/Users/username/AppData/Local/Microsoft/Edge/User Data/Default/google.com Cookies.txt')
```

### Cookiestring function
Returns a string that can be embedded into request headers.
```python
>>> from mscookies import Cookies
>>> cookies = Cookies(browser_name="edge", "profile 1")
>>> cookiestring = cookies.cookiestring("youtube.com")
>>> headers_auth = {
...     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
...     "Accept": "*/*",
...     "Accept-Language": "en-US,en;q=0.5",
...     "Content-Type": "application/json",
...     "X-Goog-AuthUser": "0",
...     "x-origin": "https://music.youtube.com",
...     "Cookie" : cookiestring}
>>> import json
>>> headers_auth_path = Path(Path.home(), "Music", "headers_auth.json")
>>> with open(headers_auth_path, "w+") as json_file:
...     json.dump(headers_auth, json_file)
>>> from ytmusicapi import YTMusic
>>> ytm = YTMusic(headers_auth_path)
>>> mp3 = Path(Path.home(), "Music", "mysong.mp3")
>>> ytm.upload_song(mp3)
```
