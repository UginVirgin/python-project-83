from bs4 import BeautifulSoup
import requests

def url_parser(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text

        status_code = response.status_code

        soup = BeautifulSoup(html, 'html.parser')

        h1_tag = soup.find('h1')
        h1 = h1_tag.string if h1_tag else None

        title_tag = soup.find('title')
        title = title_tag.string if title_tag else None

        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else None

        return {
            'status_code': status_code,
            'h1': h1,
            'title': title,
            'description': description
        }
    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None