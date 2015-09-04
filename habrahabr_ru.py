from bs4 import BeautifulSoup
import requests
import json
import io

url = 'http://habrahabr.ru/interesting/'
prefix = 'http://habrahabr.ru'
count = 0


def get_articles(base_url):
    global count
    r = requests.get(base_url).text
    soup = BeautifulSoup(r, 'lxml')

    posts = soup.find_all('div', class_='post')

    json_dumps = []
    for post in posts:
        try:
            title = post.find('a', class_='post_title').text
            link = post.find('a', class_='post_title').get('href')
        except AttributeError:
            title = post.select_one('div.inside > a').text
            link = post.select_one('div.inside > a')['href']
        try:
            pub_date = post.find('div', class_='published').text
        except AttributeError:
            pub_date = post.find('div', class_='date').text
        try:
            author = post.select_one('div.author > a').text
        except AttributeError:
            author = post.find('a', class_='byblog').text
        hubs = ', '.join([hub.text for hub in post.find_all('a', class_='hub')])

        post_info = {'title': title,
                     'url': link,
                     'pub_date': pub_date,
                     'author': author,
                     'hubs': hubs}

        json_dumps.append(post_info)

    if count <= 4:
        if soup.find('a', id='next_page'):
            count += 1
            next_page = prefix + soup.find('a', id='next_page').get('href')
            json_dumps.extend(get_articles(next_page))

    return json_dumps


def scrape():
    posts = []
    posts.extend(get_articles(url))

    with io.open('habr.json', 'w', encoding='utf-8') as f:
        data = json.dumps(posts, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
        f.write(data)

    return 'Done'


if __name__ == '__main__':
    print(scrape())
