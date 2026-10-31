from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_button = (By.ID, "login-button")
        self.error_message = (By.ID, "error-message")
    
    def open(self):
        self.driver.get("https://example.com/login")
    
    def enter_username(self, username):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.username_input)
        ).send_keys(username)
    
    def enter_password(self, password):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.password_input)
        ).send_keys(password)
    
    def click_login(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.login_button)
        ).click()
    
    def get_error_message(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.error_message)
        ).text
    
    def is_error_message_displayed(self):
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.error_message)
            ).is_displayed()
        except:
            return False
