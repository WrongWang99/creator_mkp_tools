from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import re


def random_sleep(min_time=3.5, max_time=6.5):
    time.sleep(random.uniform(min_time, max_time))


def get_span_text(driver, span_xpath):
    try:
        span_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, span_xpath))
        )
        return span_element.text
    except Exception as e:
        # print(f"获取span文本时出错")
        return None


def get_span_text_no_number(driver, span_xpath):
    try:
        span_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, span_xpath))
        )
        span_text = span_element.text
        span_text_no_number = re.sub(r'\d+', '', span_text)
        span_text_no_number = span_text_no_number.replace(' ', '', 1)
        return span_text_no_number
    except Exception as e:
        # print(f"获取span文本时出错")
        return None


def get_span_text_only_number(driver, span_xpath):
    try:
        span_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, span_xpath))
        )
        span_text = span_element.text
        span_text_only_number = ''.join(re.findall(r'\d+', span_text))
        return int(span_text_only_number) if span_text_only_number else None
    except Exception as e:
        # print(f"获取span文本时出错")
        return None