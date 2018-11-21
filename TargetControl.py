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


    def __init__(self, username=None, password=None, server=None):
        self.server = server
        self.username = username
        self.password = password
        self.logged_in = False
        self._prepare_logger()
        self._prepare_browser()
        self.round = 0
        self.player=''

        self.CMD_STOP = False
        self.CMD_FARM = True
        self.CMD_LOGIN = True
        self.CMD_GET_FARMED_RES = False


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
        """
        convert: `sendBuildRequest('url', null, 1)`; into: `url`
        """
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
        self.download_api_files()
        file = open('Planets'+options['target']['name']+'.txt', 'a')
        idx = self.getPlayerId(name)
        self.logger.info('%s %s' % (idx, name))

        galaxy = etree.parse('galaxy.xml').getroot()
        for planet in galaxy.findall('planet[@player=\'' + idx + '\']'):
            pl = Planet(id=planet.get('id'),
                        name=planet.get('name'),
                        coords=planet.get('coords'),
                        url=None)
            self.logger.info('%s %s %s' % (pl.coords, pl.name, pl.id))
            file.write(pl.coords+'  '+pl.name+'  '+pl.id+'\n')
            self.player.addPlanet(pl)
        file.close()
        return self.player.getPlanets()

    def getPlanetsFromFile(self, name):
        self.player = Player(name)
        file = open('Planets'+options['target']['name']+'.txt', 'r')
        for line in file:
            pl = Planet(id=line.split('  ')[2],
                        name=line.split('  ')[1],
                        coords=line.split('  ')[0],
                        url=None)
            self.logger.info('%s %s %s' % (pl.coords, pl.name, pl.id))
            self.player.addPlanet(pl)
        file.close()
        return self.player.getPlanets()

    def getPlayerId(self, name):
        players = etree.parse('players.xml').getroot()
        for player in players.findall('player[@name=\'' + name + '\']'):
            return player.get('id')
        return ""

    def login_lobby(self, username=None, password=None, server=None):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        username = username or self.username
        password = password or self.password
        server = server or self.server
        player_id = options['credentials']['player_id']
        number = server[1:4]
        try:
            driver= webdriver.Chrome('./chromedriver.exe',chrome_options=chrome_options)
            driver.get("https://it.ogame.gameforge.com")

            # Chiudo banner
            try:
                driver.find_element_by_link_text("x").click()
            except:
                self.logger.info('No banner found')

            # Vado sulla Login Form
            driver.find_element_by_link_text("Login").click()

            # Immetto Credenziali
            usernameLogin = driver.find_element_by_id("usernameLogin")
            passwordLogin = driver.find_element_by_id("passwordLogin")

            usernameLogin.send_keys(username)
            passwordLogin.send_keys(password)

            # Clicco su login
            driver.find_element_by_id("loginSubmit").click()
            time.sleep(2)

            # Recupero URL login
            driver.get(
                "https://lobby-api.ogame.gameforge.com/users/me/loginLink?id=" + player_id + "&server[language]=it&server[number]=" + number)
            time.sleep(2)

            # Richiamo il login
            html = driver.page_source
            soup = BeautifulSoup(html)
            url = 'https://' + server + '/game/lobbylogin.php?' + soup.find('pre').text.split('?')[1].replace('"}','').replace('&amp;', '&')
            driver.get(url)
            while True:
                self.check_target(driver)

        except Exception as e:
            self.logger.exception(e)
            self.logged_in = False
            return False

        #Chiudo il browser
        driver.quit()
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

    def check_target(self,driver):
        file = open(options['target']['name']+'.txt', 'a')
        os.remove('Planets'+options['target']['name']+'.txt')
        filePlanet = open('Planets'+options['target']['name']+'.txt', 'a')
        file.write(str(self.server_time)+'\n')
        for planet in self.player.getPlanets():
            driver.get(self.PAGES['galaxy']+'&galaxy='+planet.coords.split(':')[0]+'&system='+planet.coords.split(':')[1])
            self.miniSleep()
            contentWrapepr = driver.find_element_by_id("contentWrapper")
            self.miniSleep()
            row = contentWrapepr.find_elements_by_class_name("row")[int(planet.coords.split(':')[2])-1]
            if (row.find_element_by_class_name("playername").text.split('(')[0].strip()==options['target']['name']):
                moonIsPresent='js_no_action' not in row.find_element_by_class_name('moon').get_attribute('class')
                if (moonIsPresent):
                    moon = row.find_element_by_class_name('moon')
                    file.write(planet.coords + '--' + self.get_activity(row)+'\n')
                    file.write(planet.coords + 'MOON--' + self.get_activity(moon)+'\n')
                else:
                    file.write(planet.coords + '--' + self.get_activity(row)+'\n')
                filePlanet.write(planet.coords + '  ' + planet.name + '  ' + planet.id + '\n')
            else:
                driver.find_element_by_id('bar').find_elements_by_tag_name('li')[4].find_element_by_tag_name('a').click()
                self.miniSleep()
                driver.find_element_by_class_name('tabsbelow').find_elements_by_tag_name('li')[2].find_element_by_tag_name('a').click()
                self.miniSleep()
                driver.find_element_by_id("searchText").send_keys(planet.name)
                driver.find_element_by_id('searchForm').find_elements_by_tag_name('input')[1].click()
                self.miniSleep()
                searchTable = driver.find_element_by_class_name('searchTabs')
               # try:
               #     pagebar = searchTable.find_element_by_class_name("pagebar")
                #    pageMax = pagebar.find_elements_by_class_name('ajaxSearch')[int(len(pagebar.find_elements_by_class_name('ajaxSearch')))-1].get_attribute('ref')
                #    for x in range (1,pageMax):
               #         if (x==int(pagebar.find_elements_by_tag_name('b').text)+1):
                #            for page in pagebar.find_elements_by_class_name('ajaxSearch'):
                #                if(page.text==str(x)):
                 #                   page.click()
               #     results = searchTable.find_elements_by_tag_name('tr')
                #    self.miniSleep()
                #    for result in results:
                #       print(result.find_element_by_class_name('userName').text.strip())
                 #       if(result.find_element_by_class_name('userName').text.strip()==options['target']['name']):
                 #           file.write(planet.coords + '-- PIANETA SPOSTATO (' + planet.name + ' '+result.find_element_by_class_name('position').text+')' + '\n')
                 #           planet.coords=result.find_element_by_class_name('position').text.replace('[','').replace(']','')

                #except NoSuchElementException:
                results = searchTable.find_elements_by_tag_name('tr')
                self.miniSleep()
                for result in results:
                    print(result.find_element_by_class_name('userName').text.strip())
                    if(result.find_element_by_class_name('userName').text.strip()==options['target']['name']):
                        file.write(planet.coords + ' -- PIANETA SPOSTATO (' + planet.name + ' '+result.find_element_by_class_name('position').text+')' + '\n')
                        coords = result.find_element_by_class_name('position').text.replace('[','').replace(']','')
                        if(coords not in self.player.getAllCords()):
                            break
                filePlanet.write(coords+'  '+planet.name+'  '+planet.id+'\l')

        file.write('----------------------------------------------------------\n\n\n')
        file.close()
        filePlanet.close()
        timeSleep = self.getSleep()
        driver.execute_script('var newItem = document.createElement("LI"); \
        newItem.setAttribute("id", "controlTime");\
        newItem.setAttribute("style", "color: red;");\
        var referenceNode=document.getElementById("playerName"); \
        var list = referenceNode.parentNode; \
        list.insertBefore(newItem,referenceNode.nextSibling);')
        driver.execute_script('var value='+str(timeSleep)+';\
        var countDown = new Date(new Date().getTime()+(value*1000)).getTime();\
var x = setInterval(function() {\
    var now = new Date().getTime();\
    var distance = countDown - now;\
    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));\
    var seconds = Math.floor((distance % (1000 * 60)) / 1000);\
    document.getElementById("controlTime").innerHTML = "Prossimo controllo: "+minutes + "m " + seconds + "s ";\
    if (distance < 0) {\
        clearInterval(x);\
        document.getElementById("controlTime").innerHTML = "";\
    }\
}, 1000);')
        self.sleep(timeSleep)


    def get_activity(self,row):
        try:
            activity= row.find_element_by_class_name("activity")
            if 'minute15' in activity.get_attribute('class'):
                return '0'
            else:
                return activity.text.strip()
        except NoSuchElementException:
            return '>60'


    def getSleep(self):
        sleep_options = options['general']
        min = int(sleep_options['seed']) - randint(0, int(sleep_options['check_interval']))
        max = int(sleep_options['seed']) + randint(0, int(sleep_options['check_interval']))
        return randint(min, max)

    def sleep(self,sleep_time):
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
            if (os.path.exists('Planets'+options['target']['name']+'.txt')):
                self.getPlanetsFromFile(options['target']['name'])
            else:
                self.getPlanetsFromApi(options['target']['name'])
            self.login_lobby()
        except Exception as e:
            self.logger.exception(e)

        self.stop()

if __name__ == "__main__":
    credentials = options['credentials']
    bot = Bot(credentials['username'], credentials['password'], credentials['server'])
    bot.start()

