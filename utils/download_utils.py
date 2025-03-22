from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from utils.chrome_utils import get_chrome_info

def download_pdf_using_selenium(url, dir):
    print(f"Attempting to download PDF from: {url}")
    print(f"Download directory: {dir}")

    chrome_info = get_chrome_info()

    print(f'Chrome Version: {chrome_info["chrome_version"]}')
    print(f'ChromeDriver Version: {chrome_info["chromedriver_version"]}')
    print(f'ChromeDriver Path: {chrome_info["chromedriver_path"]}')

    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option('prefs', {
            "download.default_directory": dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        })

        service = Service(chrome_info["chromedriver_path"])
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)
        time.sleep(10)
        driver.quit()
        print("✅ PDF download attempt completed.")

        return {"status": "success", "message": "PDF download attempt completed."}

    except FileNotFoundError:
        print("❌ Error: ChromeDriver executable not found.")
        return {"status": "error", "message": "ChromeDriver not found."}

    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {str(e)}")
        return {"status": "error", "message": str(e)}
