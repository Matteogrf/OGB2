# -*- coding: utf-8 -*-
import socket
from BeautifulSoup import BeautifulSoup
from logging.handlers import RotatingFileHandler
import time
import logging
import mechanize
import os
import re
from random import randint
from datetime import datetime
from config import options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
from player import Player
from planet import Planet
from selenium.common.exceptions import NoSuchElementException
socket.setdefaulttimeout(float(options['general']['timeout']))

class Bot(object):
    HEADERS = [('User-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36')]
    RE_BUILD_REQUEST = re.compile(r"sendBuildRequest\(\'(.*)\', null, 1\)")
    RE_SERVER_TIME = re.compile(r"var serverTime=new Date\((.*)\);var localTime")

    def __init__(self):

        self.server = options['credentials']['server']
        self.username = options['credentials']['username']
        self.password = options['credentials']['password']

        self.logged_in = False
        self._prepare_logger()
        self._prepare_browser()
        self.round = 0
        self.player=''

        self.CMD_STOP = False
        self.CMD_FARM = True
        self.CMD_LOGIN = True
        self.CMD_GET_FARMED_RES = False

        self.logger.info(self.server)
        self.logger.info(self.username)
        self.logger.info(self.password)

        self.SERVER_URL = 'https://' + self.server
        self.PAGES = {
            'loging':self.SERVER_URL +'/game/index.php',
            'apiPlayers':self.SERVER_URL+ '/api/players.xml',
            'apiGalaxy':self.SERVER_URL+ '/api/universe.xml',
            'main': self.SERVER_URL + '/game/index.php?page=overview',
            'galaxy': self.SERVER_URL + '/game/index.php?page=galaxy',
        }

        self.server_time = self.local_time = datetime.now()
        self.time_diff = 0
        self.emergency_sms_sent = False

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome('./chromedriver.exe',chrome_options=chrome_options)

    def _get_url(self, page, planet=None):
        url = self.PAGES[page]
        if planet is not None:
            url += '&cp=%s' % planet.id
        return url

    def _prepare_logger(self):
        self.logger = logging.getLogger("mechanize")
        fh = RotatingFileHandler('Target.log', maxBytes=100000, backupCount=5)
        sh = logging.StreamHandler()
        fmt = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def _prepare_browser(self):
        # Instantiate a Browser and set the cookies
        self.br = mechanize.Browser()
        self.br.set_handle_equiv(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = self.HEADERS

    def _parse_build_url(self, js):

        return self.RE_BUILD_REQUEST.findall(js)[0]

    def _parse_server_time(self, content):
        return self.RE_SERVER_TIME.findall(content)[0]

    def download_api_files(self):
        # Scarico file Players
        resp = self.br.open(self.PAGES['apiPlayers'], timeout=10)
        file("players.xml", 'w').write(resp.get_data().decode())

        # Scarico galassia
        resp = self.br.open(self.PAGES['apiGalaxy'], timeout=10)
        file("galaxy.xml", 'w').write(resp.get_data().decode())


    def getPlanetsFromApi(self, name):
        self.player = Player(name)
        filePlanets = open('Planets'+name+'.txt', 'a')
        idx = self.getPlayerId(name)
        self.logger.info('%s %s' % (idx, name))
        galaxy = etree.parse('galaxy.xml').getroot()
        for planet in galaxy.findall('planet[@player=\'' + idx + '\']'):
            pl = Planet(id=planet.get('id'),
                        name=planet.get('name'),
                        coords=planet.get('coords'),
                        url=None)
            self.logger.info('%s %s %s' % (pl.coords, pl.name, pl.id))
            filePlanets.write(pl.coords+'  '+pl.name+'  '+pl.id+'\n')
            self.player.addPlanet(pl)

        filePlanets.close()
        return self.player.getPlanets()

    def getPlanetsFromFile(self, name):
        self.player = Player(name)
        file = open('Planets'+name+'.txt', 'r')
        for line in file:
            line = line.rstrip('\n')
            pl = Planet(id=line.split('  ')[2],
                        name=line.split('  ')[1],
                        coords=line.split('  ')[0],
                        url=None)
            self.player.addPlanet(pl)
        file.close()
        return self.player.getPlanets()

    def getPlayerId(self, name):
        players = etree.parse('players.xml').getroot()
        for player in players.findall('player[@name=\'' + name + '\']'):
            return player.get('id')
        return ""

    def login_lobby(self, username=None, password=None, server=None):

        username = username or self.username
        password = password or self.password
        server = server or self.server
        player_name = options['credentials']['player']
        player_id = self.getPlayerId(player_name)

        self.logger.info(player_name)
        self.logger.info(player_id)

        number = server[1:4]
        try:
            self.driver.get("https://it.ogame.gameforge.com")

            # Chiudo banner
            try:
                self.driver.find_element_by_link_text("x").click()
            except:
                self.logger.info('No banner found')

            # Vado sulla Login Form
            self.driver.find_element_by_link_text("Login").click()

            # Immetto Credenziali
            usernameLogin = self.driver.find_element_by_id("usernameLogin")
            passwordLogin = self.driver.find_element_by_id("passwordLogin")

            usernameLogin.send_keys(username)
            passwordLogin.send_keys(password)

            # Clicco su login
            self.driver.find_element_by_id("loginSubmit").click()
            time.sleep(2)

            # Recupero URL login
            self.driver.get("https://lobby-api.ogame.gameforge.com/users/me/loginLink?id=" + player_id + "&server[language]=it&server[number]=" + number)
            time.sleep(2)

            # Richiamo il login
            html = self.driver.page_source
            soup = BeautifulSoup(html)
            url = 'https://' + server + '/game/lobbylogin.php?' + soup.find('pre').text.split('?')[1].replace('"}','').replace('&amp;', '&')
            self.driver.get(url)

        except Exception as e:
            self.logger.exception(e)
            self.logged_in = False
            return False

        self.logged_in = True
        return True

    def calc_time(self, resp):
        try:
            y, mo, d, h, mi, sec = map(int, self._parse_server_time(resp).split(','))
        except:
            self.logger.error('Exception while calculating time')
        else:
            self.local_time = n = datetime.now()
            self.server_time = datetime(n.year, n.month, n.day, h, mi, sec)
            self.time_diff = self.server_time - self.local_time

            self.logger.info('Server time: %s, local time: %s' %(self.server_time, self.local_time))

    def check_target(self, driver, target):

        for planet in self.player.getPlanets():
            driver.get(self.PAGES['galaxy']+'&galaxy='+planet.coords.split(':')[0]+'&system='+planet.coords.split(':')[1])
            self.miniSleep()
            self.miniSleep()
            contentWrapepr = driver.find_element_by_id("contentWrapper")
            self.miniSleep()
            try:
                row = contentWrapepr.find_elements_by_class_name("row")[int(planet.coords.split(':')[2])-1]
                if row.find_element_by_class_name("playername").text.split('(')[0].strip() == target:
                    moonIsPresent='js_no_action' not in row.find_element_by_class_name('moon').get_attribute('class')
                    if moonIsPresent:
                        moon = row.find_element_by_class_name('moon')
                        self.player.logAttivita(planet.coords, True, self.get_activity(moon))
                        self.player.logAttivita(planet.coords, False, self.get_activity(row))
                    else:
                        self.player.logAttivita(planet.coords, False, self.get_activity(row))
                #else:
                    #driver.find_element_by_id('bar').find_elements_by_tag_name('li')[4].find_element_by_tag_name('a').click()
                    #self.miniSleep()
                    #driver.find_element_by_class_name('tabsbelow').find_elements_by_tag_name('li')[2].find_element_by_tag_name('a').click()
                    #self.miniSleep()
                    #driver.find_element_by_id("searchText").send_keys(planet.name)
                    #driver.find_element_by_id('searchForm').find_elements_by_tag_name('input')[1].click()
                    #self.miniSleep()
                    #searchTable = driver.find_element_by_class_name('searchTabs')

                    #results = searchTable.find_elements_by_tag_name('tr')
                    #self.miniSleep()
                    #for result in results:
                    #    if(result.find_element_by_class_name('userName').text.strip()==target):
                    #        file.write(planet.coords + ' -- PIANETA SPOSTATO (' + planet.name + ' '+result.find_element_by_class_name('position').text+')' + '\r\n')
                    #        coords = result.find_element_by_class_name('position').text.replace('[','').replace(']','')
                    #        if(coords not in self.player.getAllCords()):
                    #            #filePlanet.write(coords + '  ' + planet.name + '  ' + planet.id+'\n')
                    #            break

            except Exception as y:
                self.logger.exception(y)
                self.logger.error("Errore caricamento pagina galassia.")


    def get_activity(self,row):
        try:
            activity = row.find_element_by_class_name("activity")
            if 'minute15' in activity.get_attribute('class'):
                return '0'
            else:
                return activity.text.strip()
        except NoSuchElementException:
            return '>60'

    def sleep(self):
        sleep_options = options['general']
        min = int(sleep_options['seed']) - randint(0, int(sleep_options['check_interval']))
        max = int(sleep_options['seed']) + randint(0, int(sleep_options['check_interval']))
        sleep_time = randint(min, max)
        self.logger.info('Sleeping for %s secs' % sleep_time)
        time.sleep(sleep_time)

    def miniSleep(self):
        mini_sleep_time = randint(400, 2500) / 1000
        time.sleep(mini_sleep_time)

    def stop(self):
        self.logger.info('Stopping bot')
        os.unlink(self.pidfile)

    def start(self):
        self.logger.info('Starting bot')
        self.pid = str(os.getpid())
        self.pidfile = 'bot.pid'
        file(self.pidfile, 'w').write(self.pid)
        try:
            self.download_api_files()
            self.login_lobby()

            while True:
                for target in options['targets']['name'].split('&&'):
                    if os.path.exists('Planets' + target + '.txt'):
                        self.getPlanetsFromFile(target)
                    else:
                        self.getPlanetsFromApi(target)

                    self.check_target(self.driver, target)
                self.sleep()
        except Exception as e:
            self.logger.exception(e)

        # Chiudo il browser
        self.driver.quit()
        self.stop()

#if __name__ == "__main__":
   # credentials = options['credentials']
  #  bot = Bot(credentials['username'], credentials['password'], credentials['server'])
    #bot.start()

