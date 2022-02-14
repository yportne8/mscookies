import os
import json
import atexit
import sqlite3
from pathlib import Path, WindowsPath
from base64 import b64decode
from Crypto.Cipher import AES
from http.cookiejar import Cookie, CookieJar, LWPCookieJar
from ctypes import (create_string_buffer, memmove, byref,
                    POINTER, Structure, wintypes, windll,
                    c_char, c_wchar_p)


class BrowserNameError(Exception):
    pass


class DataBlob(Structure):
    _fields_ = [('cbData', wintypes.DWORD),
                ('pbData', POINTER(c_char))]


class CookieJar(CookieJar):
    
    # Allows for savedto message and returning path

    def __init__(self, path: Path):
        super().__init__()
        self.path = path            
        
    def save(self):
        cookiejar = LWPCookieJar(str(self.path))
        for cookie in self:
            cookiejar.set_cookie(cookie)
        cookiejar.save()
        print(f"Cookies save to {str(self.path)}")
        return self.path


class Browsers:

    CHROMIUM_BASED = [
        "Opera", "Opera Next", "Opera Developer",
        "Edge", "Edge Beta", "Edge Dev", "Edge Canary",
        "Chrome", "Chrome Beta", "Chrome Dev", "Chrome Canary",
        "Chromium", "Chromium Beta", "Chromium Dev", "Chromium Canary",
        "Brave-Browser", "Brave-Browser-Beta", "Brave-Browser-Nightly"]

    @staticmethod
    def browser_paths(browser_names: list=CHROMIUM_BASED) -> dict:
        browsers = {}
        appdata = os.environ["LOCALAPPDATA"]
        appdata = Path(appdata)
        for p in appdata.resolve().glob('**/'):
            for name in browser_names:
                if name == p.name:
                    browsers[p.name] = str(p)
        return browsers


class Browser(Browsers):

    MSG = \
        f"Multiple results were returned for %s." \
        "Use .browser_paths() for available names and paths." \
        "Narrow your search to one of the following:"

    NAMES = {
        "user_data": "User Data",
        "local_state": "Local State",
        "cookies": "Cookies",
        "profiles": ["Default", "Profile"]}

    def __init__(self, browser_name: str, names: dict=NAMES, **kwargs):
        browser_name = browser_name.title()
        browser_paths = self.browser_paths([browser_name])
        if browser_paths:
            if len(browser_paths) > 1:
                print(Browser.MSG % browser_name)
                print(list(self.browser_paths().keys()))
                browser_path = None
            else:
                browser_path = Path(browser_paths[browser_name])
        else:
            browser_path = None
        self.browser_path = browser_path
        for kwarg in kwargs:
            names[kwarg] = kwargs[kwarg]
        self.names = names
        self.user_data = self._user_data()
        self.local_state = self._local_state()

    def __str__(self):
        if self.browser_path:
            return str(self.browser_path)
        else:
            return str(list(self.browser_paths().keys()))

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return str(list(self.browser_paths().keys()))

    def _doesnotexist(name: str, path: Path):
        msg = f"{name} does not exist "
        msg += f"within {str(path)}"
        print(msg)

    def _user_data(self) -> Path:
        try:
            if not type(self.browser_path) == WindowsPath:
                raise BrowserNameError
            user_data = self.names["user_data"]
            for p in self.browser_path.resolve().glob('**/'):
                if p.name == user_data:
                    return p
            self._doesnotexist(user_data, self.browser_path)
        except BrowserNameError as e:
            msg = "Unknown browser_name..."
            msg += "Available browser names:"
            print(msg)
            print(self.browser_paths().keys())

    def _local_state(self) -> Path:
        try:        
            local_state = self.names["local_state"]
            for p in self.user_data.resolve().glob('**/*'):
                if p.name == local_state:
                    return p
            self._doesnotexist(local_state, self.user_data)
        except:
            return None

    def profiles(self) -> dict:
        profiles = {}
        try:
            for p in self.user_data.resolve().glob('**/'):
                for name in self.names["profiles"]:
                    split_p_name = p.name.split(" ")
                    if name in p.name:
                        profiles[p.name] = p
            return profiles
        except:
            return profiles


class Profile(Browser):

    def __init__(self, browser_name: str, profile_name: str):
        super().__init__(browser_name)
        profile_name = profile_name.title()
        msg = None
        if not self.browser_path:
            profile_path = None
            msg = f"Unable to locate {browser_name}"
        else:
            profiles = self.profiles()
            if not profile_name in profiles.keys():
                profile_path = None
                msg = f"Unable to locate {profile_name} "
                msg += f"within {str(self.browser_path)}"
            else:
                profile_path = profiles[profile_name]
        if msg:
            print(msg)
        self.profile_path = profile_path
        if self.profile_path:
            cookies = self._cookies()
            picture = self._picture()    
        else:
            cookies, picture = None, None
        self.cookies, self.picture = cookies, picture

    def __str__(self):
        if self.profile_path:
            return self.profile_path.stem
        elif not self.browser_path:
            return str(list(self.browser_paths().keys()))
        else:
            return str(self.profiles())

    def __repr__(self):
        if self.profile_path:
            return str(self.profile_path)
        elif not self.browser_path:
            return str(list(self.browser_paths().keys()))
        else:
            return str(self.profiles())
    
    def _cookies(self) -> Path:
        for p in self.profile_path.resolve().glob('**/*'):
            if p.name == self.names["cookies"]:
                return p
        msg = f"{self.names['cookies']} does not exist "
        msg += f"within {str(self.profile_path)}"
        print(msg)

    def _picture(self) -> Path:
        for p in self.profile_path.resolve().glob('**/*'):
            if p.is_file():
                if p.suffix == ".png" and \
                        ("Default" in p.stem or \
                            "Profile" in p.stem):
                    return p
        msg = "Unable to located profile picture for "
        msg += self.profile_path.name
        print(msg)


class Cookies(Profile):

    # Decryption algo adapted from https://github.com/borisbabic/browser_cookie3

    def __init__(self, browser_name: str, profile_name: str):
        super().__init__(browser_name, profile_name)
        self.keys = ["host_key", "is_secure", "expires_utc",
                     "name", "encrypted_value"]
        cookies = Path(os.environ["TEMP"], "Cookies")
        try:
            with open(cookies, "wb+") as temp_cookies:
                with open(self.cookies, "rb") as data:
                    temp_cookies.write(data.read())
            self.cookies = cookies
            atexit.register(self.__del__)
        except:
            msg = f"Unable to retrieve cookies file from {profile_name}"
            self.cookies = None
            print(msg)

    def __del__(self):
        if self.cookies.exists():
            self.cookies.unlink()
    
    def __keydpapi(self):
        try:
            with open(self.local_state,'rb') as key:
                key = json.load(key)
            key = key['os_crypt']['encrypted_key']
            key = key.encode('utf-8')
            return b64decode(key)[5:]
        except:
            return None

    def __cipher(self):
        cipher = self.__keydpapi()
        if not cipher:
            print("Failed to retrieve cipher from Local State.")
            return None
        unprotect = windll.crypt32.CryptUnprotectData
        desc = c_wchar_p()
        b_in, b_ent, b_out = \
            map(lambda x: DataBlob(len(x),
                create_string_buffer(x)),
                [cipher, b'', b''])
        unprotect(byref(b_in), byref(desc),
                  byref(b_ent), None, None,
                  0x01, byref(b_out))
        buffer = create_string_buffer(int(b_out.cbData))
        memmove(buffer, b_out.pbData, b_out.cbData)
        map(windll.kernel32.LocalFree, [desc, b_out.pbData])
        return buffer.raw

    def __decrypt(self, encrypted_value: bytes):
        encrypted_value = encrypted_value[3:]
        nonce, tag = encrypted_value[:12], encrypted_value[-16:]
        cipher = self.__cipher()
        aes = AES.new(cipher, AES.MODE_GCM, nonce=nonce)
        data = aes.decrypt_and_verify(encrypted_value[12:-16], tag)
        return data.decode()

    def _cookie(self, cookie_raw: tuple) -> dict:
        cookie = {}
        for k, v in zip(self.keys, cookie_raw):
            cookie[k] = v
        if cookie["expires_utc"] == 0:
            cookie["expires_utc"] = None
        else:
            expires = cookie["expires_utc"]
            expires = min(int(expires), 32536799999000000)
            cookie["expires_utc"] = (expires/1000000)-11644473600
        value = cookie["encrypted_value"]
        cookie["encrypted_value"] = self.__decrypt(value)
        return \
            Cookie(0, cookie["name"], cookie["encrypted_value"],
                   None, False, cookie["host_key"], True, True,
                   "/", True, cookie["is_secure"], 
                   cookie["expires_utc"], 
                   False, None, None, {})

    def _sql_query(self, domain: str=None):
        criteria = self.keys[0]
        for key in self.keys[1:]:
            criteria += f", {key}"
        query = f"SELECT {criteria} FROM cookies"
        if domain:
            if domain[0] != ".":
                domain = f".{domain}"
            query += " WHERE host_key like ?;"
            return (query, (f"%{domain}%",))
        return (query, None)

    def _cookiejar(self, domain: str):
        if domain:
            path = Path(self.profile_path,
                        f"{domain.strip('.')} Cookies.txt")
        else:
            path = Path(self.profile_path, "Cookies.txt")
        cookiejar = CookieJar(path)
        return cookiejar

    def cookiejar(self, domain: str=None):
        cookiejar = self._cookiejar(domain)
        try:
            con = sqlite3.connect(self.cookies)
            cur = con.cursor()
            query, domain = self._sql_query(domain)
            cur.execute(query,domain) if domain else cur.execute(query)
            for cookie_raw in cur.fetchall():
                cookie = self._cookie(cookie_raw)
                cookiejar.set_cookie(cookie)
            con.close()
            return cookiejar
        except Exception as e:
            msg = "cookie" if domain else "cookiejar"
            msg = f"Unable to load {msg}:\n"
            msg += f"Exception: {str(e)}"
            print(msg)

    def cookie(self, domain: str):
        cookie = self.cookiejar(domain)
        return cookie

    def cookiestring(self, domain: str):
        cookie = self.cookie(domain)
        domain = list(cookie._cookies.keys())[0]
        cookies = cookie._cookies[domain]["/"]
        if cookies:
            cookielist = \
                [f"{cookie.name}={cookie.value}" \
                 for cookie in cookies.values()]
            cookiestring = "; ".join(cookielist)
            return cookiestring
        else:
            msg = "Failed to generate cookiestring."
            print(msg)