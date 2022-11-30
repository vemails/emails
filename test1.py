import re

from bs4 import BeautifulSoup
from selenium import webdriver

from utils import gmm, gsheets, telegram

gs = gsheets.GoogleSheets('germany')
all_emails = gs.ws.get_all_values()

links = []

e = [e for e in all_emails if e[1] == 'morozovat90@bk.ru']
for em in e:
    times = ''
    links = ''
    surnames = ''
    username = em[1]
    password = em[2]
    # soup = gmm.find_regex_in_email_with_title(username, password, 'Terminvereinbarung', "SEEN")
    soup = gmm.find_regex_in_email_with_title(username, password, 'Подтверждение записи', "UNSEEN")
    for s in soup:
        telegram.send_doc('VOLKAVA_NADZEYA.html', str(s))
        print(s)
        # element = s.find("a", href=lambda href: href and "https://service2.diplo.de/rktermin/extern/confirmation_appointment.do?" in href)
        # options = webdriver.ChromeOptions()
        # options.headless = True
        # driver = webdriver.Chrome(options=options)
        # link = element['href'].replace('&amp;', '&').replace('request_locale=de', 'request_locale=ru')
        # print(f'{e}::{link}')
    # driver.get(link)
    # ps = BeautifulSoup(driver.page_source, "lxml")
    # if confirmation := ps.find('fieldset'):
    #     try:
    #         confirmation = ' '.join(ps.find('fieldset').text.split())
    #         time = re.findall('время:(.*?)Место', confirmation)[0].strip()
    #         passport = re.findall('Visumbewerbers :(.*?)Grund', confirmation)[0].strip()
    #         surname = re.findall('Фамилия:(.*?)Электронная почта:', confirmation)[0].strip().replace('Имя: ', '')
    #         links = link if not links else f'{links}\n{link}'
    #         times = time if not times else f'{times}\n{time}'
    #         surnames = surname if not surnames else f'{surnames}\n{surname}'
    #         gs.ws.update_acell(f'G{int(e[0])+1}', surnames)
    #         gs.ws.update_acell(f'H{int(e[0])+1}', times)
    #         gs.ws.update_acell(f'I{int(e[0])+1}', links)
    #         same_email = True
    #     except Exception:
    #         pass

# for i, email in enumerate(all_emails):
#     try:
#         gmm.clear_mailbox(email[1], email[2])
#         print(i)
#     except Exception as e:
#         print(f'Email: {email[1]}. Ошибка: {str(e)}')

# soup = gmm.find_regex_in_email_with_title(username, password, 'Terminvereinbarung', "SEEN")
# for s in soup:
#     print(str(soup).replace('&amp;', '&').replace('request_locale=de', 'request_locale=ru'))
