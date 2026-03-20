from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from browser_utils import do_login, dismiss_cookies, is_single_size, try_add_to_cart


def login(driver, url, email, password, log=print):
    log("Opening product page...")
    driver.get(url)

    wait = WebDriverWait(driver, 15)

    already_logged_in = False
    try:
        driver.find_element(By.ID, "addToCartButton")
        already_logged_in = True
    except:
        pass

    if already_logged_in:
        log("Already logged in, skipping login.")
        return

    do_login(driver, email, password, log)

    if "/campaigns/" not in driver.current_url:
        log("Navigating to product page...")
        driver.get(url)

    wait.until(EC.presence_of_element_located((By.ID, "addToCartButton")))


def reserve(driver, sizes, log=print, is_running=lambda: True):
    added = False
    attempt = 1
    wait = WebDriverWait(driver, 10)

    while not added and is_running():
        time.sleep(2)

        if is_single_size(driver):
            log("Single size product detected, adding directly...")
            added = try_add_to_cart(driver, log)
            if added:
                break
        else:
            size_elements = driver.find_elements(
                By.CSS_SELECTOR, "div[class*='ArticleSizeToggle-sc']"
            )

            for element in size_elements:
                if not is_running():
                    return False
                try:
                    label = element.find_element(By.TAG_NAME, "label")
                    spans = label.find_elements(By.TAG_NAME, "span")
                    size_name = spans[0].text.strip() if spans else ""
                    input_el = element.find_element(
                        By.CSS_SELECTOR, "input[data-testid='article-size-toggle']"
                    )

                    if size_name in sizes and input_el.is_enabled():
                        time.sleep(0.5)
                        label.click()
                        log(f"Selected size: {size_name}")
                        time.sleep(0.5)

                        added = try_add_to_cart(driver, log)
                        break
                except Exception:
                    continue

        if not added and is_running():
            driver.refresh()
            log(f"Product reserved by someone else. Refresh #{attempt}")
            attempt += 1
            try:
                wait.until(EC.presence_of_element_located((By.ID, "addToCartButton")))
            except:
                pass

    return added
