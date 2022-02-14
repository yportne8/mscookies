import sys

from cookies import Browser, Cookies


def main():
    browser_name, profile_name, domain = None, None, None
    opts = {
        "--browser": browser_name,
        "--profile": profile_name,
        "--domain": domain}

    for label in opts.keys():
        if label in sys.argv:
            idx = sys.argv.index(label)
            opts[label] = sys.argv[idx+1]

    if not browser_name:
        browser_paths = Cookies.paths()
        print(f"Available browser_names: {list(browser_paths.keys())}")
    elif browser_name and not profile_name:
        browser = Browser(browser_name)
        try:
            profile_paths = browser.profiles()
            print(f"Available profile_names: {list(profile_paths.keys())}")
        except:
            browser_paths = Cookies.paths()
            print(f"Available browser_names: {list(browser_paths.keys())}")
    elif browser_name and profile_name and not domain:
        cookies = Cookies(browser_name, profile_name)
        try:
            cookiejar = cookies.cookiejar()
            cookiejar.save()
        except:
            print("Unable to save cookiejar.")
    elif browser_name and profile_name and domain:
        cookies = Cookies(browser_name, profile_name)
        try:
            cookie = cookies.cookie(domain)
            cookie.save()
            cookiestring = cookies.cookiestring(domain)
            print(f"Cookiestring: {cookiestring}")
        except:
            print(f"Unable to save cookie for {domain}.")