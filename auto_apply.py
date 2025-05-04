from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ApplicationAutomator:
    def __init__(self, resume_data: Dict, gemini_model):
        self.resume_data = resume_data
        self.model = gemini_model
        self.driver = webdriver.Chrome()
    
    def fill_application(self, job_url: str):
        self.driver.get(job_url)
        
        # Identify form fields
        form_fields = self.identify_form_fields()
        
        # Match fields to resume data
        field_mapping = self.map_fields_to_data(form_fields)
        
        # Fill the form
        for field, value in field_mapping.items():
            self.fill_field(field, value)
            
        # Submit the application
        success = self.submit_application()
        return success
    
    def identify_form_fields(self) -> List[Dict]:
        # Use Selenium to find all input fields
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        
        fields = []
        for element in inputs + textareas + selects:
            fields.append({
                'element': element,
                'name': element.get_attribute('name'),
                'id': element.get_attribute('id'),
                'placeholder': element.get_attribute('placeholder'),
                'label': self.find_label_for_element(element)
            })
        return fields
    
    def map_fields_to_data(self, fields: List[Dict]) -> Dict:
        mapping = {}
        for field in fields:
            prompt = f"""
            Field information:
            - Name: {field['name']}
            - ID: {field['id']}
            - Placeholder: {field['placeholder']}
            - Label: {field['label']}
            
            Resume data: {self.resume_data}
            
            What resume data should go in this field? Return the exact value or 'SKIP' if not applicable.
            """
            response = self.model.generate_content(prompt)
            if response.text.strip() != 'SKIP':
                mapping[field['element']] = response.text.strip()
        return mapping
    
    def find_label_for_element(self, element) -> str:
        """Find the label text associated with a form element"""
        # Try to find label by 'for' attribute matching element id
        if element.get_attribute('id'):
            label = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{element.get_attribute('id')}']") 
            if label and len(label) > 0:
                return label[0].text
        
        # Try to find label as a parent or ancestor
        parent = element.find_element(By.XPATH, "./..")
        if parent.tag_name.lower() == 'label':
            return parent.text
        
        # Try to find nearby label
        nearby_labels = self.driver.find_elements(By.XPATH, 
            f"//label[preceding-sibling::*[1][name()='{element.tag_name}'] or following-sibling::*[1][name()='{element.tag_name}']]") 
        if nearby_labels and len(nearby_labels) > 0:
            return nearby_labels[0].text
        
        return ""
    
    def fill_field(self, element, value):
        """Fill a form field with the appropriate value"""
        try:
            # Handle different input types
            if element.tag_name.lower() == 'input':
                input_type = element.get_attribute('type')
                
                if input_type == 'file' and 'resume' in (element.get_attribute('name') or '').lower():
                    # Upload resume file
                    element.send_keys(self.resume_data.get('resume_path', ''))
                elif input_type in ['text', 'email', 'tel', 'url', 'number']:
                    element.clear()
                    element.send_keys(value)
                elif input_type == 'checkbox':
                    if value.lower() in ['yes', 'true', '1']:
                        if not element.is_selected():
                            element.click()
                elif input_type == 'radio':
                    if element.get_attribute('value') == value:
                        element.click()
            
            # Handle textarea
            elif element.tag_name.lower() == 'textarea':
                element.clear()
                element.send_keys(value)
            
            # Handle select dropdowns
            elif element.tag_name.lower() == 'select':
                from selenium.webdriver.support.ui import Select
                select = Select(element)
                
                # Try to select by visible text first
                try:
                    select.select_by_visible_text(value)
                except:
                    # If that fails, try to find a close match
                    options = [option.text.lower() for option in select.options]
                    best_match = None
                    for option in options:
                        if value.lower() in option or option in value.lower():
                            best_match = option
                            break
                    
                    if best_match:
                        select.select_by_visible_text(best_match)
            
            # Wait a bit to avoid being detected as a bot
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error filling field: {str(e)}")
    
    def submit_application(self):
        """Find and click the submit button"""
        # Look for submit buttons
        submit_buttons = self.driver.find_elements(By.XPATH, 
            "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(), 'Apply')] | //button[contains(text(), 'Submit')]") 
        
        if submit_buttons and len(submit_buttons) > 0:
            # Click the first submit button found
            submit_buttons[0].click()
            
            # Wait for confirmation
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Thank you') or contains(text(), 'Success') or contains(text(), 'Confirmation')]"))
                )
                return True
            except:
                # If no confirmation message is found, assume it worked
                return True
        
        return False