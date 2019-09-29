import requests
from lxml import html
import os
import threading
from urllib.request import urlopen, Request, urlretrieve
import urllib.request
import zipfile
import json
import math


try:
    f = open('save_dir.txt','r')
    beat_saber_dir = f.read()
    f.close()
except FileNotFoundError:
    while True:
        print('Missing Beat Saber directory. Please enter your Beat Saber directory.')
        print('example: C:\Program Files (x86)\Steam\steamapps\common\Beat Saber\\')
        new_dir = input()
        if new_dir[-1] != '/':
            new_dir += '/'
        if os.path.isdir(new_dir):
            break
        else:
            print('ERROR: Missing Directory')
    f = open('save_dir.txt','w+')
    f.write(new_dir)
    f.close()
    beat_saber_dir = new_dir

l = os.listdir(beat_saber_dir + 'Beat Saber_Data/CustomLevels/')
beat_saber_song_database = []
for folder_name in l:
    beat_saber_song_database.append(folder_name.split(' ')[0])

print('Player scoresaber link:')
url = input()
while url == '':
    print('Please enter a scoresaber link:')
    url = input()
url = url.replace('https://scoresaber.com/u/','')

print('')
print('Specify sort order:')
print('1. Top played songs')
print('2. Recently played songs')
sort = input()
while sort not in ['1','2']:
    print('Please enter a valid number:')
    sort = input()

print('')
print('Number of songs to download:')

songs = None
while songs == None:
    songs = input()
    try:
        songs = int(songs)
    except:
        songs = None
        print('Please enter a number:')

pages = 1
activeThreads = 0
distribute_count = 0

if songs > 8:
    pages = math.ceil(songs/8)

def clean_text(text):
    valid_chars = [' ','-','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']
    new_text = ''
    for char in text:
        if char.lower() in valid_chars:
            new_text += char
    return new_text

def cleanUrl(text):
    valid_chars = ['1','2','3','4','5','6','7','8','9','0']
    new_text = ''
    for char in text:
        if char.lower() in valid_chars:
            new_text += char
    return new_text

def get_url(url):
    header_dat = {
        'User-Agent':'Mozilla/5.0'
        }
    req = Request(url,headers=header_dat)
    response = urlopen(req)
    json_obj = json_convert(response)
    return json_obj

def json_convert(response):
    string = response.read().decode('utf-8')
    json_obj = json.loads(string)
    return json_obj

# threads = []
# activeThreads = 0
# distribute_count = 0

def download_song(songID):
    global activeThreads    
    try:
        beat_saver_dat = get_url('https://beatsaver.com/api/maps/by-hash/' + songID)
        song_version_nums = beat_saver_dat['key']
        song_name_info = beat_saver_dat['metadata']['songName'] + ' - ' + beat_saver_dat['metadata']['songAuthorName']
        if song_version_nums not in beat_saber_song_database:
            download_url = 'https://beatsaver.com' + beat_saver_dat['downloadURL']
            r = requests.get(download_url)
            with open(songID + '.zip', 'wb') as outfile:
                outfile.write(r.content)
            with zipfile.ZipFile(songID + '.zip','r') as zip_ref:
                zip_ref.extractall(beat_saber_dir + 'Beat Saber_Data/CustomLevels/' + song_version_nums + ' (' + clean_text(song_name_info) + ')/')
            if os.path.exists(songID + '.zip'):
                os.remove(songID + '.zip')
            print('(' + clean_text(song_name_info) + ') - Downloaded!')
            
        else:
            print('(' + clean_text(song_name_info) + ') - Already downloaded')
        
    except Exception as e:
        print('The following error occurred while downloading a song:')
        print(e)
    activeThreads -= 1


def getSongs(playerURL, songNum, pageNum,sortNum):
    global activeThreads, distribute_count
    while (activeThreads != 0) or (distribute_count < songNum):
        i = 0
        for x in range(1,pageNum+1):
            url = "https://scoresaber.com/u/{}".format(playerURL).split("&", 1)[0]+"&page={}&sort={}".format(x,sortNum)
            page = requests.get(url)
            tree = html.fromstring(page.content)
            rows = tree.xpath('//div/table/tbody/tr/th/div/div/img')
            for row in rows:
                if distribute_count < songNum:
                    print('Starting download '+str(distribute_count+1)+'/'+str(songNum))
                    songID = row.xpath('@src')[0].replace('/imports/images/songs/','').replace('.png','')
                    # print(songID)
                    
                    threading.Thread(target = download_song, args = [songID]).start()
                    distribute_count += 1
                    activeThreads += 1
                    i+=1
    print('Finished')
    print('Press any key to close...')
    input()
    

if __name__ == "__main__":    
    getSongs(url, songs, pages, sort)
    
