import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import warnings
import logging

logging.getLogger("undetected_chromedriver").setLevel(logging.ERROR)

class TabManager:
    def __init__(self, driver):
        self.driver = driver
        self.tabs = {}
    
    def add_tab(self, name, handle):
        self.tabs[name] = handle
        print(f"Tab '{name}' saved: {handle}")
    
    def switch_to(self, name):
        if name in self.tabs:
            self.driver.switch_to.window(self.tabs[name])
            print(f"Switched to tab: {name}")
        else:
            print(f"Tab '{name}' not found. Available tabs: {list(self.tabs.keys())}")
    
    def get_current_tab_name(self):
        current_handle = self.driver.current_window_handle
        for name, handle in self.tabs.items():
            if handle == current_handle:
                return name
        return None
    
    def close_tab(self, name):
        if name in self.tabs:
            self.switch_to(name)
            self.driver.close()
            del self.tabs[name]
            print(f"Tab '{name}' closed")
        else:
            print(f"Tab '{name}' not found")
    
    def list_tabs(self):
        return list(self.tabs.keys())


def create_stealth_driver():
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36"
    )
    options = uc.ChromeOptions()
    
    options.add_argument("--headless=new")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-popup-blocking")
    options.add_argument(f"--user-agent={user_agent}")

    path = os.path.join(os.getcwd(), "chromedriver")
    service = Service(path)
    
    print("Start driver")
    driver = uc.Chrome(service=service, options=options, version_main=146)
    driver.execute_cdp_cmd("Network.emulateNetworkConditions", {
        "offline": False,
        "downloadThroughput": 1.5 * 1024 * 1024 / 8,  # 1.5 Mbps
        "uploadThroughput": 750 * 1024 / 8,            # 750 Kbps
        "latency": 40
    })
    print("Driver starting")
    
    tab_manager = TabManager(driver)
    
    driver.get("https://www.wildberries.ru/")
    try:
        print("Waiting for WB layout")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "portalContainer")))
        print("WB layout loaded")
    except Exception as e:
        print(f"WB layout not loaded: {e}")
    
    tab_manager.add_tab("wb", driver.current_window_handle)
    
    driver.switch_to.new_window('tab')

    # driver.get("https://www.ozon.ru/")
    # try:
    #     print("Waiting for Ozon layout")
    #     wait = WebDriverWait(driver, 10)
    #     wait.until(EC.presence_of_element_located((By.ID, "layoutPage")))
    #     print("Ozon layout loaded")
    # except Exception as e:
    #     print(f"Ozon layout not loaded: {e}")
    
    # tab_manager.add_tab("ozon", driver.current_window_handle)
    
    return driver, tab_manager


if __name__ == "__main__":
    driver, tabs = create_stealth_driver()
    
    tabs.switch_to("wb")
    print(f"Current URL: {driver.current_url}")
    
    tabs.switch_to("ozon")
    print(f"Current URL: {driver.current_url}")
    
    print(f"Available tabs: {tabs.list_tabs()}")
    
    print(f"Current tab: {tabs.get_current_tab_name()}")
    
    driver.quit()
