from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import cv2
import numpy as np
import logging
import json
from datetime import datetime
import os
from PIL import Image
import io
import base64
from ml_model import TrainingSession, AdRatingModel

class WebAgent:
    def __init__(self):
        self.driver = None
        self.is_recording = False
        self.actions_log = []
        self.training_session = TrainingSession()
        self.ad_rating_model = AdRatingModel()
        self.setup_logging()

    def setup_logging(self):
        """Initialize logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            filename=os.path.join(log_dir, f'agent_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def initialize(self, chrome_options=None):
        """Initialize the web browser with optional Chrome profile settings"""
        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            
            if chrome_options:
                if 'user_data_dir' in chrome_options:
                    options.add_argument(f"user-data-dir={chrome_options['user_data_dir']}")
                if 'profile_directory' in chrome_options:
                    options.add_argument(f"profile-directory={chrome_options['profile_directory']}")
            
            # Add additional options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=9222")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            logging.info("Browser initialized successfully with custom profile")
        except Exception as e:
            logging.error(f"Failed to initialize browser: {str(e)}")
            raise

    def start_recording(self):
        """Start recording user actions"""
        self.is_recording = True
        logging.info("Started recording user actions")

    def stop_recording(self):
        """Stop recording user actions"""
        self.is_recording = False
        self.save_recorded_actions()
        logging.info("Stopped recording user actions")

    def save_recorded_actions(self):
        """Save recorded actions to a JSON file"""
        if not self.actions_log:
            return

        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        filename = os.path.join(log_dir, f'actions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(filename, 'w') as f:
            json.dump(self.actions_log, f, indent=4)
        
        logging.info(f"Saved recorded actions to {filename}")
        self.actions_log = []

    def record_action(self, action_type, params=None):
        """Record an action if recording is enabled"""
        if self.is_recording:
            action = {
                'timestamp': datetime.now().isoformat(),
                'type': action_type,
                'params': params or {}
            }
            self.actions_log.append(action)
            self.training_session.add_action(action)
            logging.info(f"Recorded action: {action_type}")

    def navigate_to(self, url):
        """Navigate to a specific URL"""
        try:
            self.driver.get(url)
            self.record_action('navigate', {'url': url})
            logging.info(f"Navigated to {url}")
        except Exception as e:
            logging.error(f"Failed to navigate to {url}: {str(e)}")
            raise

    def click(self, x, y):
        """Click at specific coordinates"""
        try:
            script = f"document.elementFromPoint({x}, {y}).click();"
            self.driver.execute_script(script)
            self.record_action('click', {'x': x, 'y': y})
            logging.info(f"Clicked at coordinates ({x}, {y})")
        except Exception as e:
            logging.error(f"Failed to click at ({x}, {y}): {str(e)}")
            raise

    def scroll(self, direction='down', amount=300):
        """Scroll the page"""
        try:
            scroll_script = f"window.scrollBy(0, {amount if direction == 'down' else -amount});"
            self.driver.execute_script(scroll_script)
            self.record_action('scroll', {'direction': direction, 'amount': amount})
            logging.info(f"Scrolled {direction} by {amount} pixels")
        except Exception as e:
            logging.error(f"Failed to scroll {direction}: {str(e)}")
            raise

    def capture_screenshot(self, element=None):
        """Capture screenshot of the page or specific element"""
        try:
            if element:
                screenshot = element.screenshot_as_png
            else:
                screenshot = self.driver.get_screenshot_as_png()
            
            image = Image.open(io.BytesIO(screenshot))
            return np.array(image)
        except Exception as e:
            logging.error(f"Failed to capture screenshot: {str(e)}")
            raise

    def find_element_by_image(self, template_image):
        """Find an element on the page using template matching"""
        try:
            screenshot = self.capture_screenshot()
            template = cv2.imread(template_image)
            
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > 0.8:  # Threshold for match confidence
                return max_loc
            return None
        except Exception as e:
            logging.error(f"Failed to find element by image: {str(e)}")
            raise

    def get_page_text(self):
        """Extract all text content from the page"""
        try:
            return self.driver.find_element(By.TAG_NAME, "body").text
        except Exception as e:
            logging.error(f"Failed to get page text: {str(e)}")
            raise

    def close(self):
        """Close the browser and clean up"""
        try:
            if self.driver:
                self.driver.quit()
            if self.is_recording:
                self.stop_recording()
            logging.info("Browser closed successfully")
        except Exception as e:
            logging.error(f"Failed to close browser: {str(e)}")
            raise

    def start_training_sequence(self):
        """Start a new training sequence"""
        self.training_session.start_sequence()
        self.start_recording()

    def end_training_sequence(self, rating):
        """End current training sequence with rating"""
        self.stop_recording()
        self.training_session.end_sequence(rating)

    def train_model(self):
        """Train the model on collected sequences"""
        return self.training_session.train_model()

    def predict_rating(self):
        """Predict rating based on current action sequence"""
        if not self.actions_log:
            return None
        return self.ad_rating_model.predict(self.actions_log)

    def detect_ad_content(self):
        """Detect and analyze ad content on the page"""
        try:
            # Find common ad selectors
            ad_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "[class*='ad'], [id*='ad'], [class*='advertisement'], iframe[src*='ad']")
            
            ad_data = {
                'count': len(ad_elements),
                'positions': [],
                'types': []
            }

            for element in ad_elements:
                try:
                    location = element.location
                    ad_data['positions'].append(location)
                    
                    # Determine ad type
                    if element.tag_name == 'iframe':
                        ad_data['types'].append('iframe')
                    elif element.find_elements(By.TAG_NAME, 'video'):
                        ad_data['types'].append('video')
                    elif element.find_elements(By.TAG_NAME, 'img'):
                        ad_data['types'].append('image')
                    else:
                        ad_data['types'].append('text')
                except:
                    continue

            return ad_data
        except Exception as e:
            logging.error(f"Failed to detect ad content: {str(e)}")
            return None

    def save_training_data(self, path='training_data'):
        """Save collected training data"""
        self.training_session.save_training_data(path)

    def load_training_data(self, filename):
        """Load training data from file"""
        self.training_session.load_training_data(filename)

if __name__ == "__main__":
    # Example usage with ad rating
    agent = WebAgent()
    try:
        agent.initialize()
        agent.start_training_sequence()
        agent.navigate_to("https://www.example.com")
        
        # Detect and analyze ads
        ad_data = agent.detect_ad_content()
        if ad_data and ad_data['count'] > 0:
            # Interact with first ad
            first_ad_pos = ad_data['positions'][0]
            agent.scroll('down', first_ad_pos['y'])
            agent.click(first_ad_pos['x'], first_ad_pos['y'])
        
        # End sequence with rating
        agent.end_training_sequence(1)  # 1 for positive rating
        
        # Train model
        agent.train_model()
    finally:
        agent.close()
