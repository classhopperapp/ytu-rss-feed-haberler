import requests
from bs4 import BeautifulSoup
import csv
import datetime
import re
import xml.dom.minidom as md
from xml.etree.ElementTree import Element, SubElement, tostring
import html

def scrape_ytu_announcements():
    """
    YTÜ haberler sayfasından başlık ve linkleri çeker.
    """
    url = 'https://www.yildiz.edu.tr/universite/haberler'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [a for a in soup.find_all('a', href=True) if a['href'].startswith('/universite/haberler/') and a.get_text(strip=True)]
        announcements = []
        for a in links:
            title = a.get_text(strip=True)
            url_full = f"https://www.yildiz.edu.tr{a['href']}"
            announcements.append({'title': title, 'url': url_full, 'date': None})
        return announcements
    except Exception as e:
        print(f"Haberler çekilemedi: {e}")
        return []

def generate_rss(announcements, filename):
    # RSS kökünü oluştur
    rss = Element('rss', {'version': '2.0'})
    channel = SubElement(rss, 'channel')
    title = SubElement(channel, 'title')
    title.text = 'YTÜ Haberler'
    link = SubElement(channel, 'link')
    link.text = 'https://www.yildiz.edu.tr/universite/haberler'
    description = SubElement(channel, 'description')
    description.text = 'Yıldız Teknik Üniversitesi Resmi Haberler'
    for ann in announcements:
        item = SubElement(channel, 'item')
        item_title = SubElement(item, 'title')
        # Tarihi başlığa ekle
        if ann.get('date'):
            item_title.text = f"{ann['title']} ({ann['date']})"
        else:
            item_title.text = ann['title']
        item_link = SubElement(item, 'link')
        item_link.text = ann['url']
        # pubDate alanı ekle
        if ann.get('date'):
            try:
                pubdate = datetime.datetime.strptime(ann['date'], "%Y-%m-%d")
                pubdate_str = pubdate.strftime("%a, %d %b %Y 12:00:00 +0300")
                pubDate = SubElement(item, 'pubDate')
                pubDate.text = pubdate_str
            except Exception:
                pass
    rough_string = tostring(rss, 'utf-8')
    reparsed = md.parseString(rough_string)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))
    print(f"RSS beslemesi başarıyla oluşturuldu: {filename}")

if __name__ == "__main__":
    print("YTÜ haberleri çekiliyor...")
    announcements = scrape_ytu_announcements()
    if announcements:
        print(f"{len(announcements)} haber bulundu.")
        # generate_rss fonksiyonunu haberler için kullan
        generate_rss(announcements, "ytu_haberler.xml")
        for i, ann in enumerate(announcements[:5], 1):
            print(f"Haber {i}:")
            print(f"Başlık: {ann['title']}")
            print(f"URL: {ann['url']}")
            print("-"*50)
    else:
        print("Hiç haber bulunamadı. RSS oluşturulamadı.")