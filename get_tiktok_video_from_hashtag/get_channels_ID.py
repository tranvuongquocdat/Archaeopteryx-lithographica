from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import time

def get_channels_ID(hashtag, limit, driver):
    try:
        # 1. Mở YouTube
        driver.get("https://www.youtube.com")

        # 2. Tìm kiếm hashtag
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys(f"#{HASHTAG}")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # 3. Chuyển sang tab "Shorts" (nếu có)
        try:
            shorts_tab = driver.find_element(By.XPATH, "//yt-chip-cloud-chip-renderer//span[contains(text(), 'Shorts')]")
            shorts_tab.click()
            time.sleep(2)
        except Exception:
            pass  # Nếu không có tab Shorts thì bỏ qua

        # 4. Lấy kênh cho tới khi đủ LIMIT
        channels = set()
        pbar = tqdm(total=LIMIT, desc="Số kênh đã lấy", ncols=80)
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        MAX_SCROLL_ATTEMPTS = 5
        scroll_attempts = 0
        while len(channels) < LIMIT and scroll_attempts < MAX_SCROLL_ATTEMPTS:
            shorts = driver.find_elements(By.XPATH, "//a[contains(@href, '/shorts/')]")
            for short in shorts:
                if len(channels) >= LIMIT:
                    break
                try:
                    parent = short.find_element(By.XPATH, "./../../..")
                    # Thử nhiều selector khác nhau
                    selectors = [
                        ".//a[contains(@href, '/@')]",
                        ".//a[contains(@href, '/channel/')]", 
                        ".//a[contains(@href, '/c/')]"
                    ]

                    for selector in selectors:
                        try:
                            channel_elem = parent.find_element(By.XPATH, selector)
                            channel_name = channel_elem.text
                            channel_url = channel_elem.get_attribute("href")
                            before = len(channels)
                            channels.add((channel_name, channel_url))
                            after = len(channels)
                            if after > before:
                                pbar.update(1)
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"Lỗi khi lấy thông tin kênh: {e}")  # Debug
                    continue

            if len(channels) >= LIMIT:
                break

            # Cuộn xuống và đợi lâu hơn
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(0.5)  
            
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                time.sleep(1)  # Đợi thêm trước khi thử lại
            else:
                scroll_attempts = 0  # Reset nếu có nội dung mới
            last_height = new_height
        pbar.close()

        # 5. return ra danh sách kênh
        print(f"Đã lấy {len(channels)} kênh:")
        return [url for name, url in list(channels)]
    except Exception as e:
        print(f"Lỗi khi lấy kênh: {e}")
        return []
