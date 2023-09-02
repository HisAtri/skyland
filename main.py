import random
import requests
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('')

cred_list = []
vName = '1.0.1'
vCode = '100001014'
UA = f"Skland/{vName} (com.hypergryph.skland; build:{vCode}; Android 29; ) Okhttp/4.11.0"
with open("cred_list.txt", 'r+') as file:
    for line in file:
        line = line.strip()
        cred_list.append(line)


def signin(cred):
    headers = {
        'cred': cred,
        'User-Agent': UA,
        'Accept-Encoding': 'gzip',
        'vName': vName,
        'vCode': vCode
    }
    url = "https://zonai.skland.com"
    sign_api = "/api/v1/game/attendance"
    bind_api = "/api/v1/game/player/binding"

    def get_list():
        user_list = []
        response_list = requests.get(url=url + bind_api, headers=headers).json()
        if response_list.get('message') == '用户未登录':
            logging.info('登录失败' + cred)
            return False
        for user in response_list['data']['list']:
            if user.get('appCode') == 'arknights':
                user_list.extend(user.get('bindingList'))
        return user_list

    characters = get_list()
    if characters:
        for character in characters:
            uid = character.get('uid')
            gameID = character.get("channelMasterId")
            character_json = {
                'uid': uid,
                'gameId': gameID
            }
            response = requests.post(url=url + sign_api, headers=headers, json=character_json).json()
            if response['code'] == 0:
                logging.info(f"签到成功,UID:{uid};GameID:{gameID}")
            else:
                logging.info("签到失败" + str(response['code']))


def get_next_timestamp(timeh, next_day=False):
    # 获取当前时间
    now = datetime.datetime.now()
    tz = datetime.timezone(datetime.timedelta(hours=8))
    # 将当前时间转换为UTC+8时区
    now = now.astimezone(tz)
    current_hour = now.hour
    # 判断当前小时数是否大于等于传入的小时数a
    if current_hour >= timeh or next_day:
        now += datetime.timedelta(days=1)
    # 设置下一个目标时间的小时数和分钟数
    target_time = now.replace(hour=timeh, minute=0, second=0, microsecond=0)
    target_time = target_time.astimezone(datetime.timezone.utc)
    # 返回目标时间戳
    return int(target_time.timestamp())


def timing_task(start, end, next_day=False):
    end_timestamp = get_next_timestamp(end)
    start_timestamp = end_timestamp - (end - start) * 3600
    time_range_start = random.randint(start_timestamp, end_timestamp - 10, next_day)
    return time_range_start


def start_task(start, end):
    next_start = timing_task(start, end)

    while True:
        now_time = datetime.datetime.now().timestamp()
        if next_start < now_time < next_start + 10:
            for single_cred in cred_list:
                signin(single_cred)
            next_start = timing_task(start, end, True)


start_task(9, 10)
