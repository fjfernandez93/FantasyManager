from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep
from bs4 import BeautifulSoup
import re
import collections
import os.path
import csv
import psycopg2


def storeMainInfo(table, position):
    conn = psycopg2.connect("dbname=nba user=postgres password=postgres")
    cur = conn.cursor()
    for player in table:

        cur.execute("SELECT id from player where name=%s;",(player[0],))
        a = cur.fetchall()
        if(len(a)!=0):
            id_player = a[0][0]
            cur.execute("UPDATE player SET total_points=%s, current_price=%s, current_ratio=%s WHERE id=%s" \
                    ,(player[1],player[2],player[3],id_player))
        else:
            cur.execute("INSERT INTO player (name, position, total_points, current_price, current_ratio) VALUES (%s,%s,%s,%s,%s)" \
                    ,(player[0],position,player[1],player[2],player[3]))
    conn.commit()
    cur.close()
    conn.close()

def parseHtml(listaHtmlfiles):

    table = []
    for html in listaHtmlfiles:
        soup = BeautifulSoup(html, "html.parser")
        tag_l = soup.find_all("tr",{"id":re.compile("PlayerRec")})

        for tag in tag_l:
            name = tag.find("a", {"id":re.compile("btnPlayerName")}).text
            pts = float(tag.find("span",{"id":re.compile("SeasonSTAT6")}).text)
            cost = float(re.search( "^€([0-9.]+)m",tag.find("span",{"id":re.compile("lblValue")}).text).group(1))
            total = pts / cost

            player = (name,pts,cost,total)
            table.append(player)


    sorted_list = sorted(table, key=lambda tup: tup[3], reverse=True)
    return sorted_list

def extractByPosition(pos,pags):
    table = []
    htmllist = []
    select = Select(driver.find_element_by_id('ddlPosition'))
    select.select_by_index(pos)
    sleep(3)
    htmllist.append(driver.page_source)
    endList = False
    #for i in range(2,pags):
    while not endList:
        pageButton = driver.find_element_by_link_text("Siguiente")
        if pageButton.is_displayed() and pageButton.is_enabled():
            pageButton.click()
            sleep(4)
            htmllist.append(driver.page_source)
        else:
            break
    table = parseHtml(htmllist)
    if(pos==0):
        position = "B"
    elif(pos==1):
        position = "A"
    else:
        position = "P"
    storeMainInfo(table, position)

driver = webdriver.Firefox()
driver.get("http://fantasynba.movistarplus.es/")


usernameBox = driver.find_element_by_id("txtLogin")
passwordBox = driver.find_element_by_id("txtPassword")

user = os.environ["FANTASY_USER"]
password = os.environ["FANTASY_PASS"]

usernameBox.send_keys(user)
passwordBox.send_keys(password)

okButton = driver.find_element_by_xpath("//input[@value='JUGAR']")

okButton.click()

teamLink = driver.find_element_by_link_text("Fidesol Thunders")
teamLink.click()

selectButton = driver.find_element_by_link_text("Selecciona tus jugadores")
selectButton.click()

sleep(3)

extractByPosition(0,6)
extractByPosition(1,6)
extractByPosition(2,3)
