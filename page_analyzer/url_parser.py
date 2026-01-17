from bs4 import BeautifulSoup
import requests

def url_parser(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(
                    {
                'title': soup.find('title').text if soup.find('title') else None,
                'h1': soup.find('h1').text if soup.find('h1') else None,
                'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
                'status_code': response.status_code
            }
            )
            return {
                'title': soup.find('title').text if soup.find('title') else None,
                'h1': soup.find('h1').text if soup.find('h1') else None,
                'description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else None,
                'status_code': response.status_code
            }
        else:
            return {'error': 'Произошла ошибка при проверке'}
    except requests.RequestException:
        return {'error': 'Произошла ошибка при проверке'}
