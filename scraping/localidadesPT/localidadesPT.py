from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import tkinter as tk
import time

service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

print(driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])

driver.get('https://www.visitarportugal.pt/braga')
time.sleep(5)

#consent
button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
button.click()
time.sleep(5)


# get concelhos
concelhos_list = driver.find_element(By.CLASS_NAME, 'tagsb')
#create list to save
list_concelhos = concelhos_list.find_elements(By.TAG_NAME, 'li')

#save and print concelhos
with open('concelhosBraga.txt', 'w') as f:
    for concelhos in list_concelhos:
        f.write(concelhos.text + '\n')
        print(concelhos.text)
#save concelhos list as variables to enter
concelho_links = {}

for concelhos in list_concelhos:
    try:
        concelho_name = concelhos.text
        concelho_link = concelhos.find_element(By.TAG_NAME, 'a').get_attribute('href')
        concelho_links[concelho_name] = concelho_link
    except NoSuchElementException:
        print(f"No link found for {concelhos.text}")

# iterate through the concelho_links dictionary
for concelho_name, concelho_link in concelho_links.items():
	print(f"Entering {concelho_name} page...")
	driver.get(concelho_link)

	#get localidades from each concelho
	try:
		localidades_list = driver.find_element(By.XPATH, "//h2[contains(text(),'Localidades deste concelho com informações')]/following-sibling::ul")
		localidades = localidades_list.find_elements(By.TAG_NAME, 'li')
		localidades_names = [localidade.text for localidade in localidades] #you can replace localidade with any valid variable name. It's just a temporary variable that will take the value of each element in the localidades list during the list comprehension.
		print(localidades_names)


		with open(f'{concelho_name}_localidades', 'w') as f:
			for localidade in localidades:
				f.write(localidade.text + '\n')
				print(localidade.text)
	except: NoSuchElementException
	print(f"No localidades found for {concelho_name}")

root = tk.Tk()
root.title("Script Finished")

label = tk.Label(root, text="Finished mothafocka!")
label.pack(padx=20, pady=20)

root.mainloop()
time.sleep(5)
driver.quit()
