import ssl
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait  # type:ignore
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import urllib.request
import urllib.error

# Ignore SSL certificate verification warnings
ssl._create_default_https_context = ssl._create_unverified_context

searchKey = input("Input Keyword: ")

chrome_options = Options()
chrome_driver_path = "./chromedriver.exe"
chrome_service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get("https://www.google.co.kr/imghp?hl=ko&tab=wi&authuser=0&ogbl")
elem = driver.find_element(By.NAME, "q")

elem.send_keys(searchKey)
elem.send_keys(Keys.RETURN)

SCROLL_PAUSE_TIME = 1
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        try:
            driver.find_element(By.CSS_SELECTOR, ".mye4qd").click()
        except:
            break
    last_height = new_height

# List of sites to exclude (add more URLs if needed)
excluded_sites = [
    "https://media.ed.edmunds-media.com/",
    # Add more URLs of sites you want to exclude from processing
]

time.sleep(2)

images = driver.find_elements(By.CSS_SELECTOR, ".rg_i.Q4LuWd")
count = 1
for image in images:
    try:
        image.click()
        # Use WebDriverWait to wait for the image preview to be visible on the page
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#Sva75c > div.A8mJGd.NDuZHe > div.dFMRD > div.pxAole > div.tvh9oe.BIB1wf > c-wiz > div > div > div > div.n4hgof > div.MAtCL.PUxBg > a > img.r48jcc.pT0Scc.iPVvYb",
                )
            )
        )
        # Find the image element using CSS Selector
        img_element = driver.find_element(
            By.CSS_SELECTOR,
            "#Sva75c > div.A8mJGd.NDuZHe > div.dFMRD > div.pxAole > div.tvh9oe.BIB1wf > c-wiz > div > div > div > div.n4hgof > div.MAtCL.PUxBg > a > img.r48jcc.pT0Scc.iPVvYb",
        )
        imgUrl = img_element.get_attribute("src")

        # Check if the image format is ".webp" and skip if it is
        if imgUrl.endswith(".webp"):  # type:ignore
            print("Skipping .webp format image -", imgUrl)
            continue

        # Check if the image URL matches any of the excluded sites and skip if it does
        if any(site in imgUrl for site in excluded_sites):  # type:ignore
            print("Skipping image from excluded site -", imgUrl)
            continue

        # Check if the image URL is accessible before attempting to download
        try:
            urllib.request.urlopen(imgUrl)  # type:ignore
        except urllib.error.HTTPError as e:
            print(
                "Error occurred for image",
                count,
                "- Skipping and continuing to the next image.",
            )
            print("Error message:", e)
            continue

        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
            )
        ]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(
            imgUrl, f"./imgs/{searchKey}{str(count)}.jpg"  # type:ignore
        )  # type:ignore
        count += 1
    except TimeoutException:
        print(
            "Timeout occurred for image",
            count,
            "- Skipping and continuing to the next image.",
        )
    except NoSuchElementException:
        print(
            "Image element not found for image",
            count,
            "- Skipping and continuing to the next image.",
        )
    except Exception as e:
        print(
            "Error occurred for image",
            count,
            "- Skipping and continuing to the next image.",
        )
        print("Error message:", e)
        pass
    finally:
        # Close the image preview if it's open
        try:
            close_button = driver.find_element(
                By.CSS_SELECTOR, ".iOGqzf.H4qWMc.npT2md.IpCkIb.B04j1c"
            )
            close_button.click()
        except:
            pass

driver.close()
