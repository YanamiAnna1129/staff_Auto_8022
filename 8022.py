import requests
import ast
choice_answer_list = []
oj_answer_list = []
questionId_list = []
oj_id_list = []

# 获取cookie
session = requests.Session()
login_url = "http://218.5.5.242:8022/manage-api/user/login"
params = {
    "phone": "g2321435",
    "password": "e856280b57c90c8f5bd5289821aa25a6"
}
session.get(login_url, params=params)
SHAREJSESSIONID = session.cookies.get_dict()['SHAREJSESSIONID']
cookie = 'SHAREJSESSIONID='+SHAREJSESSIONID
print(cookie)

session = requests.Session()
login_url = "http://218.5.5.242:8022/manage-api/user/login"
params = {
    "phone": "g2320650",
    "password": "e856280b57c90c8f5bd5289821aa25a6"
}
session.get(login_url, params=params)
SHAREJSESSIONID = session.cookies.get_dict()['SHAREJSESSIONID']
cookie_others = 'SHAREJSESSIONID='+SHAREJSESSIONID
print(cookie_others)

# 获取总作业id,学生id
url2 = r"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/Page?courseId=514&pageNo=1&pageSize=8&state=4"
header = {
    "Accept": "application/json, text/plain, */*",
    "Cookie": f"{cookie}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
}
header_others = {
    "Accept": "application/json, text/plain, */*",
    "Cookie": f"{cookie_others}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0"
}
response = requests.post(url2, headers=header)
print(response.text)
num = response.json()["data"]['list'][0]['qulzId']
stu_id = response.json()["data"]['list'][0]['stuId']
print(num)
print(stu_id)
# 获取题目id
questionId_url = rf"http://218.5.5.242:8022/course/course-api/courses/qulz/getStuQulz?id={num}"
response3 = requests.post(questionId_url, headers=header)
response = requests.post(questionId_url, headers=header).json()
for i in response['data']['qulzchoose']:
    questionId_list.append(i['questionId'])
print(questionId_list)
for i in response['data']['qulzoj']:
    oj_id_list.append(i['questionId'])

# 获取答案
url3 = f"http://218.5.5.242:8022/course/course-api/courses/qulz/getUserId?id={num}"
response3 = requests.post(url3, headers=header_others)
answer = response3.json()

if answer['data']['chooseProblem']:
    c = answer['data']['chooseProblem']
    question_num = len(c)
    print('选择题答案：')
    for i in range(0, question_num):
        choice_answer = answer['data']['chooseProblem'][i]['answer']
        answer_and_id = choice_answer
        choice_answer_list.append(answer_and_id)
    print(choice_answer_list)

if answer['data']['ojProblemList']:
    s = answer['data']['ojProblemList']
    question_num = len(s)
    # print(question_num)
    print('-------------------------------------------')
    for i in range(0, question_num):
        oj_answer = answer['data']['ojProblemList'][i]['viewAnswer']
        print(oj_answer)
        oj_answer_list.append(oj_answer)
        print()
        print()

    print('-------------------------------------------')

# 选择答案
post_answer_url = rf"http://218.5.5.242:8022/course/course-api/qulz_oj/submitProblemAnswer/{num}"
for p_id, p_answer in enumerate(choice_answer_list):
    data = {
        "answer": f"{p_answer}",
        "problemValue": "1",
        "problemId": questionId_list[p_id],
    }
    response4 = requests.post(post_answer_url, headers=header, json=data)
    print(response4.text)

    # 提交答案
    post_url = r"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/studentUpdate"
    data2 = {
      "stuId": stu_id,
      "qulzId": f"{num}"
    }

    response5 = requests.post(post_url,headers=header,json=data2)
    print(response5.text)


# oj答案
post_answer_url = r'http://218.5.5.242:8022/oj/Oj-api/judge/JugerServerId'
for p_id, p_answer in enumerate(oj_answer_list):
    data = {
        "proId": oj_id_list[p_id],
        "examId": f"{num}",
        "type": 1,
        "language": "py3",
        "answer": f"{p_answer}",
    }
    print(data)
    response4 = requests.post(post_answer_url, headers=header, data=data)
    print(response4.text)

    # 提交答案
    post_url = r"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/studentUpdate"
    data2 = {
      "stuId": stu_id,
      "qulzId": f"{num}"
    }

    response5 = requests.post(post_url,headers=header,json=data2)
    print(response5.text)

