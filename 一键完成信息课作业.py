import requests
from tqdm import tqdm
import time

def login(phone):
    login_url = "http://218.5.5.242:8022/manage-api/user/login"
    params = {
        "phone": phone,
        "password": "e856280b57c90c8f5bd5289821aa25a6"
    }
    # 创建一个新的 session 对象
    session = requests.Session()
    session.get(login_url, params=params)
    ck = session.cookies.get_dict().get('SHAREJSESSIONID', '')
    cookie = 'SHAREJSESSIONID=' + ck
    print('Captain on the bridge')
    # print(f'{phone}: {cookie}')
    return cookie


def get_basic_info(cookie):
    question_id_list = []
    oj_id_list = []
    header = \
        {
            "Accept": "application/json, text/plain, */*",
            "Cookie": f"{cookie}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0"
                          "Safari/537.36 Edg/123.0.0.0"
        }
    url1 = "http://218.5.5.242:8022/teaching/teaching-api/coursechoose/selectCourse"

    course_id = requests.post(url1, headers=header).json()[0]['id']
    url2 = f"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/Page?courseId={course_id}"
    response = requests.post(url2, headers=header)
    # print(response.text)
    num = response.json()["data"]['list'][0]['qulzId']
    stu_id = response.json()["data"]['list'][0]['stuId']
    print('作业id:', num)
    # print('学生ID:', stu_id)

    question_id_url = rf"http://218.5.5.242:8022/course/course-api/courses/qulz/getStuQulz?id={num}"
    response = requests.post(question_id_url, headers=header).json()
    for i in response['data']['qulzchoose']:
        question_id_list.append(i['questionId'])
    # print(question_id_list)
    for i in response['data']['qulzoj']:
        oj_id_list.append(i['questionId'])

    return num, stu_id, question_id_list, oj_id_list


def get_answer(cookie, num):
    choice_answer_list = []
    oj_answer_list = []
    url3 = f"http://218.5.5.242:8022/course/course-api/courses/qulz/getUserId?id={num}"
    header = \
        {
            "Accept": "application/json, text/plain, */*",
            "Cookie": f"{cookie}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0"
                          "Safari/537.36 Edg/123.0.0.0"
        }
    response3 = requests.post(url3, headers=header)
    answer = response3.json()

    if answer['data']['chooseProblem']:
        c = answer['data']['chooseProblem']
        question_num = len(c)
        print('获取答案中：')
        for i in tqdm(range(0, question_num), desc="正在获取选择题答案"):
            choice_answer = answer['data']['chooseProblem'][i]['answer']
            answer_and_id = choice_answer
            choice_answer_list.append(answer_and_id)
        print(choice_answer_list)

    if answer['data']['ojProblemList']:
        s = answer['data']['ojProblemList']
        question_num = len(s)
        # print('编程题答案：')
        for i in tqdm(range(0, question_num), desc="正在获取编程题答案"):
            oj_answer = answer['data']['ojProblemList'][i]['viewAnswer']
            # print(oj_answer)
            oj_answer_list.append(oj_answer)
            # print()
        print(oj_answer_list)

    return choice_answer_list, oj_answer_list


def submit_answer(cookie, num, stu_id, choice_answer_list, oj_answer_list, question_id_list, oj_id_list):
    header = \
        {
            "Accept": "application/json, text/plain, */*",
            "Cookie": f"{cookie}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/123.0.0.0"
                          "Safari/537.36 Edg/123.0.0.0"
        }
    submit_choose_answer_url = rf"http://218.5.5.242:8022/course/course-api/qulz_oj/submitProblemAnswer/{num}"
    submit_oj_answer_url = r'http://218.5.5.242:8022/oj/Oj-api/judge/JugerServerId'
    submit_url = r"http://218.5.5.242:8022/teaching/teaching-api/qulzresult/studentUpdate"

    if choice_answer_list:
        for p_id, p_answer in tqdm(enumerate(choice_answer_list), total=len(choice_answer_list),
                                   desc="正在上传选择题答案"):
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
        for p_id, p_answer in tqdm(enumerate(oj_answer_list),total=len(oj_answer_list), desc="正在上传编程题答案"):
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


def main():
    self_phone = input("输入自己账号(例如g2321435)")
    self_cookie = login(self_phone)
    other_phone = input("指定抄谁的作业(回车跳过,使用默认)：")
    if not other_phone:
        other_phone = 'g2320650'
    other_cookie = login(other_phone)
    num, stu_id, question_id_list, oj_id_list = get_basic_info(self_cookie)
    choice_answer_list, oj_answer_list = get_answer(other_cookie, num)
    print('loading...')
    time.sleep(2)
    submit_answer(self_cookie, num, stu_id, choice_answer_list, oj_answer_list, question_id_list, oj_id_list)

if __name__ == '__main__':
    print("项目地址：https://github.com/QAQ2333333/staff_Auto_8022")
    main()
    print("拿下!")
    input("按任意键退出...")
