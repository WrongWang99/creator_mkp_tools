from selenium import webdriver


def get_driver(user_data_dir):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    return webdriver.Chrome(options=options)