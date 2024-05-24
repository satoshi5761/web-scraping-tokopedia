import time
import os, sys
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

class Scraper:
    def __init__(self):
        options = webdriver.ChromeOptions() 
        options.add_argument("start-maximized")
        # to supress the error messages/logs
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # locate where chrome driver is located
        your_os = os.name
        if your_os == 'posix': # windows os
            possible_location = os.popen("locate chromedriver.exe").read().rstrip().split()
            if not possible_location:
                print("chromedriver not found")
                print("please install here:", "https://developer.chrome.com/docs/chromedriver/downloads")
                sys.exit()
            else:
                print(">>> chromedriver found")
                for path in possible_location:
                    print("adding -->", path, "to your path")
                    os.environ['PATH'] += ':' + path

        elif your_os == 'nt':
            possible_location = os.popen("where /R C: chromedriver.exe").read().rstrip().split()
            if not possible_location:
                print("chromedriver not found under C: drive")
                print("please install here:", "https://developer.chrome.com/docs/chromedriver/downloads")
                sys.exit()
            else:
                print(">>> chromedriver found")
                for path in possible_location:
                    print("adding -->", path, "to your path")
                    os.environ['PATH'] += ';' + path

        else:
            print("please add the path manually") # by adding "executable_path=r'Your/Path/ToChrome/Driver.exe" |
            sys.exit() # and erase this line <------------------------------------------------------------------|
#                                                                                                               |
#                                                                                                               |
        self.driver = webdriver.Chrome(options=options)# <------------------------------------------------------|

    
    def get_data(self):
        self.driver.get(input(">>> enter tokopedia link: "))
        pages = input(">>> banyak halaman (kosongkan untuk semua halaman): ")

        if pages.isdigit():
            pages = int(pages)
        else:
            pages = 2 * 10 ** 9

        data = []
        
        # Scrap datas from 10 pages
        for page in range(pages):

            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#zeus-root')))
            time.sleep(2)

            # Scroll the page until the end of the page
            scroll = 15
            for i in range(scroll):
                self.driver.execute_script('window.scrollBy(0,500)')
                time.sleep(0.5)

                
        
            # Parse the page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Scrap website pages
            for item in soup.find_all('div', class_='css-1asz3by'):
                
                # Scrap product names and titles
                product_name = item.find('div', class_='prd_link-product-name css-3um8ox')
                try:
                    product_name = product_name.get_text()
                except AttributeError:
                    product_name = ''

                price = item.find('div', class_='prd_link-product-price css-h66vau')
                try:
                    price = price.get_text()
                except AttributeError:
                    price = ''


                # Check if there is any rating or not
                rates = item.find('span', class_='prd_rating-average-text css-t70v7i')
                if rates is not None:
                    rate = item.find('span', class_='prd_rating-average-text css-t70v7i').get_text()
                else:
                    rate = ''

                # Check if there is any sold item or not
                sold_items = item.find('span', class_='prd_label-integrity css-1sgek4h')
                if sold_items is not None:
                    sold = item.find('span', class_='prd_label-integrity css-1sgek4h').get_text()
                else:
                    sold = 0

                # Scrap address details
                address = item.find_all('div', class_='css-1rn0irl')
                location = ''
                seller = ''

                for item2 in address:
                    try :
                        location = item2.find('span', class_='prd_link-shop-loc css-1kdc32b flip').get_text()
                    except AttributeError:
                        location = ''
                    try: 
                        seller = item2.find('span', class_='prd_link-shop-name css-1kdc32b flip').get_text()
                    except AttributeError:
                        seller = ''

                data.append(
                    {
                        'Penjual' : seller,
                        'Lokasi': location,
                        'Produk': product_name,
                        'Harga': price,
                        'Rate': rate,
                        'Tejual': sold
                    }
                )


            time.sleep(1)

            end_of_page = False
            while True:
                try:
                    # get the element
                    try:
                        # if in a spesific shop
                        link = self.driver.find_element(By.CSS_SELECTOR, "a[data-testid='btnShopProductPageNext']")
                    except:
                        # if not in a spesific shop
                        link = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Laman berikutnya']")

                    print("next page found ... clicking")

                    # use javascript why
                    self.driver.execute_script("arguments[0].click();", link)
                    break
                except StaleElementReferenceException:
                    print("error clicking ... trying")
                    continue
                except NoSuchElementException:
                    print("end of page ... exiting")
                    end_of_page = True
                    break
            
            if end_of_page:
                break

        self.driver.close()
        
        return data

if __name__ == '__main__':
    scraper = Scraper()
    data = scraper.get_data()

    df = pd.DataFrame(data)
    df.to_csv('dataset.csv', index=False) 