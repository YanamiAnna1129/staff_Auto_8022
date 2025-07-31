import requests
import hashlib
import datetime
import pytz

def md5(string='yk654321'):
    bytes = string.encode('utf-8')
    md5_hash = hashlib.md5()
    md5_hash.update(bytes)
    return md5_hash.hexdigest()
def format_time(timestamp_ms):
    try:
        timestamp_s = timestamp_ms / 1000
        utc_dt = datetime.datetime.fromtimestamp(timestamp_s, tz=pytz.utc)
        cst_tz = pytz.timezone('Asia/Shanghai')
        cst_dt = utc_dt.astimezone(cst_tz)
        formatted_time = cst_dt.strftime("%m月%d日 %H:%M")
        return formatted_time
    except:
        return '-'


def login(phone, password):
    login_url = "http://218.5.5.242:8022/manage-api/user/login"
    password = md5(password)
    params = {
        "phone": phone,
        "password": password
    }
    session = requests.Session()
    r = session.get(login_url, params=params)
    ck = session.cookies.get_dict().get('SHAREJSESSIONID', '')
    cookie = 'SHAREJSESSIONID=' + ck
    print('登入成功', cookie)
    return cookie, r.json()['status']


def get_basic_info(cookie):
    info_list = []
    header ={"Cookie": f"{cookie}"}
    url1 = "http://218.5.5.242:8022/teaching/teaching-api/coursechoose/selectCourse"
    course_id = requests.post(url1, headers=header).json()[0]['id']
    courseName = requests.post(url1, headers=header).json()[0]['courseName']
    url2 = f"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/Page?courseId={course_id}"
    response = requests.post(url2, headers=header)
    # print(response.json())
    endRow = response.json()["data"]['endRow']

    for i in range(endRow):
        num = response.json()["data"]['list'][i]['qulzId']
        stu_id = response.json()["data"]['list'][i]['stuId']
        name = response.json()["data"]['list'][i]['maTUserName']
        qulzname = response.json()["data"]['list'][i]['qulzName']
        score = response.json()["data"]['list'][i]['score']
        createTime = response.json()["data"]['list'][i]['createTime']
        submitTime = response.json()["data"]['list'][i]['submitTime']
        status = response.json()["data"]['list'][i]['status']
        if int(status) == 1:
            status = '未完成'
        else:
            status = '已完成'
        createTime = format_time(createTime)
        submitTime = format_time(submitTime)
        info_dict = {
            'num': num,
           'stu_id': stu_id,
            'name': name,
            'qulzname': qulzname,
           'score': score,
            'createTime': createTime,
           'submitTime': submitTime,
           'status': status
        }
        info_list.append(info_dict)

    return info_list, name


def get_question_id_list(cookie, num):
    question_id_list = []
    oj_id_list = []
    header ={"Cookie": f"{cookie}"}
    question_id_url = rf"http://218.5.5.242:8022/course/course-api/courses/qulz/getStuQulz?id={num}"

    response = requests.post(question_id_url, headers=header).json()

    for i in response['data']['qulzchoose']:
        question_id_list.append(i['questionId'])

    for i in response['data']['qulzoj']:
        oj_id_list.append(i['questionId'])
    
    return question_id_list, oj_id_list



def get_answer(cookie, num):
    choice_answer_list = []
    oj_answer_list = []
    url3 = f"http://218.5.5.242:8022/course/course-api/courses/qulz/getUserId?id={num}"
    header = {
    "Cookie": f"{cookie}",
}
    response3 = requests.post(url3, headers=header)
    answer = response3.json()
    # print('answer:::::::::::',answer)
    try:
        if answer['data']['chooseProblem']:
            c = answer['data']['chooseProblem']
            question_num = len(c)
            print('获取答案中：')
            for i in range(0, question_num):
                choice_answer = answer['data']['chooseProblem'][i]['answer']
                answer_and_id = choice_answer
                choice_answer_list.append(answer_and_id)
            print(choice_answer_list)
    except:
        print('可能没有选择题')
    try:
        if answer['data']['ojProblemList']:
            s = answer['data']['ojProblemList']
            question_num = len(s)
            # print('编程题答案：')
            for i in range(0, question_num):
                oj_answer = answer['data']['ojProblemList'][i]['viewAnswer']
                # print(oj_answer)
                oj_answer_list.append(oj_answer)
                # print()
            print(oj_answer_list)
    except:
        print('可能没有编程题')
    return choice_answer_list, oj_answer_list


def submit_answer(cookie, num, stu_id, choice_answer_list, oj_answer_list, question_id_list, oj_id_list):
    header ={"Cookie": f"{cookie}"}
    submit_choose_answer_url = rf"http://218.5.5.242:8022/course/course-api/qulz_oj/submitProblemAnswer/{num}"
    submit_oj_answer_url = r'http://218.5.5.242:8022/oj/Oj-api/judge/JugerServerId'
    submit_url = r"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/studentUpdate"

    if choice_answer_list:
        for p_id, p_answer in enumerate(choice_answer_list):
            data = {
                "answer": f"{p_answer}",
                "problemValue": "1",
                "problemId": question_id_list[p_id],
            }
            # 选择答案
            response4 = requests.post(submit_choose_answer_url, headers=header, json=data)
            # print(response4.text)
            # 提交答案
            data2 = {
                "stuId": stu_id,
                "qulzId": f"{num}"
            }
            response5 = requests.post(submit_url, headers=header, json=data2)
            # print(response5.text)

    if oj_answer_list:
        for p_id, p_answer in enumerate(oj_answer_list):
            data = {
                "proId": oj_id_list[p_id],
                "examId": f"{num}",
                "type": 1,
                "language": "py3",
                "answer": f"{p_answer}",
            }
            # 上传编程题答案
            response4 = requests.post(submit_oj_answer_url, headers=header, data=data)
            # print(response4.text)
            # 提交答案
            data2 = {
                "stuId": stu_id,
                "qulzId": f"{num}"
            }
            response5 = requests.post(submit_url, headers=header, json=data2)
            # print(response5.text)


