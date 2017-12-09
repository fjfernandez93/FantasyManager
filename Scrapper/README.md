# FantasyManager: Scrapper

A scrapper in python that collects info from the Fantasy website and stores it in a PostgreSQL DB.

At the moment, it has two scripts:

- updateMain.py: It updates the current info (current price and points), and adds new players.
- getDataFromWeek: It collect the info from a specific week. The week is passed as an argument.


IMPORTANT: at the moment, it's a very early version. It needs a lot of improvements, as: handle exceptions, define a setup.py, improve this readme with more info, define main methods, extract the database info from a config file, etc.
