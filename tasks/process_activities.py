from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from utils.selenium_utils import random_sleep, get_span_text
from utils.helper import get_orderid, get_actions_required_creator
from concurrent.futures import ThreadPoolExecutor


def process_activity(driver, activity_id):
    url = f"https://creatormarketplace.tiktok.com/ad/invitation-camp/detail/{activity_id}?enter_from=campaign-list&general_order_status=2000"
    driver.get(url)


def process_creators(driver, activity_id):
    max_retries = 3
    retries = 0
    while True and retries < max_retries:
        try:
            random_sleep(4.0, 5.0)

            i = get_actions_required_creator(driver, activity_id)
            # random_sleep(2.0, 3.0)

            if i is None:
                print(f"无更多创作者")
                break
            creator_xpath = f"//*[@id='{activity_id}']/div[2]/div/div/div[1]/div[3]/table/tbody/tr[{i}]/td[2]/div/div/div[2]/div"
            # 找到创作者并点击
            creator = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, creator_xpath))
            )

            creator.click()
            print(f"进入第 {i} 个创作者主页")

            random_sleep(3.0, 4.5)

            # 处理创作者页面
            process_creator_page(driver)

            # random_sleep(3.0, 4.5)

            # 返回上一页
            driver.back()

            i += 1
            retries = 0

        except Exception as e:
            if retries >= max_retries - 1:
                print("已达到最大重试次数，停止操作。")
                break
            else:
                print(f"操作超时，刷新页面并重试第 {retries + 1} 次————process_creators:{e}")
                driver.refresh()
                random_sleep(5.0, 8.5)
def process_creator_page(driver):
    current_url = driver.current_url
    order_id = get_orderid(current_url)
    try:
        accept_xpath = f"//*[@id='{order_id}']/div[2]/section[1]/div[2]/div[2]/div/div/div[1]/div/div[5]/button"
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, accept_xpath))
        )
        accept_button.click()
        random_sleep(5.0, 8.5)
        review_and_approve(driver, order_id)
    except Exception as e:
        print(f"未能找到'接受'按钮或已接受")
        review_and_approve(driver, order_id)


def get_review_j_values(driver, order_id):
    j_values = []
    for j in range(1, 11):
        review_xpath = f"//*[@id='{order_id}']/div[2]/section[1]/div[2]/div[2]/div/div/div/div/div[{j}]/div/div[2]/div/div[1]/div[1]/span"
        span_text = get_span_text(driver, review_xpath)
        if span_text == "视频待提交":
            print(f"第 {j} 个视频未提审，提前结束审查")
            break
        elif span_text == "你有一个新的视频待审查":
            print(f"第 {j} 个视频需要审查")
            j_values.append(j)
        elif span_text == "视频已发布":
            print(f"第 {j} 个视频已审查")
            continue
        elif span_text == "视频可以发布了":
            print(f"第 {j} 个视频被干了, 过！")
            continue
    return j_values


def review_and_approve(driver, order_id):
    max_retries = 3

    # 多线程获取所有需要审核的j值
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_j_values = executor.submit(get_review_j_values, driver, order_id)
        j_values = future_j_values.result()

    for j in j_values:
        try:
            review_xpath = f"//*[@id='{order_id}']/div[2]/section[1]/div[2]/div[2]/div/div/div/div/div[{j}]/div/div[3]/section/div[1]/div[2]/button"
            review_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, review_xpath))
            )
            review_button.click()
            print(f"审核点击成功: {j}")
            random_sleep(3.0, 4.5)
        except Exception as e:
            print(f"审核点击失败或已审核: {j}")
            continue

        approve_attempts = 0
        approved = False
        while approve_attempts < max_retries:
            try:
                approve_xpath = f"//*[@id='{order_id}']/div[2]/section[1]/div[2]/div[2]/div/div/div/div/div[{j}]/div/div[3]/section/div[2]/div/div/section/div[3]/div[2]/button/span"
                approve_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, approve_xpath))
                )
                approve_button.click()
                print(f"完成批准: {j}")
                random_sleep(3.0, 4.5)
                approved = True
                break
            except Exception as e:
                approve_attempts += 1
                print(f"批准点击失败: {j}，尝试次数: {approve_attempts}: {e}")
                if approve_attempts >= max_retries:
                    print(f"批准点击失败已达最大尝试次数: {j}")
                    break
        if not approved:
            continue

        approve_video_attempts = 0
        while approve_video_attempts < max_retries:
            try:
                approve_video_xpath = f"/html/body/div[6]/div/div[3]/button[2]/span"
                approve_video_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, approve_video_xpath))
                )
                approve_video_button.click()
                print(f"批准视频点击成功: {j}")
                random_sleep(3.0, 5.0)
                break
            except Exception as e:
                approve_video_attempts += 1
                print(f"批准视频点击失败: {j}, 尝试次数: {approve_video_attempts}: {e}")
                if approve_video_attempts >= max_retries:
                    print(f"批准视频点击失败已达最大尝试次数: {j}")
                    break

    print(f"审核结束")


def process_activities(driver, activity_ids_list):
    current_hour = datetime.now().hour
    if 0 <= current_hour or current_hour < 24:
        while True:
            for activity_id in activity_ids_list:
                process_activity(driver, activity_id)
                process_creators(driver, activity_id)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"=======活动id：{activity_id}，已审核完成=======: {timestamp}")
    else:
        print("err")
