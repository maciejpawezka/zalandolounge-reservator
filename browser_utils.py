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
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
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


def do_login(driver, email, password, log=print):
    wait = WebDriverWait(driver, 15)

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


def try_add_to_cart(driver, log):
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


def is_single_size(driver):
    try:
        section = driver.find_element(By.ID, "article-size-section")
        text = section.text.lower()
        return "dostępny tylko w jednym rozmiarze" in text
    except:
        return False


def try_add_product(driver, sizes, log):
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "addToCartButton")))
    except:
        log("Add to cart button not found, skipping...")
        return False

    time.sleep(1)

    if is_single_size(driver):
        log("Single size product, adding directly...")
        return try_add_to_cart(driver, log)

    size_elements = driver.find_elements(
        By.CSS_SELECTOR, "div[class*='ArticleSizeToggle-sc']"
    )

    for element in size_elements:
        try:
            label = element.find_element(By.TAG_NAME, "label")
            spans = label.find_elements(By.TAG_NAME, "span")
            size_name = spans[0].text.strip() if spans else ""
            input_el = element.find_element(
                By.CSS_SELECTOR, "input[data-testid='article-size-toggle']"
            )

            if size_name in sizes and input_el.is_enabled():
                time.sleep(0.3)
                label.click()
                log(f"Selected size: {size_name}")
                time.sleep(0.3)
                return try_add_to_cart(driver, log)
        except Exception:
            continue

    log("No matching size available, skipping...")
    return False
