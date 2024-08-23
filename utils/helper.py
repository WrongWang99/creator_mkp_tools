import re
from urllib.parse import urlparse
from utils.selenium_utils import get_span_text_no_number, get_span_text_only_number
from concurrent.futures import ThreadPoolExecutor


def get_orderid(current_url):
    parsed_url = urlparse(current_url)
    path = parsed_url.path
    match = re.search(r'/order/detail/(\d+)', path)
    return match.group(1) if match else print("No matching ID found in the URL")


def check_action_required(driver, activity_id, index):
    actions_required_xpath = f"//*[@id='{activity_id}']/div[2]/div/div/div[1]/div[3]/table/tbody/tr[{index}]/td[3]/div/div/div/a"
    span_text = get_span_text_no_number(driver, actions_required_xpath)
    # print(span_text)
    if span_text is None or span_text.strip() == "":
        # print(f"第 {index} 个创作者无需审核")
        return None
    if span_text == "actions required":
        print(f"第 {index} 个创作者需审核")
        return index
    return None


def get_actions_required_creator(driver, activity_id):
    ongoing_xpath = f"//*[@id='tab-2000']"
    creators_number = get_span_text_only_number(driver, ongoing_xpath)
    if creators_number is None:
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_action_required, driver, activity_id, i) for i in range(1, creators_number + 1)]
        for future in futures:
            result = future.result()
            if result is not None:
                return result

    return None