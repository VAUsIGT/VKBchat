#
# ФАЙЛ С БИБЛИОТЕКАМИ
#



import shutil
import requests
from vkbottle.bot import Bot, Message
from vkbottle.dispatch.rules import ABCRule
from vkbottle import PhotoMessageUploader, VoiceMessageUploader
from keyb import KEYBOARD_SEARCH,KEYBOARD_FIRST, KEYBOARD_DIALOG
from config import token
from loguru import logger
from colorama import init
from random import getrandbits
from colorama import Fore, Back, Style
import datetime
import urllib.request