from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Opening browser using Selenium
browser = webdriver.Chrome()
browser.maximize_window()
browser.get("https://www.amazon.in/gp/bestsellers/?ref_=nav_em_cs_bestsellers_0_1_1_2")

# Parsing the main page
html_content = browser.page_source
doc = BeautifulSoup(html_content, "html.parser")
data = []

# Getting all Departments
department_names = []
department_urls = []
base = "https://www.amazon.in"
department_tags = doc.find_all("div", {"role": "group"})[0].find_all("a")
for i in range(0, len(department_tags)):
    department_names.append(department_tags[i].text.strip())
    department_urls.append(base + department_tags[i]["href"])

# Getting all Categories of every Department
for i in range(0, len(department_names)):
    print(f"Scraping Department {i + 1} {department_names[i]}")
    browser.get(department_urls[i])
    html_content = browser.page_source
    doc = BeautifulSoup(html_content, "html.parser")

    category_tags = doc.find_all("div", {"role": "group"})[0].find_all("a")
    special = base + category_tags[0]["href"]
    for j in range(0, len(category_tags)):
        print(f"Scraping Category {j + 1} {category_tags[j].text.strip()}")
        category_name = category_tags[j].text.strip()
        category_url = base + category_tags[j]["href"]

        # Getting Sub Categories of every Category
        browser.get(category_url)
        html_content = browser.page_source
        doc = BeautifulSoup(html_content, "html.parser")

        sub_category_tags = doc.find_all("div", {"role": "group"})[0].find_all("a")
        for k in range(0, len(sub_category_tags)):
            if special in base + sub_category_tags[0]["href"]:
                break
            else:
                print(f"Scraping Sub Category {k + 1} {sub_category_tags[k].text.strip()}")
                sub_category_name = sub_category_tags[k].text.strip()
                sub_category_url = base + sub_category_tags[k]["href"]

                # Getting Product Links of every Sub Category
                browser.get(sub_category_url)
                product_links = []
                
                # Going through 2 pages of products
                for l in range(0, 2):
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    html_content = browser.page_source
                    doc = BeautifulSoup(html_content, "html.parser")
    
                    product_tags = doc.find_all("div", {"id": "gridItemRoot"})
                    for m in range(0, len(product_tags)):
                        product_links.append(base + product_tags[m].find("a")["href"])
    
                    # Going to next page
                    if l == 1:
                        break
                    try:
                        next_page_tag = doc.find_all("div", {"class": "a-text-center"})[-1].find("li", {"class": "a-last"}).find("a")
                        browser.get(base + next_page_tag["href"])
                    except:
                        pass

                # Getting Info of every product
                for l in range(0, len(product_links)):
                    print(f"Scraping Product {l + 1}")
                    browser.get(product_links[l])
                    html_content = browser.page_source
                    doc = BeautifulSoup(html_content, "html.parser")
                    product_data = []

                    product_name = doc.find("span", {"id": "productTitle"}).text.strip()
                    try:
                        price_div = doc.find("div", {"class": "a-section a-spacing-none aok-align-center aok-relative"})
                        product_price = price_div.find("span", {"class": "a-price-whole"}).text.strip()
                        sale_discount = price_div.find("span", {"class": "a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage"}).text.strip().split("-")[1]
                    except:
                        product_price = None
                        sale_discount = None
                        
                    best_seller_rating = doc.find("div", {"class": "a-section a-spacing-base brand-snapshot-flex-row"}).text.strip().split("%")[0] + "%"
                    try:
                        ship_from = doc.find("div", {"id": "tabular-buybox"}).find_all("div", {"tabular-attribute-name": "Ships from"})[1].text.strip()
                    except:
                        ship_from = None
                    
                    sold_by = doc.find("div", {"class": "a-section a-spacing-medium brand-snapshot-flex-row"}).find("span").text.strip()
                    rating = doc.find("span", {"id": "acrPopover"}).find("a").find("span").text.strip()
                    product_description = doc.find_all("div", {"id": "aplus"})[-1].text.strip().replace("Product Description", "").replace("\n", "").replace("  ", " ")
                    try:
                        number_of_bought = doc.find("span", {"id": "social-proofing-faceout-title-tk_bought"}).find("span").text.strip().split("+")[0].replace("K", "000")
                    except:
                        number_of_bought = None

                    # Storing product data to list
                    data.append([product_name, product_price, sale_discount, best_seller_rating, ship_from, sold_by, rating, product_description, number_of_bought, department_names[i]])

# Saving product data to csv after sorting on sale discounts
df = pd.DataFrame(data, columns=["Product Name", "Product Price", "Sale Discount", "Best Seller Rating", "Ship From", "Sold by", "Rating", "Product Description", "Number of Bought", "Category"])
df = df.sort_values(by="Sale Discount", ascending=False)
df.to_csv("data.csv", index=None)

browser.close()