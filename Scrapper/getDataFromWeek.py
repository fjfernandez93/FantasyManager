from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep
from bs4 import BeautifulSoup
import re
import collections
import os.path
import psycopg2
import sys

def parseAndStore(html,week):
    conn = psycopg2.connect("dbname=nba user=postgres password=postgres")
    cur = conn.cursor()

    soup = BeautifulSoup(html, "html.parser")
    tag_l = soup.find_all("tr", {"id": re.compile("playerResults")})
    for tag in tag_l:
        # Extract data from row
        name = tag.find("a", {"href": re.compile("/basketball/reports/profile.asp")}).text
        priceRaw = tag.find("td",{"class":re.compile("currency")}).text
        price = float(re.search("^€([0-9.]+)",priceRaw).group(1))
        children = tag.findChildren()
        points = float(children[len(children)-1].text)
        ratio = points/price
        # Find de id of the player
        cur.execute("SELECT * FROM player WHERE name = %s;",(name,))
        result = cur.fetchall()
        id_player = result[0][0]
        # Insert the new info
        cur.execute("INSERT INTO history_week (id_player,week, price, points, ratio) VALUES (%s,%s,%s,%s,%s);" \
                    ,(id_player,week,price,points,ratio))

    conn.commit()
    cur.close()
    conn.close()

def extractByPositionAndWeek(pos,week):
    #Create both Select objects (position and week)
    selectPos = Select(driver.find_element_by_id("pos"))
    selectWeek = Select(driver.find_element_by_id("wk"))
    # Select the corresponding values
    selectPos.select_by_index(pos)
    selectWeek.select_by_index(week)
    # Find a click SAVE button to make the changes
    saveButton = driver.find_element_by_xpath("//input[@value='GUARDAR']")
    saveButton.click()
    sleep(3)
    # Extract first page
    html = driver.page_source
    parseAndStore(html,week)

    # Extract the rest
    # if(pos == 0 or pos == 1):
    #     numpags = 7
    # else:
    #     numpags = 2
    # for i in range(0,numpags):
    endList = False
    while not endList:
        nextButton = driver.find_element_by_id("searchResults_next")
        classAtt = nextButton.get_attribute("class")
        if( re.search("disable",classAtt) == None):
            nextButton.click()
            sleep(2)
            html = driver.page_source
            parseAndStore(html,week)
        else:
            break


######### MAIN ##########
if(len(sys.argv)!=2):
    print("Wrong number of arguments")
    sys.exit()
week = int(sys.argv[1])
driver = webdriver.Firefox()
driver.get("http://fantasynba.movistarplus.es/")

### LOGIN
usernameBox = driver.find_element_by_id("txtLogin")
passwordBox = driver.find_element_by_id("txtPassword")
usernameBox.send_keys(os.environ["FANTASY_USER"])
passwordBox.send_keys(os.environ["FANTASY_PASS"])
okButton = driver.find_element_by_xpath("//input[@value='JUGAR']")
okButton.click()

### GET INTO STATS TAB
teamLink = driver.find_element_by_link_text("Fidesol Thunders")
teamLink.click()
statsLink = driver.find_element_by_link_text("Estadísticas")
statsLink.click()
sleep(3)

###

extractByPositionAndWeek(0,week)
extractByPositionAndWeek(1,week)
extractByPositionAndWeek(2,week)
