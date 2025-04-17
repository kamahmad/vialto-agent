from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
import time
import json

main_page_url = "https://vialtopartners.com/regional-alerts"

def scrape_article_data(soup, url):
    """Scrapes data from a single article page."""
    article_data = {}

# Extract title
    title_element = soup.find('h1', class_='text__StyledText-sc-e4269771-0 iwqZyj') or soup.find('h1', class_='text__StyledText-sc-e4269771-0 iwjpPt')
    article_data['title'] = title_element.text.strip() if title_element else None

    # Extract the publication date
    date_element = soup.find('p', class_='text__StyledText-sc-e4269771-0 eeBqnz hero-small__StyledAttributionText-sc-97bf421f-5 eiBXnl')
    article_data['date'] = date_element.text.strip() if date_element else None

    # Extract content
    content_container = soup.find('div', class_='rich-content-regional-alerts__StyledRichContent-sc-7b7c470b-2 bTntuL')
    if content_container:
        content_parts = [element.text.strip() for element in content_container.find_all(['p', 'h2'])]
        article_data['content'] = '\n\n'.join(content_parts).strip()
    else:
        article_data['content'] = None

    article_data['url'] = url
    return article_data

def get_article_links(url):
    """Extracts all article links from the main page."""
    driver = webdriver.Chrome()
    try:
        driver.get(url)
        time.sleep(3)
        article_links = set()

        while True:
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link_elements = soup.find_all('a', class_='button__StyledAnchor-sc-1ab41720-0')  # Your article link class
                for link_element in link_elements:
                    href = link_element.get('href')
                    if href:
                        if not href.startswith('http'):
                            href = main_page_url + href
                        article_links.add(href)

                load_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".button__StyledButton-sc-1ab41720-1.jZNWpQ"))
                )
                driver.execute_script("arguments[0].click();", load_more_button)
                time.sleep(3)
            except NoSuchElementException:
                print("Load More button not found. Assuming all articles loaded.")
                break
            except ElementNotInteractableException:
                print("Load More button is not interactable. Assuming all articles loaded.")
                break
            except Exception as e:  
                print(f"An error occurred while trying to load more: {e}")
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        return article_links   

def scrape_articles(article_links):
    """Scrapes data from each article page."""

    driver = webdriver.Chrome()
    all_article_data = []
    for article_url in list(article_links):
        print(f"\nScraping data from: {article_url}")
        try:
            driver.get(article_url)
            time.sleep(2)
            article_soup = BeautifulSoup(driver.page_source, 'html.parser')
            article_data = scrape_article_data(article_soup, article_url)
            if article_data:
                all_article_data.append(article_data)
        except Exception as e:
            print(f"Error scraping {article_url}: {e}")
            continue

    driver.quit()
    return all_article_data


"""article_links = list(get_article_links(main_page_url))
print("\nAll article links found.")

with open("links.txt", "w") as f:
    for link in article_links:
        f.write(link + "\n")

print("Article links written to links.txt") """

with open("links.txt", "r") as f:
    article_links = [line.strip() for line in f]

all_article_data = scrape_articles(article_links)

with open("article_data.json", "w", encoding='utf-8') as f:
    json.dump(all_article_data, f, indent=4, ensure_ascii=False)

print("Article data saved to article_data.json")










def scrape_article_data2(soup, url):
    """Scrapes data from a single article page."""
    article_data = {}

    title_classes = [
        'text__StyledText-sc-e4269771-0 iwqZyj',
        'text__StyledText-sc-e4269771-0 iwjpPt',
    ]

    for class_name in title_classes:
        title_element = soup.find('h1', class_=class_name)
        if title_element:
            article_data['title'] = title_element.text.strip()
            break

    # Extract the publication date
    date_element = soup.find('p', class_='text__StyledText-sc-e4269771-0 eeBqnz hero-small__StyledAttributionText-sc-97bf421f-5 eiBXnl')
    article_data['date'] = date_element.text.strip() if date_element else None

    # Extract the main content of the article
    content_container = soup.find('div', class_='rich-content-regional-alerts__StyledRichContent-sc-7b7c470b-2 bTntuL')

    if content_container:
        main_content_parts = []
        content_elements = content_container.find_all(['p', 'h2'])

        # 3. Iterate and extract text
        for element in content_elements:
            main_content_parts.append(element.text.strip())
            if element.text.strip() == 'Contact us':
                break
        
        # 4. Join the extracted text with double line breaks for paragraphs and single for headings
        main_content = "\n\n".join(part for part in main_content_parts if element.name == 'p')
        main_content += "\n".join(part for part in main_content_parts if element.name.startswith('h'))
        article_data['content'] = main_content.strip()
    else:
        article_data['content'] = None

    article_data['url'] = url

    return article_data