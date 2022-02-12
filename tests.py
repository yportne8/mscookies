import unittest
import http.cookiejar
from ms_cookiejar import Browsers, Browser, Profile, Cookies


class TestWindowsPaths(unittest.TestCase):
    
    def test_browsers_paths(self):
        browsers = Browsers.browser_paths()
        for browser in browsers.keys():
            self.assertTrue(browser in Browsers.CHROMIUM_BASED)

    def test_browser_paths(self):
        browser = Browser("Edge")
        self.assertTrue(browser.browser_path.exists())
        self.assertTrue(browser.user_data.exists())
        self.assertTrue(browser.local_state.exists())

    def test_profile_paths(self):
        profile = Profile("edge", "Default")
        self.assertTrue(profile.profile_path.exists())
        self.assertTrue(profile.local_state.exists())
        self.assertTrue(profile.cookies.exists())
        self.assertTrue(profile.picture.exists())
    

class TestCookies(unittest.TestCase):

    def test_cookiejar(self):
        cookies = Cookies("edge", "default")
        self.assertTrue(type(cookies.cookiejar())==http.cookiejar.FileCookieJar)



if __name__ == '__main__':
    unittest.main()