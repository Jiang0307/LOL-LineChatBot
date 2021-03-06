import os
import sys
import message_template
import requests
import re
from lxml import etree
from PIL import Image
from pyquery import PyQuery
from flask import Flask, jsonify, request, abort, send_file
import urllib3
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from transitions.extensions import GraphMachine
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

dict_tw_en = {"亞歷斯塔": "Alistar", "亞菲利歐": "Aphelios", "伊澤瑞爾": "Ezreal", "伊瑞莉雅": "Irelia", "伊羅旖": "Illaoi", "伊芙琳": "Evelynn", "伊莉絲": "Elise", "克雷德": "Kled", "克黎思妲": "Kalista", "凱爾": "Kayle", "凱特琳": "Caitlyn", "凱能": "Kennen", "凱莎": "Kaisa", "剎雅": "Xayah", "剛普朗克": "Gangplank", "加里歐": "Galio", "努努和威朗普": "Nunu", "劫": "Zed", "勒布朗": "Leblanc", "卡力斯": "Khazix", "卡爾瑟斯": "Karthus", "卡特蓮娜": "Katarina", "卡瑪": "Karma", "卡莎碧雅": "Cassiopeia", "卡薩丁": "Kassadin", "卡蜜兒": "Camille", "厄薩斯": "Aatrox", "古拉 格斯": "Gragas", "史加納": "Skarner", "史瓦妮": "Sejuani", "吉茵珂絲": "Jinx", "吶兒": "Gnar", "嘉文四世": "Jarvaniv", "圖奇": "Twitch", "埃可尚": "Akshan", "埃爾文": "Ivern", "塔莉雅": "Taliyah", "塔里克": "Taric", "塔隆": "Talon", "墨菲特": "Malphite", "夜曲": "Nocturne", "奈德麗": "Nidalee", "奧莉安娜": "Orianna", "好運姐": "MissFortune", "妮可": "Neeko", "姍娜": "Senna", "姬亞娜": "Qiyana", "威寇茲": "Velkoz", "娜米": "Nami", "安妮": "Annie", "寇格魔": "KogMaw", "崔絲塔娜": "Tristana", "巴德": "Bard", "布蘭德": "Brand", "布郎姆": "Braum", "布里茨": "Blitzcrank", "希格斯": "Ziggs", "希瓦娜": "Shyvana", "希維爾": "Sivir", "庫奇": "Corki", "弗力貝爾": "Volibear", "弗拉迪米爾": "Vladimir", "悟空": "Monkeyking", "悠咪": "Yuumi", "慎": "Shen", "慨影": "Kayn", "拉克絲": "Lux", "拉姆斯": "Rammus", "提摩": "Teemo", "斯溫": "Swain", "易大師": "MasterYi", "星朵拉": "Syndra", "札克": "Zac", "李星": "LeeSin", "杰西": "Jayce", "枷蘿": "Zyra", "柔依": "Zoe", "極靈": "Zilean", "歐拉夫": "Olaf", "汎": "Vayne", "沃維克": "Warwick", "法洛士": "Varus", "波比": "Poppy", "泰達米爾": "Tryndamere", "派克": "Pyke", "漢默丁格": "Heimerdinger", "潘森": "Pantheon", "烏爾加特": "Urgot", "烏迪爾": "Udyr", "煞蜜拉": "Samira", "燼": "Jhin", "特朗德": "Trundle", "犽凝": "Yone", "犽宿": "Yasuo", "珍娜": "Janna", "瑟菈紛": "Seraphine", "瑟雷西": "Thresh", "科加斯": "Chogath", "約瑞科": "Yorick", "納帝魯斯": "Nautilus", "納瑟斯": "Nasus", "索娜": "Sona", "索拉卡": "Soraka", "維克特": "Viktor", "維爾戈": "Viego", "維迦": "Veigar", "翱銳龍獸": "AurelionSol", "艾克": "Ekko", "艾妮維亞": "Anivia", "艾希": "Ashe", "茂凱": "Maokai", "莉莉亞": "Lillia", "菲歐拉": "Fiora", "菲艾": "Vi", "葛雷夫": "Graves", "葵恩": "Quinn", "蒙多醫生": "DrMundo", "蓋倫": "Garen", "薇可絲": "Vex", "薩科": "Shaco", "藍寶": "Rumble", "貪啃奇": "TahmKench", "費德提克": "Fiddlesticks", "賈克斯": "Jax", "賽勒斯 ": "Sylas", "賽恩": "Sion", "賽特": "Sett", "赫克林": "Hecarim", "趙信": "XinZhao", "路西恩": "Lucian", "辛吉德": "Singed", "逆命": "TwistedFate", "達瑞文": "Draven", "達瑞斯": "Darius", "鄂爾": "Ornn", "銳兒": "Rell", "銳空": "Rakan", "鏡爪": "Kindred", "關": "Gwen", "阿卡莉": "Akali", "阿姆姆": "Amumu", "阿璃": "Ahri", "阿祈爾": "Azir", "雷尼克頓": "Renekton", "雷歐娜": "Leona", "雷玟": "Riven", "雷珂煞": "RekSai", "雷茲": "Ryze", "雷葛爾": "Rengar", "露璐": "Lulu", "飛斯": "Fizz", "馬爾札哈": "Malzahar", "魔甘娜": "Morgana", "魔鬥凱薩": "Mordekaiser", "麗 珊卓": "Lissandra", "黛安娜": "Diana", "齊勒斯": "Xerath"}
dict_cn_en = {}
dict_tw_cn = {}
dict_en_tw = {}
dict_cn_tw = {}

def create_dictionary():
    header = {"User-Agent":"Chrome/96.0.4664.110" , "Accept-Language":"zh-TW,zh;q=0.9"} # configurations
    opgg_url = "https://tw.op.gg/champion/statistics"
    X_PATH =  '//div[@class="champion-index__champion-list"]//div[@data-champion-name and @data-champion-key]'
    webpage = requests.get(opgg_url, headers=header)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))
    champ_list = dom.xpath(X_PATH)
    champ_count =  len(champ_list)
    for i in range(champ_count):
        chinese = champ_list[i].get("data-champion-name")
        english = champ_list[i].get("data-champion-key")
        english = english.capitalize()
        dict_cn_en[chinese] = english
        #dict_en_ch[english] = chinese
    dict_cn_en["铸星龙王"]="AurelionSol";dict_cn_en["祖安狂人"]="DrMundo";dict_cn_en["深渊巨口"]="KogMaw";dict_cn_en["盲僧"]="LeeSin";dict_cn_en["无极剑圣"]="MasterYi";dict_cn_en["赏金猎人"]="MissFortune";dict_cn_en["虚空遁地兽"]="RekSai";dict_cn_en["河流之王"]="TahmKench";dict_cn_en["卡牌大师"]="TwistedFate";dict_cn_en["德邦总管"]="XinZhao";

    for tw_key , tw_value in dict_tw_en.items():
        for cn_key , cn_value in dict_cn_en.items():
            if(cn_value == tw_value):
                dict_tw_cn[tw_key] = cn_key

    for key , value in dict_tw_en.items():
        value = value.lower()
        value = value.replace(' ','')
        dict_en_tw[value] = key

    for key , value in dict_tw_cn.items():
        dict_cn_tw[value] = key

    print(len(dict_tw_cn))
    print(len(dict_cn_en))
    print(len(dict_cn_tw))
    print(len(dict_tw_en))
    print(len(dict_en_tw))
    print(dict_tw_cn)
    print(dict_cn_en)    
    return