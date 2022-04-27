import os
import smtpd
from pdf2image import convert_from_path
import pandas as pd
import requests
import json
import shutil


def convert_pdf(sp,dp,name):
    image = convert_from_path(sp)
    for i in range(len(image)):
        image[i].save(dp+name+'.jpeg','JPEG')

def get_ocr(file,dest,name):
    word_list = []
    bbox_list = []

    le = file['pages'][0]['dimensions'][0]
    bre = file['pages'][0]['dimensions'][1]
    print(le,bre)
    for i in range(len(file['pages'])):
        for j in range(len(file['pages'][i]['blocks'])):
            for k in range(len(file['pages'][i]['blocks'][j]['lines'])):
                for l in range(len(file['pages'][i]['blocks'][j]['lines'][k]['words'])):
                    word_list.append(file['pages'][i]['blocks'][j]['lines'][k]['words'][l]['value'])
                    final_bb = []
                    for t in range(len(file['pages'][i]['blocks'][j]['lines'][k]['words'][l]['geometry'])):
                        final_bb.append(file['pages'][i]['blocks'][j]['lines'][k]['words'][l]['geometry'][t][0]*bre)
                        final_bb.append(file['pages'][i]['blocks'][j]['lines'][k]['words'][l]['geometry'][t][1] * le)
                    bbox_list.append(final_bb)
    df = pd.DataFrame(list(zip(word_list, bbox_list)), columns = ['words', 'bbox'])
    df['tags'] = ''
    df.to_csv(dest+name+'.csv')


def get_json(path):
    files = {'file': open(path, 'rb')}
    response = requests.post("http://localhost:8000/ocr",files = files,headers={'Connection':'close'}).json()
    return response

def get_file_name(source_path):
    file_name = os.listdir(source_path)
    return file_name

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sp = './docs/'
    ip = './images/'
    tp = './tags/'
    pp = './processed_image/'
    files = get_file_name(ip)
    for i in files:
        name = i.split('.')[0]
        print(name)
        if i.lower().__contains__('.pdf'):
            pa = sp+i
            #convert_pdf(pa,ip,name)
        path = ip+name+'.jpeg'
        print('started api')
        file = get_json(path)
        print('completed')
        print('started ocr')
        get_ocr(file,tp,name)
        print('complted')
        shutil.move(path,pp+name+'.jpeg')
        print('file moved')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
