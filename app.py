from flask import Flask, render_template, make_response, request, redirect, url_for, flash, session
import re
import requests
import api8022
import time

app = Flask(__name__)
app.secret_key = '1145141919810'

@app.route('/')
@app.route('/auto8022')
def auto8022():
    ck = request.cookies.get('ck')
    if ck:
        info_list, name = api8022.get_basic_info(ck)
        return render_template('auto8022v2.html', name = name, info_list = info_list)
    else:
        return redirect(url_for('login'))


@app.route('/check', methods=['POST'])
def check():
    self_account = request.form.get('self_account')
    self_password = request.form.get('self_password')
    other_account = request.form.get('other_account')
    other_password = request.form.get('other_password')
    
    if not re.match('g[0-9]+', self_account) or not re.match('g[0-9]+', other_account):
        flash('账号格式错误')
        return redirect(url_for('login'))
    
    ck, status_code = api8022.login(self_account, self_password)
    other_ck, other_status_code = api8022.login(other_account, other_password)
    if status_code != 200 or other_status_code != 200:
        flash('账号或密码错误')
        return redirect(url_for('login'))
    
    resp = make_response(redirect(url_for('auto8022')))
    resp.set_cookie('ck', ck)
    resp.set_cookie('other_ck', other_ck)
    return resp


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/complete_quiz', methods=['POST'])
def complete_quiz():
    num = request.form.get('num')

    ck = request.cookies.get('ck')
    info_list, _ = api8022.get_basic_info(ck)
    stuid = info_list[0]['stu_id']
    question_id_list, oj_id_list = api8022.get_question_id_list(ck, num)

    other_ck = request.cookies.get('other_ck')


    choice_answer_list, oj_answer_list = api8022.get_answer(other_ck, num)
    print(choice_answer_list, oj_answer_list)
    
    time.sleep(2)
    api8022.submit_answer(ck, num, stuid, choice_answer_list, oj_answer_list, question_id_list, oj_id_list)


    return redirect(url_for('auto8022'))


if __name__ == '__main__':
    app.run(debug=True, threaded=True)