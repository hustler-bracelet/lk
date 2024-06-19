import os

from aiogram import Bot

TG_BOT_TOKEN = os.getenv('TOKEN')
BRACELET_CHANNEL_ID = os.getenv('CHANNEL_ID')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

# TG_BOT_TOKEN = "6781360051:AAHsuiSJBM9EnAMcxJyJR9TeoMIgxAAfSPQ" (PROD)
# TG_BOT_TOKEN = "7254821810:AAEg1ZUp1beOXpJcs2-9rR105PCG7ULfWzI"
# BRACELET_CHANNEL_ID = -1001969838018 (PROD)
# BRACELET_CHANNEL_ID = -1002233580105
# DB_HOST = "127.0.0.1"
# DB_PORT = 5432
# DB_USER = "postgres"
# DB_PASS = "a1TPceenqWe"
# DB_NAME = "postgres"
# ADMINS = [6567176437, 1702948486, 404161836]

BOT: Bot | None = None

VERSION = '1.1.1-lk'
UPDATE_TIME = '19 июня 2024'
