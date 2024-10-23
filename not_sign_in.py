import json, os
from seleniumbase import SB
from selenium.webdriver.common.by import By
from datetime import datetime
from tqdm import tqdm
from logging import getLogger

locations = {
    "SF": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en",  # San Francisco
    "NY": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en",  # New York
    "CA": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en",  # Chicago
    "LA": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en",  # Los Angeles
    "HT": "https://news.google.com/?hl=en-US&gl=US&ceid=US:en",  # Houston
}


def extract_email_password_pairs(file_path = "accounts.txt"):
    '''
    return a list of emails
    [(email, password, backup_email, backup_password, region), ...]
    '''
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    for line in lines:
        email, password, backup_email, backup_password, region = line.strip().split('----')
        yield email, password, backup_email, backup_password, region
    # strip the last two ascii for each line
    

# Function to create folder based on email and today's date
def create_save_folder(email):
    today_date = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join("save", email, today_date)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def scrape_articles(sb, location_name, location_url, folder_path):
    news_data = []
    num_articles = 0

    sb.open(location_url)

    while num_articles < 50:  # Continue scrolling until we get at least 50 articles
        articles = sb.find_elements(By.TAG_NAME, "article")

        for article in articles:
            if num_articles >= 50:
                break
            try:
                # Scrape sourceSrc (media image link) and sourceText if the new structure exists
                try:
                    image_container = article.find_element(By.CSS_SELECTOR, ".MCAGUe")
                    source_element = article.find_element(By.CSS_SELECTOR, ".qEdqNd")
                    source = source_element.get_attribute("src") if source_element else "No Source"
                except:
                    # Fallback for old structure
                    source_element = article.find_element(By.CSS_SELECTOR, ".vr1PYe")
                    source = source_element.text if source_element else "No Source"

                # Scrape title and link (applies to both structures)
                title_element = article.find_element(By.CSS_SELECTOR, ".gPFEn")
                title = title_element.text if title_element else "No Title"
                text_link = title_element.get_attribute("href") if title_element else "No Link"

                # Scrape the datetime and time text using the correct time tag
                datetime_element = article.find_element(By.TAG_NAME, "time")
                datetime = datetime_element.get_attribute("datetime") if datetime_element else "No DateTime"
                time_text = datetime_element.text if datetime_element else "No Time"

                # Add the scraped data to the list
                news_data.append({
                    "sourceText": source,
                    "titleText": title,
                    "datetime": datetime,
                    "timeText": time_text,
                    "textLink": text_link
                })

                num_articles += 1
                print(f"Scraped article {num_articles}: {title} - {source} - {datetime} - {time_text} - {text_link}")

            except Exception as e:
                print(f"Error scraping article: {e}")
                continue

        # Scroll down the page to load more articles
        sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sb.sleep(3)  # Pause to allow new content to load

    save_path = os.path.join(folder_path, f"{location_name}.json")
    with open(save_path, 'w') as f:
        json.dump(news_data, f, indent=4)
    print(f"Saved {num_articles} articles to {save_path}")


def main_scraper(email, password):
    folder_path = create_save_folder(email)
    if len(os.listdir(folder_path)) >= len(locations):
        print(f"Scraping for {email} is already done, skipping...")
        return
    with SB(uc = True, headless = True) as sb:
        print(f"Scraping news for {email}...")
        # otherwise we have to endure signin
        sb.open("https://accounts.google.com/signin")

        # Type in the email address (wait for the input field)
        sb.wait_for_element_visible('input[type="email"]', timeout = 20)
        sb.type('input[type="email"]', email)
        sb.click('button:contains("Next")')

        # Wait for the password input to appear
        sb.wait_for_element_visible('input[type="password"]', timeout = 20)
        sb.type('input[type="password"]', password)
        sb.click('button:contains("Next")')

        # Add a delay to allow for login completion
        sb.sleep(5)  # Increase if 2FA is needed or for more processing time

        # Check if the "fingerprint unlock" page appears
        if sb.is_element_visible('button:contains("以后再说")'):
            sb.click('button:contains("以后再说")')

        # Loop through each location and scrape the articles
        for location_name, location_url in locations.items():
            # first check if the file existed
            if os.path.exists(f"{folder_path}/{location_name}.json"):
                print(f"File {location_name} already existed, skip scraping...")
                continue
            print(f"Scraping news for {location_name}...")
            scrape_articles(sb, location_name, location_url, folder_path)

if __name__ == "__main__":
    # use tqdm to show progress
    for email, password, backup_email, backup_password, region in tqdm(extract_email_password_pairs()):
        main_scraper(email, password)
    print("All done!")
