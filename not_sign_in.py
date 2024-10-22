from news import extract_email_password_pairs
import json
from seleniumbase import SB
from selenium.webdriver.common.by import By

emails_and_passwords = extract_email_password_pairs()
email, password = "schmitsondrini@gmail.com", "ftywfzlvjnl"
with SB(uc=True) as sb:
    # Open the Google Sign-in page
    sb.open("https://accounts.google.com/signin")
    
    # Type in the email address (wait for the input field)
    sb.wait_for_element_visible('input[type="email"]', timeout=15)
    sb.type('input[type="email"]', email)
    sb.click('button:contains("Next")')
    
    # Wait for the password input to appear
    sb.wait_for_element_visible('input[type="password"]', timeout=15)
    sb.type('input[type="password"]', password)
    sb.click('button:contains("Next")')
    
    # Add a delay to allow for login completion
    sb.sleep(5)  # Increase if 2FA is needed or for more processing time

    # Check if the "fingerprint unlock" page appears
    if sb.is_element_visible('button:contains("以后再说")'):
        sb.click('button:contains("以后再说")')
    
    # Ensure we're on the "For You" page for Google News with US location
    sb.open("https://news.google.com/foryou?hl=en-US&gl=US&ceid=US:en")
    
    # Add a small delay to allow the page to load
    sb.sleep(3)

    # Initialize a list to hold news data
    news_data = []
    num_articles = 0

    # Scroll and collect news articles until we reach 50
    while num_articles < 50:
        # Find all article elements on the page
        
        articles = sb.find_elements(By.TAG_NAME, "article")

        for article in articles:
            if num_articles >= 50:
                break
            try:
                # Scrape the source (media name) using the correct class "vr1PYe"
                source_element = article.find_element(By.CSS_SELECTOR, ".vr1PYe")
                source = source_element.text if source_element else "No Source"

                # Scrape the title and link using the correct class "gPFEn"
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
        sb.scroll_to_bottom()
        sb.sleep(2)  # Allow time for more articles to load


    with open("news_data.json", "w") as f:
        json.dump(news_data, f, indent=4)
