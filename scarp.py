import csv
import re
import urllib.request
import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome('../chromedriver.exe', options=options)

action = ActionChains(driver)
wait = WebDriverWait(driver, 5)
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

postal = []

def no_of_x_in_y(x, y):
    number = 0
    for i in y:
        if i == x:
            number = number + 1

    return number


def if_email(case):
    index_at_the_rate = 0
    index_dot = 0
    for i in range(0, len(case)):
        if case[i] == "@":
            index_at_the_rate = i
            break
    if no_of_x_in_y(".", case[index_at_the_rate:len(case)]) == 0:
        return 0

    if len(case[0:index_at_the_rate]) == 0:
        return 0

    if no_of_x_in_y("@", case) != 1:
        return 0
    else:
        return 1

with open("zipcode_client_sam.csv", "r") as f:
    reader = csv.reader(f, delimiter="\t")
    for line in reader:
        line = line[0].split(',')
        if len(line[0]) == 3:
            line[0] = '00' + line[0]
            postal.append(line)
        elif len(line[0]) == 4:
            line[0] = '0' + line[0]
            postal.append(line)
        else:
            postal.append(line)

# print(postal)
final = []
for zip in postal:
    print(zip[0])

    driver.get(f"https://www.yellowpages.com/search?search_terms=jewelry%20stores&geo_location_terms={zip[0]}")
    page = 1
    while True:
        cards = driver.find_elements_by_xpath('//div[@class="info"]')[:-5]
        for card in cards:
            data = {}
            address = ''
            try:
                address += card.find_element_by_xpath('.//div[@class="locality"]').text.lower()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            try:
                address += card.find_element_by_xpath('.//p[@class="adr"]').text.lower()
            except selenium.common.exceptions.NoSuchElementException:
                pass
            if zip[1].lower() in address or zip[0] in address:
                data['name'] = card.find_element_by_xpath('.//a[@class="business-name"]').text
                try:
                    data['ph'] = card.find_element_by_xpath('.//div[@class="phones phone primary"]').text
                except:
                    data['ph'] = ''

                address = ''
                try:
                    address += card.find_element_by_xpath('.//div[@class="street-address"]').text + ', '
                except selenium.common.exceptions.NoSuchElementException:
                    pass
                try:
                    address += card.find_element_by_xpath('.//div[@class="locality"]').text
                except selenium.common.exceptions.NoSuchElementException:
                    pass

                data['address'] = address
                data['zip'] = zip[0]
                data['county'] = zip[1]

                try:
                    data['exp'] = card.find_element_by_xpath('.//div[@class="number"]').text
                except:
                    data['exp'] = ''
                try:
                    data['reviews'] = card.find_element_by_xpath('.//span[@class="count"]').text[1:-1]
                except:
                    data['reviews'] = ''
                try:
                    data['website'] = card.find_element_by_xpath('.//a[@class="track-visit-website"]').get_attribute('href')

                    if data['website']:
                        try:
                            webdata = urllib.request.urlopen(data['website'], timeout=5)
                            soup = BeautifulSoup(webdata.read().decode(), 'lxml')
                            a = soup.get_text()
                            phone = re.findall(r"((?:\d{3}|\(\d{3}\))?(?:\s|-|\.)?\d{3}(?:\s|-|\.)\d{4})", a)
                            emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", a)
                            if phone:
                                data['webph'] = ', '.join(phone)
                            else:
                                data['webph'] - ''
                            if emails:
                                data['webmail'] = ', '.join(emails)
                            else:
                                data['webmail'] = ''
                        except:
                            data['webph'] = ''
                            data['webmail'] = ''
                            pass
                except:
                    data['webph'] = ''
                    data['webmail'] = ''
                    data['website'] = ''
                try:
                    data['rating'] = ''
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating five  "]')
                    data['rating'] = '5'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="class="result-rating four half "]')
                    data['rating'] = '4.5'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating four  "]')
                    data['rating'] = '4'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating three half "]')
                    data['rating'] = '3.5'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating three  "]')
                    data['rating'] = '3'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating two half "]')
                    data['rating'] = '2.5'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating two  "]')
                    data['rating'] = '2'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating one half "]')
                    data['rating'] = '1.5'
                except:
                    pass
                try:
                    data['rating'] = card.find_element_by_xpath('.//div[@class="result-rating one  "]')
                    data['rating'] = '1'
                except:
                    pass
            if data:
                final.append([value for value in data.values()])
                # pprint(data)
        with open("new.csv", "a") as fp:
            wr = csv.writer(fp, lineterminator='\n')
            wr.writerows(final)
        final = []
        try:
            temp = driver.find_element_by_xpath('//a[@class="next ajax-page"]')
            page += 1
            driver.get(f"https://www.yellowpages.com/search?search_terms=jewelry%20stores&geo_location_terms={zip[0]}&page={page}")
        except:
            break
