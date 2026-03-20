from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def launch_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def dismiss_cookies(driver):
    try:
        buttons = driver.find_elements(By.XPATH,
            "//button[contains(text(),'Akceptuj') or contains(text(),'akceptuj')]"
        )
        for btn in buttons:
            if btn.is_displayed():
                btn.click()
                time.sleep(0.5)
                break
    except:
        pass


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

    dismiss_cookies(driver)

    log("Clicking 'Sign in with Zalando'...")
    btn = wait.until(EC.element_to_be_clickable((By.ID, "signin-with-Zalando")))
    btn.click()

    log("Entering email...")
    email_input = wait.until(EC.element_to_be_clickable((By.ID, "username")))
    email_input.clear()
    email_input.send_keys(email)

    continue_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "[data-testid='verify-email-button']")
    ))
    continue_btn.click()

    log("Entering password...")
    pw_input = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "[data-testid='login-password-input']")
    ))
    pw_input.clear()
    pw_input.send_keys(password)

    login_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "[data-testid='login-button']")
    ))
    login_btn.click()

    log("Waiting for login to complete...")
    WebDriverWait(driver, 30).until(
        lambda d: "zalando-lounge.pl" in d.current_url and "accounts.zalando" not in d.current_url
    )
    log("Logged in!")

    if "/campaigns/" not in driver.current_url:
        log("Navigating to product page...")
        driver.get(url)

    wait.until(EC.presence_of_element_located((By.ID, "addToCartButton")))


def _try_add_to_cart(driver, log):
    add_btn = driver.find_element(By.ID, "addToCartButton")
    btn_text = add_btn.text.lower()

    if "zarezerw" in btn_text or "brak" in btn_text or add_btn.get_attribute("disabled"):
        log(f"Button unavailable ('{add_btn.text}')")
        return False

    add_btn.click()
    time.sleep(1)

    verify = driver.find_elements(By.ID, "addToCartButton")
    if verify:
        txt = verify[0].text.lower()
        if "zarezerw" in txt or verify[0].get_attribute("disabled"):
            log("Product reserved after click. Retrying...")
            return False

    log("Added to cart!")
    return True


def _is_single_size(driver):
    try:
        section = driver.find_element(By.ID, "article-size-section")
        text = section.text.lower()
        return "dostępny tylko w jednym rozmiarze" in text
    except:
        return False


def reserve(driver, sizes, log=print, is_running=lambda: True):
    added = False
    attempt = 1
    wait = WebDriverWait(driver, 10)

    while not added and is_running():
        time.sleep(2)

        if _is_single_size(driver):
            log("Single size product detected, adding directly...")
            added = _try_add_to_cart(driver, log)
            if added:
                break
        else:
            size_elements = driver.find_elements(
                By.XPATH, "//div[contains(@class,'ArticleSizeToggle-sc')]"
            )

            for element in size_elements:
                if not is_running():
                    return False
                try:
                    size_name = element.find_element(
                        By.XPATH, ".//span[contains(@class,'ArticleSizeItemTitle-sc')]"
                    ).text
                    input_el = element.find_element(By.TAG_NAME, "input")

                    if size_name in sizes and input_el.is_enabled():
                        time.sleep(0.5)
                        element.find_element(By.TAG_NAME, "label").click()
                        log(f"Selected size: {size_name}")
                        time.sleep(0.5)

                        added = _try_add_to_cart(driver, log)
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
