import secrets
import requests
from urllib.parse import urlencode, quote_plus
from django.conf import settings
# 전체 num : 2649


# API_KEY = getattr("secrets.json", "CAMP_API_KEY")
API_KEY = "iN2MyW0y826slyTaUpwpzEHzUJDo%2B3Ax9mGKTUu%2FNozBfu1w8FgP7yDxvz6ubbKpkiVt0d1d8YNLNaUhBapFeA%3D%3D"


def get_data():
    url = "http://api.visitkorea.or.kr/openapi/service/rest/GoCamping/basedList"
    queryParams = '?' + urlencode({quote_plus(
        'numOfRows'): '2649',
        quote_plus('MobileOS'): 'AND',
        quote_plus('MobileApp'): 'Carping',
        quote_plus('_type'): 'json',
        quote_plus('ServiceKey'): ""}) + API_KEY

    req = requests.get(url + queryParams)
    req_json = req.json()
    response = req_json['response']
    body = response['body']
    items = body['items']
    item = items['item']
    return item


# CampSite
    # for item in item:
item = get_data()


# 26개
column = ['name', 'lat', 'lon' 'animal', 'event', 'program', 'website', 'phone', 'address', 'brazier', 'oper_day', 'off_day_start',
          'off_day_end', 'faculty', 'permission_date', 'reservation', 'toilet', 'shower', 'type', 'sub_facility', 'season', 'image', 'area', 'themenv', 'created_at', 'updated_at']

# 27개
json_column = ['facltNm', 'mapX', 'mapY', 'animalCmgCl', 'clturEvent', 'exprnProgrm', 'homepage', 'tel', 'addr1',
               'brazierCl', 'operDeCl', 'hvofBgnde', 'hvofEnddle', 'facltDivNm', 'prmisnDe', 'resveCl', 'toiletCo', 'swrmCo', 'induty', 'sbrsCl', 'sbrsEtc', 'operPdCl', 'firstImageUrl', 'doNm', 'themaEnvrnCl', 'createdtime', 'modifiedtime']

# data = []

# for i in range(22):
#     data.append(0)

# for i in item:
#     # 0 ~ 21
#     for json_num in range(len(json_column)):
#         if not i.get(json_column[json_num]) == None:
#             data[json_num] += 1

count = 0

item_arr = []
for i in item:
    key = i.get('themaEnvrnCl')
    if key is not None:
        i_arr = key.split(',')
        for j in i_arr:
            if not j in item_arr:
                item_arr.append(j)
        count += 1
    # if induty == "공동취사장":

    # count += 1xz
    # print(induty)
print(item_arr)
print(count)
#위도 : x
#경도 : y
# 이름, 주소, 위도, 경도, asㅁㄴxaxAxA, 화로여부, 웹사이트 주소,
