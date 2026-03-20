from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from browser_utils import do_login, dismiss_cookies, try_add_product


CAMPAIGN_BASE_URL = "https://www.zalando-lounge.pl/campaigns/"
MAIN_PAGE_URL = "https://www.zalando-lounge.pl/"
MAX_CART_ITEMS = 20


def _get_cart_count(driver):
    try:
        badge = driver.find_element(
            By.CSS_SELECTOR, "#nav-to-cart-trigger [class*='AmountContainer']"
        )
        return int(badge.text.strip())
    except:
        return 0


def _wait_for_campaign_start(driver, code, log, is_running):
    campaign_url = CAMPAIGN_BASE_URL + code
    attempt = 0

    while is_running():
        driver.get(campaign_url)
        time.sleep(3)

        if code in driver.current_url:
            products = driver.find_elements(By.ID, "articleListWrapper")
            if products:
                log("Campaign is live! Products found.")
                return True

        attempt += 1
        if attempt == 1:
            log("Campaign hasn't started yet. Waiting...")
        if attempt % 6 == 0:
            log(f"Still waiting for campaign {code}...")

        for _ in range(3):
            if not is_running():
                return False
            time.sleep(1)

    return False


def _apply_sort(driver, sort_option, log):
    try:
        sort_tabs = driver.find_elements(
            By.XPATH, "//button[@role='tab']//span[contains(text(),'Sortowanie')]"
        )
        if sort_tabs:
            sort_tabs[0].find_element(By.XPATH, "ancestor::button").click()
            time.sleep(0.5)

            options = driver.find_elements(By.CSS_SELECTOR, "[data-testid='sort-button']")
            for opt in options:
                label = opt.find_element(By.XPATH, "ancestor::label")
                if sort_option.lower() in label.text.lower():
                    label.click()
                    log(f"Sort applied: {sort_option}")
                    time.sleep(1)

                    try:
                        close_btn = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='close-open-button']"
                        )
                        close_btn.click()
                        time.sleep(0.5)
                    except:
                        pass
                    return
            log(f"Sort option '{sort_option}' not found")
        else:
            log("Sortowanie tab not found")
    except Exception as e:
        log(f"Could not apply sort: {e}")


def _apply_brand(driver, brand, log):
    if not brand:
        return
    try:
        brand_tabs = driver.find_elements(
            By.XPATH, "//button[@role='tab']//span[contains(text(),'Marka')]"
        )
        if brand_tabs:
            brand_tabs[0].find_element(By.XPATH, "ancestor::button").click()
            time.sleep(1)

            brand_buttons = driver.find_elements(
                By.CSS_SELECTOR, "button[data-testid='brand-item']"
            )
            for btn in brand_buttons:
                btn_text = btn.text.strip()
                if brand.lower() == btn_text.lower():
                    btn.click()
                    log(f"Brand filter applied: {btn_text}")
                    time.sleep(1)

                    try:
                        close_btn = driver.find_element(
                            By.CSS_SELECTOR, "[data-testid='close-open-button']"
                        )
                        close_btn.click()
                        time.sleep(0.5)
                    except:
                        pass
                    return

            log(f"Brand '{brand}' not found in filters. Available: "
                + ", ".join([b.text.strip() for b in brand_buttons]))
        else:
            log("Marka tab not found")
    except Exception as e:
        log(f"Could not apply brand filter: {e}")


def _collect_product_links(driver):
    links = driver.find_elements(
        By.CSS_SELECTOR, "#articleListWrapper a[class*='LinkOverlay']"
    )
    hrefs = []
    for link in links:
        href = link.get_attribute("href")
        if href and href not in hrefs:
            hrefs.append(href)
    return hrefs


def _grab_products(driver, sizes, log, is_running):
    product_links = _collect_product_links(driver)
    main_window = driver.current_window_handle
    total = len(product_links)
    
    # Initial cart count from main page
    added_count = _get_cart_count(driver)
    attempted = 0

    log(f"Found {total} products on campaign page. Cart: {added_count}/{MAX_CART_ITEMS}")

    for i, href in enumerate(product_links):
        if not is_running():
            break
        if added_count >= MAX_CART_ITEMS:
            log(f"Cart full! {added_count}/{MAX_CART_ITEMS} items.")
            break

        log(f"[{i+1}/{total}] Opening product in new tab...")
        
        # Open in new tab and switch
        driver.execute_script(f"window.open('{href}', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])

        try:
            success = try_add_product(driver, sizes, log)
            if success:
                added_count += 1
                log(f"Cart (estimated): {added_count}/{MAX_CART_ITEMS}")
        except Exception as e:
            log(f"Error on product page: {e}")
        finally:
            # Close product tab and switch back to main campaign tab
            driver.close()
            driver.switch_to.window(main_window)
            time.sleep(0.5)  # Short pause before next product

        attempted += 1

    # Refresh main page once at the end to get the true final cart count
    if attempted > 0:
        driver.refresh()
        time.sleep(2)
        added_count = _get_cart_count(driver)

    log(f"Finished. Went through {attempted} products. Actual Cart: {added_count}/{MAX_CART_ITEMS}")
    return added_count


def campaign_grab(driver, code, email, password, sizes, sort, brand, log=print, is_running=lambda: True):
    log("Opening Zalando Lounge...")
    driver.get(MAIN_PAGE_URL)
    time.sleep(2)

    dismiss_cookies(driver)

    needs_login = False
    try:
        driver.find_element(By.ID, "signin-with-Zalando")
        needs_login = True
    except:
        pass

    if needs_login:
        do_login(driver, email, password, log)
    else:
        log("Already logged in.")

    if not is_running():
        return 0

    log(f"Navigating to campaign {code}...")
    started = _wait_for_campaign_start(driver, code, log, is_running)
    if not started:
        return 0

    time.sleep(2)

    if sort and sort != "Popularne":
        _apply_sort(driver, sort, log)

    if brand:
        _apply_brand(driver, brand, log)

    time.sleep(1)

    if not is_running():
        return 0

    log("Starting to add products to cart...")
    added = _grab_products(driver, sizes, log, is_running)

    return added
