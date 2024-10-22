from news import extract_email_password_pairs

emails_and_passwords = extract_email_password_pairs()
email, password = "schmitsondrini@gmail.com", "ftywfzlvjnl"

from seleniumbase import SB

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
    
    # Check if login was successful by verifying the URL or content
    current_url = sb.get_current_url()
    if "https://news.google.com/foryou" not in current_url:
        sb.open("https://news.google.com/foryou")

