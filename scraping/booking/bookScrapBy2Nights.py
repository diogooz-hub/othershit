import time
import re
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

hotel_name = "Santa Eulalia Hotel & Spa"
days_to_check = 29

today = date.today()
startDate = today.strftime("%Y-%m-%d")
nextDate = (today + timedelta(days=3)).strftime("%Y-%m-%d")
print("Today's date:", startDate)

url = 'https://www.booking.com/'
driver.get(url)
time.sleep(5)
main_window = driver.current_window_handle

# accept cookies
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))).click()

# type name of the hotel on the search
search_box = driver.find_element(By.NAME, 'ss')
search_box.send_keys(hotel_name)

# select first dates
date_picker = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="searchbox-dates-container"]'))
)
date_picker.click()
time.sleep(2)

checkin_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{startDate}"]'))
)
checkin_element.click()

checkout_element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, f'span[data-date="{nextDate}"]'))
)
checkout_element.click()
submit_button = driver.find_element(By.XPATH, '//button/span[contains(text(),"Search")]/..')
submit_button.click()

# Click on dismiss pop-up on first search page
time.sleep(5)
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Dismiss sign in information."]'))).click()

# Find and click on the property
try:
    property_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@data-testid="title" and contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{hotel_name.lower()}")]'))
    )
    property_element.click()
except Exception as e:
    print(f"Error finding property element: {e}")
    driver.quit()
    exit()
time.sleep(10)
all_windows = driver.window_handles
for window in all_windows:
    if window != main_window:
        driver.switch_to.window(window)
        break

# SECOND PAGE #
def date_has_price(driver, date_str):
    try:
        date_element = driver.find_element(By.CSS_SELECTOR, f'span[data-date="{date_str}"]')
        price_element = date_element.find_element(By.XPATH, '..')
        return "—" not in price_element.text
    except NoSuchElementException:
        return False

def select_dates_in_property(driver, checkin_date, checkout_date):
    # Abrir o calendário do segundo elemento
    date_input_container = driver.find_elements(By.XPATH, '//div[@data-testid="searchbox-dates-container"]')[1]
    date_input_start = date_input_container.find_element(By.XPATH, './/button[@data-testid="date-display-field-start"]')
    date_input_start.click()
    time.sleep(1)

    # Loop para encontrar a data de check-in com preço
    while True:
        try:
            # Verificar se a data tem preço, se não, incrementar as datas até encontrar uma data com preço
            while not date_has_price(driver, checkin_date):
                checkin_date = (date.fromisoformat(checkin_date) + timedelta(days=3)).strftime("%Y-%m-%d")
                checkout_date = (date.fromisoformat(checkin_date) + timedelta(days=3)).strftime("%Y-%m-%d")
            
            checkin_element = driver.find_element(By.CSS_SELECTOR, f'span[data-date="{checkin_date}"]')
            checkin_element.click()
            break
        except NoSuchElementException:
            try:
                next_button = driver.find_element(By.XPATH, '//span[contains(@class, "d71f792240") and @role="button"]')
                next_button.click()
                time.sleep(1)
            except NoSuchElementException:
                print(f"Next button not found while looking for check-in date: {checkin_date}")
                break

    time.sleep(1)
    # Loop para encontrar a data de check-out
    while True:
        try:
            checkout_element = driver.find_element(By.CSS_SELECTOR, f'span[data-date="{checkout_date}"]')
            checkout_element.click()
            break
        except NoSuchElementException:
            try:
                next_button = driver.find_element(By.XPATH, '//span[contains(@class, "d71f792240") and @role="button"]')
                next_button.click()
                time.sleep(1)
            except NoSuchElementException:
                print(f"Next button not found while looking for check-out date: {checkout_date}")
                break
    
    submit_button = driver.find_element(By.XPATH, '//button/span[contains(text(),"Apply changes")]/..')
    submit_button.click()
    return checkin_date, checkout_date

# Função para extrair preços
def extract_prices(driver, startDate_str, nextDate_str):
    rooms = []
    rows = driver.find_elements(By.XPATH, '//*[@id="hprt-table"]/tbody/tr')

    current_room_type = None

    for row in rows:
        try:
            room_type_element = row.find_element(By.CLASS_NAME, 'hprt-roomtype-icon-link')
            room_type = room_type_element.text
            current_room_type = room_type  # Atualizar o tipo de quarto atual
        except:
            room_type = current_room_type  # Usar o tipo de quarto atual se não encontrar um novo

        try:
            guests = row.find_element(By.CLASS_NAME, 'hprt-occupancy-occupancy-info').text
            guests = re.search(r'\d+', guests).group()  # Extrair apenas o número de pessoas
        except:
            guests = "N/A"

        try:
            price_element = row.find_element(By.CLASS_NAME, 'hprt-price-block')
            price = price_element.text.split("\n")[0].strip()  # Capturar apenas a primeira linha do preço
            price = re.sub(r'Price\s+', '', price)
            price = re.sub(r'Includes taxes and charges', '', price).strip()
        except:
            price = "N/A"

        try:
            conditions_elements = row.find_elements(By.CSS_SELECTOR, 'td.hprt-table-cell-conditions ul.hprt-conditions-bui li')
            conditions = [element.text.strip() for element in conditions_elements]
        except:
            conditions = ["N/A"]

        room_data = {
            'date_searched': startDate_str,
            'room_type': room_type,
            'guests': guests,
            'price': price
        }

        for i, condition in enumerate(conditions):
            room_data[f'condition_{i+1}'] = condition

        rooms.append(room_data)

    return rooms

# Extrair preços para as primeiras datas selecionadas
df = pd.DataFrame()

all_rooms = extract_prices(driver, startDate, nextDate)
df = pd.concat([df, pd.DataFrame(all_rooms)], ignore_index=True)
df.to_excel(hotel_name + '_hotel_prices.xlsx', index=False)

# Loop para iterar pelas datas subsequentes
checked_days = 0
skipped_days = 0

while checked_days < days_to_check:
    try:
        # Selecionar novas datas no calendário da propriedade
        startDate, nextDate = select_dates_in_property(driver, startDate, nextDate)
        print(f"Checking prices for {startDate} to {nextDate}")
        time.sleep(2)

        # Esperar até que os elementos da tabela de preços estejam disponíveis novamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'hprt-table')))

        # Extrair preços para as novas datas
        all_rooms = extract_prices(driver, startDate, nextDate)
        df = pd.concat([df, pd.DataFrame(all_rooms)], ignore_index=True)
        df.to_excel(hotel_name + '_hotel_prices.xlsx', index=False)  # Save after each iteration
        time.sleep(2)
        
        # Incrementar o contador de dias verificados
        checked_days += 1
        
        # Incrementar as datas para a próxima iteração
        startDate = nextDate
        nextDate = (date.fromisoformat(startDate) + timedelta(days=3)).strftime("%Y-%m-%d")
        
    except Exception as e:
        print(f"Error on day {checked_days + 1}: {e}")
        skipped_days += 1

# Ajustar o total de dias a verificar
days_to_check += skipped_days

print("Data has been saved to " + hotel_name + "_hotel_prices.xlsx")

driver.quit()
