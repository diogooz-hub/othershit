import time
import tkinter as tk
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

driver.get('https://www.visitportugal.com/pt-pt/encontre-tipo/?context=405&&regioes=285')
time.sleep(5)

# Consent
frame = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Consent window"]')
driver.switch_to.frame(frame)
button = driver.find_element(By.CSS_SELECTOR, '.sc-furwcr.jhwOCG.button.button--filled.button__acceptAll')
button.click()
time.sleep(5)
driver.switch_to.default_content()

# Restaurants list
restaurants_data = []
pages = 0

while True:
    time.sleep(2)
    restaurant_elements = driver.find_elements(By.CLASS_NAME, 'search-result-name')
    contact_elements = driver.find_elements(By.CLASS_NAME, 'search-result-desc')

    for name_element, contact_element in zip(restaurant_elements, contact_elements):
        restaurant_name = name_element.text

        # Extract contact information using regular expressions
        contact_info = contact_element.text
        telefone_match = re.search(r'Telefone: ([^\n]+)', contact_info)
        telefone = telefone_match.group(1).strip() if telefone_match else ""

        email_match = re.search(r'E-mail: (.+)', contact_info)
        email = email_match.group(1).strip() if email_match else ""

        restaurants_data.append({'name': restaurant_name, 'telefone': telefone, 'email': email})

    # Save data to file
    with open('restaurants_porto.txt', 'w') as file:
        for restaurant in restaurants_data:
            file.write(f"Name: {restaurant['name']}\n")
            file.write(f"Telefone: {restaurant['telefone']}\n")
            file.write(f"Email: {restaurant['email']}\n\n")

    # Find and click the Next button
    next_button = driver.find_element(By.XPATH, '//li[contains(@class, "pager-next")]/a')
    if 'disabled' in next_button.get_attribute('class'):
        break
    next_button.click()
    pages += 1
    time.sleep(5)  # Add a delay to ensure the next page loads properly

# Close the browser
driver.quit()

print(f"Finished scraping {pages} pages")
root = tk.Tk()
root.title("Script Finished")

label = tk.Label(root, text="Finished mothafocka!")
label.pack(padx=20, pady=20)

root.mainloop()