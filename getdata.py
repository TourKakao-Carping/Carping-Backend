import requests
from urllib.parse import urlencode, quote_plus
from django.conf import settings
# 전체 num : 2649

API_KEY = getattr(settings, "CAMP_API_KEY")


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


# 21개
column = ['name', 'lat', 'lon' 'animal', 'website', 'phone', 'address', 'brazier', 'oper_day', 'off_day_start',
          'off_day_end', 'faculty', 'permission_date', 'reservation', 'toilet', 'shower', 'type', 'sub_facility', 'season', 'image', 'area']

# 22개
json_column = ['facltNm', 'mapX', 'mapY', 'animalCmgCl', 'homepage', 'tel', 'addr1',
               'brazierCl', 'operDeCl', 'hvofBgnde', 'hvofEnddle', 'facltDivNm', 'prmisnDe', 'resveCl', 'toiletCo', 'swrmCo', 'induty', 'sbrsCl', 'sbrsEtc', 'operPdCl', 'firstImageUrl', 'doNm']

# data = []

# for i in range(22):
#     data.append(0)

# for i in item:
#     # 0 ~ 21
#     for json_num in range(len(json_column)):
#         if not i.get(json_column[json_num]) == None:
#             data[json_num] += 1

count = 0

for i in item:
    induty = i.get('induty')
    if '자동차야영장' in induty:
        count += 1
print(count)
#위도 : x
#경도 : y
# 이름, 주소, 위도, 경도, 동물출입여부, 화로여부, 웹사이트 주소,