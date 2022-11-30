import base64
import json
import logging
import os
import re
import sys
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver

from utils import gsheets, gmm, telegram, users


def get_user(email):
    logging.warning('1')
    us = users.get_users('Inviting') + users.get_users('Tourism')
    logging.warning('2')
    user = [user for user in us if email in user['vc_comment']]
    logging.warning('3')
    if user:
        user_id = user[0]['id']
        family = [user for user in us if user['vc_with'] == user_id]
        user = user + family
    logging.warning('4')
    return user


if __name__ == "__main__":
    while True:
        try:
            gs = gsheets.GoogleSheets('germany')
            emails = gs.ws.get_all_values()
            emails = [email for email in emails if email[5] == '1']
            for e in emails:
                errors = []
                for _ in range(5):
                    try:
                        logging.warning(e)
                        soup = gmm.find_regex_in_email_with_title(e[1], e[2], 'Terminvereinbarung', seen_type='UNSEEN')
                        for s in soup:
                            logging.warning(soup)
                            element = s.find("a", href=lambda
                                href: href and "rktermin/extern/confirmation_appointment.do?" in href)
                            options = webdriver.ChromeOptions()
                            settings = {
                                "recentDestinations": [{
                                    "id": "Save as PDF",
                                    "origin": "local",
                                    "account": "",
                                }],
                                "selectedDestinationId": "Save as PDF",
                                "version": 2
                            }
                            prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
                                     'savefile.default_directory': os.path.dirname(os.path.realpath(__file__))}
                            options.add_experimental_option('prefs', prefs)
                            options.add_argument('--kiosk-printing')
                            options.headless = True
                            driver = webdriver.Chrome(options=options)
                            link = element['href'].replace('&amp;', '&').replace('request_locale=de',
                                                                                 'request_locale=ru')
                            driver.get(link)
                            ps = BeautifulSoup(driver.page_source, "lxml")
                            if confirmation := ps.find('fieldset'):
                                try:
                                    confirmation = ' '.join(ps.find('fieldset').text.split())
                                    time = re.findall('время:(.*?)Место', confirmation)[0].strip()
                                    search_stop = 'Grund' if re.findall('Visumbewerbers :(.*?)Grund', confirmation) else 'Telefonnummer'
                                    passport = re.findall(f'Visumbewerbers :(.*?){search_stop}', confirmation)[0].strip()
                                    surname = re.findall('Фамилия:(.*?)Электронная почта:', confirmation)[0].strip().replace('Имя: ', '')
                                    # telegram.send_doc(f'🟩💌 Германия подтвержден email({e[1]}):\n{surname}({time})\n{link}', str(ps), debug=False)
                                    gs.ws.update_acell(f'G{int(e[0]) + 1}', surname)
                                    gs.ws.update_acell(f'H{int(e[0]) + 1}', time)
                                    gs.ws.update_acell(f'I{int(e[0]) + 1}', link)
                                    driver.execute_script(f'document.title = "{surname}"')
                                    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", settings)
                                    with open(f'{surname}.pdf', 'wb') as file:
                                        file.write(base64.b64decode(pdf_data['data']))
                                        us = get_user(e[1])
                                        for u in us:
                                            file = os.path.abspath(f"{surname}.pdf")
                                            body = {'vc_status': '4', 'vc_comment': f'{u["vc_comment"]}|{link}', 'vc_visit_date': time}
                                            users.update_fields(url=f'{sys.argv[2]}', id=u['id'], body=body, file=file)
                                            telegram.send_message(f'📄Германия pdf добавлен в агент для {u["id"]} {u["vc_surname"]} {u["vc_name"]}', debug=False)
                                except Exception as ex:
                                    telegram.send_doc(f'🟩🔴💌 Германия подтвержден email, необходимо добавить в агент руками({e[1]}):\nОшибка: {str(ex)}',str(ps), debug=False)
                            else:
                                telegram.send_doc(f'🔴💌 Германия НЕ подтвержден email({e[1]})', str(ps), debug=False)
                            gs.ws.update_acell(f'F{int(e[0]) + 1}', int(e[5]) - 1)
                        break
                    except Exception as ex:
                        errors.append(str(ex))
                        # telegram.send_message(f'Email error: {str(ex)}')
                        sleep(1)
                else:
                    telegram.send_message(f'🔴💌 Германия ошибка проверки почты({e[1]}): {errors}')
                sleep(1)
        except Exception as ex:
            telegram.send_message(f'Ошибка проверки почты: {str(ex)}')
        sleep(30)
        logging.warning('---')
