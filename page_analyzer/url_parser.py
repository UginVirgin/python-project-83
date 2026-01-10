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
        h1 = h1_tag.string if h1_tag else ''

        title_tag = soup.find('title')
        title = title_tag.string if title_tag else ''

        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else ''

        return {
            'status_code': status_code,
            'h1': h1,
            'title': title,
            'description': description
        }
    except requests.RequestException as e:
        print(f"Ошибка запроса для URL {url}: {e}")
        # ВАЖНО: возвращаем словарь, а не None!
        return {
            'status_code': None,
            'h1': '',
            'title': '',
            'description': ''
        }
    except Exception as e:
        print(f"Неожиданная ошибка при парсинге URL {url}: {e}")
        return {
            'status_code': None,
            'h1': '',
            'title': '',
            'description': ''
        }
