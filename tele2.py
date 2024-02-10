import io
import sys
from bs4 import BeautifulSoup
import requests
import time
import logging
import html

BOT_TOKEN = '6724153008:AAF65osoXQ43V8D6WZszVf4HE4QT5YhXDio'
CHAT_ID = '656196513'  # Replace with the ID of the chat you want to send messages to
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

posted_posts = set()

def send_to_chat(title, price, image_url, view_more_link):
    try:
        api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        
        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            # Save the image locally
            with open('temp_image.jpg', 'wb') as f:
                f.write(response.content)
            
            # Open the image file
            photo_file = {'photo': open('temp_image.jpg', 'rb')}
            
            # HTML caption with clickable link around the image and "View More" link
            caption_html = f"<a href='{view_more_link}'>;</a><b>{html.escape(title)}</b>\n<b>Price</b>:{html.escape(price)}\n<a href='{view_more_link}'>View More</a>"

            params = {
                'chat_id': CHAT_ID,
                'caption': caption_html,
                'parse_mode': 'HTML'
            }

            response = requests.post(api_url, params=params, files=photo_file)
            response.raise_for_status()

            logger.info("Message sent successfully to the chat.")
        else:
            logger.error("Failed to download the image.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to the chat: {e}")

def scrape_and_send_to_chat():
    url = 'https://www.addisber.com/shop/'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve the webpage. Error: {e}")
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
    
        products = soup.select('.product-col')

        for product in products:
            image_url = product.select_one('.wp-post-image')['src']
            title = product.select_one('.woocommerce-loop-product__title').text.strip()
            category_list = product.select_one('.category-list').text.strip()
            href = product.select_one('.product-loop-title')['href']
            price_tag = product.select_one('.price').find('bdi')
            if price_tag:
                price = price_tag.text.strip()
            else:
                price = "Price not available"

            if title not in posted_posts:
                logger.info(f"Sending message to the chat for: {title}")
                send_to_chat(title, price, image_url, href)

                posted_posts.add(title)

            time.sleep(5)

    else:
        logger.warning(f"Failed to retrieve the webpage. Status code: {response.status_code}")

while True:
    scrape_and_send_to_chat()
    time.sleep(600)
