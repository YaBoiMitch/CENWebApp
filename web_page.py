"""
    WISHLIST:
        IMMEDIATE:
            Upload files
        NOT:
            Change Current Students redirect
            Implement 'remember me' (not forgot your password?)
            Admin Account?
"""

import sqlite3
import database as adb

from flask import Flask, render_template, request, url_for, redirect, g, escape, session
#from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
#from werkzeug import generate_password_hash, check_password_hash

#init stuff
DATABASE = 'SCIP.db'
PORT = 5003
DEBUG = True
app = Flask(__name__)
app.secret_key = "asdfq3495basdfbsdpo2451"

#################################
#############WEBPAGE#############
#################################

@app.route('/')
def main():
    session.clear()
    app.logger.debug('Main page accessed')
    return render_template('index.html')

@app.route('/SCIP')
def choice():
    app.logger.debug('Main page accessed')

    try:
        if escape(session['type']) == 'student':
            return redirect('/Student/Home')
    except:
        pass
    
    return render_template('choice.html')

#######################
#####Student pages#####
#######################

@app.route('/Students')
def student():
    try:
        if escape(session['type']) == 'student':
            return redirect('/Student/Home')
    except:
        pass

    return render_template('students.html')

@app.route('/Student/Login', methods=['GET', 'POST'])
def studentLogin():
    try:
        if escape(session['type']) == 'student':
            return redirect('/Student/Home')
    except:
        pass
    
    error = None
    if request.method == 'POST':
        #valid_login not implemented
        if valid_login(request.form['email'],
                       request.form['password'],
                       True):
            session['uname'] = request.form['email']
            session['type']  = "student"
            return redirect('/Student/Home')
        else:
            error = 'Invalid username/password'

    return render_template('studentlogin.html', error=error)

@app.route('/Student/Register', methods=['GET', 'POST'])
def studentRegister():
    try:
        if escape(session['type']) == 'student':
            return redirect('/Student/Home')
    except:
        pass
    
    error = None
    if request.method == 'POST':
        #valid_login not implemented

        #returns 0 if successful, 1 if username already taken
        #2 if passwords dont match up, 3 if email already taken/invalid
        flag = reg_student(request.form['first'] + ' ' + request.form['last'],
                            request.form['password'],
                            request.form['cpassword'],
                            request.form['email'])
        if not flag: #log in not implemented
            session['uname'] = request.form['email']
            session['type']  = 'student'
            return redirect('/Student/Home')
        elif flag == 1:
            error = 'Invalid username/password'
        elif flag == 2:
            error = 'Invalid e-mail'
        elif flag == 4:
            error = 'E-mail already in use!'

    return render_template('studentregister.html', error=error)

@app.route('/Student/Home')
def studentHome():
    try:
        if escape(session['type']) == 'student':
            return render_template('studenthome.html')
    except:
        pass
    
    return redirect('/Students')

@app.route('/Student/Search', methods=['GET', 'POST'])
def studentSearch():
    
    if escape(session['type']) == 'student':
        if request.method == 'POST':
            return render_template('studentsearch.html')
        else: 
            return render_template('studentsearch.html',
                        table=[(i[0], i[4], i[5], "", "", "") for i in adb.view_cjoini_t()])

    return redirect('/Students')

@app.route('/Student/Apply')
def studentApply():
    return 'studentApply'

########################
#####Employee pages#####
########################

@app.route('/Employers')
def employer():
    try:
        if escape(session['type']) == 'employer':
            return redirect('/Employer/Home')
    except:
        pass
    
    return render_template('employers.html')

@app.route('/Employers/Login', methods=['GET', 'POST'])
def employerLogin():
    try:
        if escape(session['type']) == 'employer':
            return redirect('/Employer/Home')
    except:
        pass
    
    error = None
    if request.method == 'POST':
        #valid_login not implemented
        if valid_login(request.form['email'],
                       request.form['password'],
                       False):
            session['uname'] = request.form['email']
            session['type']  = "employer"
            return redirect('/Employer/Home') #log in not implemented
        else:
            error = 'Invalid username/password'

    return render_template('employerlogin.html', error=error)
        
@app.route('/Employers/Register', methods=['GET', 'POST'])
def employerRegister():
    try: #if already logged in as employer go straight to home
        if escape(session['type']) == 'employer':
            return redirect('/Employer/Home')
    except:
        pass
    
    error = None
    if request.method == 'POST':
        #returns 0 if successful, 1 if username already taken
        #2 if passwords dont match up, 3 if email already taken/invalid
        flag = reg_employer(request.form['username'],
                            request.form['password'],
                            request.form['cpassword'],
                            request.form['email'])

        if not flag: #log in not implemented
            session['uname'] = request.form['email']
            session['type']  = "employer"
            return log_employer_in('email')
        elif flag == 1:
            error = 'Invalid username/password'
        elif flag == 2:
            error = 'Invalid e-mail'
        elif flag == 3:
            error = 'Company or E-mail already in use!'

    return render_template('employerregister.html', error=error)

@app.route('/Employer/Home')
def employerHome():
    try:
        if escape(session['type']) == 'employer':
            return render_template('employerhome.html')
    except:
        pass
    
    return redirect('/Employers')

@app.route('/Employer/EditLogo')
def employerEditLogo():
    return 'employer'

@app.route('/Employer/AddInternships', methods=['GET', 'POST'])
def employerAddInt():
    if request.method == 'POST':
        #use the logged in uname(email) and position name
        #to create position in db module
        #need to implement description 
        adb.add_internship(session['uname'], request.form['posname'])
        return 'asdf' + render_template('employeraddinternships.html')
    
    try:
        if escape(session['type']) == 'employer':
            return render_template('employeraddinternships.html')
    except:
        pass

    return redirect('/Employers')

@app.route('/Employer/ViewInternships')
def employerViewInt():
    return 'employer'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def valid_login(email, password, student = True):
    if student and adb.student_login(email, password):
        return True
    if not student and adb.company_login(email, password):
        return True

    return False
    
def log_employer_in(username):
    return redirect('/Employer/Home')

def log_student_in(username):
    return redirect('/Student/Home')

#need to check if email is a possible valid email
#need to have some checks on arguments
def reg_employer(name, password, cpassword, email):

    #return 1 if passwords not equal error
    if password != cpassword:
        return 1
    if '@' not in email:
        return 2
    for r in adb.view_company_t(): #companies can't have same name
        if name == r[0] or email == r[4]:
            return 3
    
    else:
        adb.add_company(name, password, email)
        return False


def reg_student(name, password, cpassword, email):

    #return 1 if passwords not equal error
    if password != cpassword:
        return 1
    if '@' not in email:
        return 2
    for r in adb.view_student_t(): #students cant have same email
        if email == r[4]:
            return 4  
    else:
        adb.add_student(name, password, email)
        return False
    

################UTILITY DEBUGGING FUNCTIONS###################
@app.route('/Admin/RecreateDB')
def adminDB():
    adb.create_db()
    return 'done'

@app.route('/Admin/ViewT')
def adminSType():
    return session['type']

@app.route('/Admin/ViewC')
def adminViewC():
    s = ""
    for r in adb.view_company_t():
        s += str(r) + '\n'

    return s

@app.route('/Admin/ViewS')
def adminViewS():
    s = ""
    for r in adb.view_student_t():
        s += str(r) + '\n'

    return s

@app.route('/Admin/ViewI')
def adminViewI():
    s = ""
    for r in adb.view_internship_t():
        s += str(r) + '\n'

    return s

if __name__ == "__main__":
    app.logger.setLevel(0)
    app.run(port=PORT, debug=True)