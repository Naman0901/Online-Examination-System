import functools
import smtplib
from flask import( Blueprint, flash, g, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from OES.db import get_db
from datetime import date,time,timezone

bp= Blueprint('auth', __name__)
@bp.route('/register',methods=('GET','POST'))

def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Username is Required.'
        elif not password:
            error = 'Password is Required.'
        elif not firstname:
            error = 'Firstname is Required.'
        elif not lastname:
            error = 'Lastname is Required.'
        elif not email:
            error = 'E-mail is Required.'
        elif db.execute(
            'SELECT id FROM student WHERE username = ?',(username,)
            ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO student(username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)',
                (username, generate_password_hash(password), firstname, lastname, email))
            db.commit()
            db.execute(
                'INSERT INTO user(username, password, email, u_type) VALUES (?,?,?,?) ',
                (username, generate_password_hash(password),email, 'student',))
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.html')

        
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'+username
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'+username

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            if user['u_type'] == 'admin':
                username=user['username']
                return redirect(url_for('auth.admin',users=username))
            if user['u_type'] =='faculty':
                uname=user['username']                
                global fac
                fac = db.execute('select id from faculty where username=?',(user['username'],)).fetchone()                              
                return redirect(url_for('auth.faculty',users=uname))
            if user['u_type'] == 'student':
                uname=user['username']
                global stud
                stud = db.execute('SELECT * FROM student WHERE USERNAME = ?',(user['username'],)).fetchone()
                return redirect(url_for('auth.student', users=uname))
        flash(error)    
    return render_template('login.html')


def login_required(view):
    @functools.wraps(view)  
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/forgot', methods=('GET', 'POST'))
def forgotpassword():
    if request.method == 'POST':
        username = request.form['username']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if user is None:
            error = 'Incorrect Username.'

        if error is None:
            gmailaddress = '19DCE032@charusat.edu.in'
            gmailpassword = 'namang942'
            mailto = user['email']
            passwd = user['username']
            msg='Your Password is ' + passwd
            db = get_db()
            db.execute('update user set password=? where username=?',(generate_password_hash(passwd),user['username'],))
            db.commit()
            mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
            mailServer.starttls()
            mailServer.login(gmailaddress , gmailpassword)
            mailServer.sendmail(gmailaddress, mailto , str(msg))            
            mailServer.quit()
            '''return redirect(url_for('auth.login'))'''
            error = 'Message Sent Successfully'
        flash(error)
    return render_template('forgot.html')


@bp.route('/admin/<users>', methods=('GET', 'POST'))
def admin(users):
    if request.method == 'GET':
        return render_template('admindashboard.html',username=users)

@bp.route('/faculty/<users>', methods=('GET', 'POST'))
def faculty(users):
    if request.method == 'GET':
        faculty=facultydata(fac['id'])
        return render_template('Facultydashboard.html',username=users,firstname=faculty['firstname'],lastname=faculty['lastname'])

@bp.route('/student/<users>', methods=('GET', 'POST'))
def student(users):
    if request.method == 'GET':
        student=studentdata(stud['id'])
        return render_template('studentdashboard.html',username=users,
        firstname='First Name : '+student['firstname'],lastname='Last Name : '+student['lastname'],rollno='Roll No. : '+str(student['rollno'])
        , sems='Semester : '+str(student['sem']),stds='Class : '+str(student['class']),email='E-Mail : '+student['email'])

@bp.route('/createtest', methods=('GET', 'POST'))
@login_required
def createtest():
    if request.method == 'POST':
        tname=request.form['name']
        sub=request.form['subject']
        mark=request.form['mark']
        time=request.form['stime']
        dur=request.form['duration']
        sem=request.form['sem']
        noque=request.form['que']
        db=get_db()
        error=None
        if tname is None:
            error='please check again'
        if error is None:
            test = db.execute(
                'INSERT INTO test(username,tname,tsub,tmarks,tstime,tduration,tsem,tnoque) VALUES (?,?,?,?,?,?,?,?)',
                (str(g.user['username']),str(tname),str(sub),int(mark),str(time),str(dur),int(sem),int(noque),))
            db.commit()
            tstid=db.execute('select id from test where username=? and tname=?',(str(g.user['username']),str(tname),)).fetchone()
            return redirect(url_for('auth.question',tid=tstid['id'],num=1))
        flash(error)
    if request.method == 'GET' and g.user['u_type']=='admin':
        return render_template('crtest.html')
    if request.method =='GET' and g.user['u_type']=='faculty':
        return render_template('crtest2.html')
    
@bp.route('/question/<tid>/<num>', methods=('GET', 'POST'))
@login_required
def question(tid,num):
    
    if request.method == 'GET':       
        db=get_db()
        test=db.execute('select * from test where id =?',(tid,)).fetchone()
        tot=int(test['tnoque'])
        lef=tot-int(num)     
        return render_template('question.html',no=num,left=lef,total=tot)

    if request.method == 'POST' and g.user['u_type']=='admin':
        quest=request.form['question']
        answer=request.form['ans']
        option1=request.form['opt1']
        option2=request.form['opt2']
        option3=request.form['opt3']
        option4=request.form['opt4']
        db=get_db()
        test=db.execute('select * from test where id =?',(tid,)).fetchone()
        tot=int(test['tnoque'])
        lef=tot-int(num) 
        q=db.execute('select * from que where testid=?',(tid,)).fetchall()
        if q==None:
            db.execute(
                'insert into que(testid,ques,ans,opt1,opt2,opt3,opt4,queid) VALUES(?,?,?,?,?,?,?,?)',
                (tid,quest,answer,option1,option2,option3,option4,int(num),))
            db.commit()
        else:
            db.execute(
                'update que set ques=?,ans=?,opt1=?,opt2=?,opt3=?,opt4=? where testid=? and queid=?',
                (quest,answer,option1,option2,option3,option4,int(tid),int(num),))
            db.commit()
        numb=int(num)+1
        lef-=1
        if lef!=0:
            return redirect(url_for('auth.question',tid=test['id'],num=numb))
        return render_template('admindashboard.html',username=g.user['username'])

    elif request.method == 'POST' and g.user['u_type']=='faculty':
        quest=request.form['question']
        answer=request.form['ans']
        option1=request.form['opt1']
        option2=request.form['opt2']
        option3=request.form['opt3']
        option4=request.form['opt4']
        db=get_db()
        test=db.execute('select * from test where id =?',(tid,)).fetchone()
        tot=int(test['tnoque'])
        lef=tot-int(num)
        q=db.execute('select * from que where testid=?',(tid,)).fetchall()
        if q==None:
            db.execute(
                'insert into que(testid,ques,ans,opt1,opt2,opt3,opt4,queid) VALUES(?,?,?,?,?,?,?,?)',
                (tid,quest,answer,option1,option2,option3,option4,int(num),))
            db.commit()
        else:
            db.execute(
                'update que set ques=?,ans=?,opt1=?,opt2=?,opt3=?,opt4=? where testid=? and queid=?',
                (quest,answer,option1,option2,option3,option4,int(tid),int(num),))
            db.commit()
        numb=int(num)+1
        lef-=1
        print(numb)
        print(lef)
        if lef!=-1:
            return redirect(url_for('auth.question',tid=test['id'],num=numb))
        faculty=facultydata(fac['id'])
        return render_template('Facultydashboard.html',username=g.user['username'],firstname=faculty['firstname'],lastname=faculty['lastname'])

@bp.route('/alltest', methods=('GET','POST'))
@login_required
def testtable():
    if request.method=='GET' and g.user['u_type']=='admin':
        db=get_db()
        tests=db.execute('SELECT * FROM test').fetchall()
        return render_template('edittesttable.html', rows=tests)
    elif request.method=='GET' and g.user['u_type']=='faculty':
        db=get_db()
        tests=db.execute('SELECT * FROM test where username = ?',(g.user['username'],)).fetchall()
        return render_template('edittesttable2.html', rows=tests)
    elif request.method=='GET' and g.user['u_type']=='student':
        db=get_db()
        student=db.execute('select * from student where username=?',(g.user['username'],)).fetchone()
        tests=db.execute('SELECT * FROM test where tsem = ?',(student['sem'],)).fetchall()
        return render_template('showtest.html', rows=tests)
    
    if request.method=='POST' and request.form['tid'] != "" and request.form['tdid'] == "" and g.user['u_type'] == "student":
        return redirect(url_for('auth.exam', tid =request.form['tid'], num=1, mark=0))

    if request.method=='POST' and request.form['tid'] == "" and request.form['tdid'] != "" and g.user['u_type'] == "student":
        db=get_db()
        result=db.execute('select * from marks where testid=? and userid=?',(int(request.form['tdid']),g.user['id'],)).fetchall()
        return render_template('result.html', rows=result)

    elif request.method=='POST' and request.form['tid'] != "" and request.form['tdid'] == "":
        return redirect(url_for('auth.edittest',testid=request.form['tid']))
    
    elif request.method=='POST' and request.form['qid']!="":
        return redirect(url_for('auth.question',tid=request.form['qid'],num=1))

    elif request.method=='POST' and request.form['tdid'] != "" and request.form['tid']=="":
        db=get_db()
        db.execute('DELETE from test where id = ?', (int(request.form['tdid']),))
        db.commit()
        return redirect(url_for('auth.testtable'))


@bp.route('/edittest/<testid>', methods=('GET', 'POST'))
@login_required
def edittest(testid):
    if request.method=="POST":
        tname=request.form['name']
        sub=request.form['subject']
        mark=request.form['mark']
        time=request.form['stime']
        dur=request.form['duration']
        sem=request.form['sem']
        noque=request.form['que']
        error=None
        db=get_db()
        if error is None and g.user['u_type']=='admin':
            test = db.execute(
                'UPDATE test SET username = ?,tname = ?,tsub = ?,tmarks = ?,tstime = ?,tduration = ?,tsem = ?,tnoque = ? where id = ?',
                (str(g.user['username']),str(tname),str(sub),int(mark),str(time),str(dur),int(sem),int(noque),int(testid),))
            db.commit()
            return redirect(url_for('auth.admin', users=g.user['username']))
        elif g.user['u_type']=='faculty':
            test2 = db.execute(
                'UPDATE test SET username = ?,tname = ?,tsub = ?,tmarks = ?,tstime = ?,tduration = ?,tsem = ?,tnoque = ? where id = ?',
                (str(g.user['username']),str(tname),str(sub),int(mark),str(time),str(dur),int(sem),int(noque),int(testid),))
            db.commit()
            faculty=facultydata(fac['id'])
            return render_template('Facultydashboard.html',username=g.user['username'],firstname=faculty['firstname'],lastname=faculty['lastname'],subject=faculty['subj'],dept=faculty['dept'])


    if request.method=="GET" and g.user['u_type']=='admin':
        db=get_db()
        info=db.execute(
            'select * from test where id = ?',(int(testid),)).fetchone()
        return render_template('edittest.html', testname=info['tname'],subject=info['tsub'],marks=info['tmarks'],time=info['tstime'],
        duration=info['tduration'],sem=info['tsem'],que=info['tnoque'])

    if request.method=="GET" and g.user['u_type']=='faculty':
        db=get_db()
        info=db.execute(
            'select * from test where id = ?',(int(testid),)).fetchone()
        return render_template('edittest2.html', testname=info['tname'],subject=info['tsub'],marks=info['tmarks'],time=info['tstime'],
        duration=info['tduration'],sem=info['tsem'],que=info['tnoque'])
      

@bp.route('/addfaculty', methods=('GET', 'POST'))
@login_required
def addfaculty():
    if request.method == 'POST':
        uname=request.form['username']
        password=request.form['password']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        subject=request.form['subject']
        dept=request.form['dept']
        db=get_db()
        error=None
        if error is None:
            faculty=db.execute(
                'INSERT INTO Faculty(username,password,firstname,lastname,email,subj,dept) VALUES(?,?,?,?,?,?,?)',
                (uname,generate_password_hash(password),firstname,lastname,email,subject,dept,))
            db.commit()
            adduser=db.execute(
                'INSERT INTO user(username, password, email, u_type) VALUES (?,?,?,?) ',
                (uname, generate_password_hash(password),email,'faculty',))
            db.commit()
            error='added Succesfully'
            return render_template('addfaculty.html')
        flash(error)
    return render_template('addfaculty.html')

@bp.route('/allfaculty', methods=('GET','POST'))
@login_required
def facultytable():
    if request.method=='GET' and g.user['u_type']=='admin':
        db=get_db()
        tests=db.execute('SELECT * FROM faculty').fetchall()
        return render_template('editfactable.html', rows=tests)
    elif request.method=='POST' and request.form['fid'] != "" and request.form['fdid'] != "":
        return redirect(url_for('auth.editfaculty',facid=request.form['fid']))
    elif request.method=='POST' and request.form['fdid'] != "" and request.form['fid']=="":
        db=get_db()
        db.execute('DELETE from faculty where id = ?', (int(request.form['fdid']),))
        db.commit()
        return redirect(url_for('auth.facultytable'))


@bp.route('/editfaculty', methods=('GET', 'POST'))
@login_required
def editfaculty(facid):
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        subject=request.form['subject']
        dept=request.form['dept']
        db=get_db()
        error=None
        if error is None:
            faculty=db.execute(
                'UPDATE faculty SET firstname=?,lastname=?,email=?,subject=?,dept=? where id=?',
                (firstname,lastname,email,subject,dept,int(facid),))
            db.commit()
            return redirect(url_for('auth.admin', users=g.user['username']))
    if request.method=='GET':
        db=get_db()
        info=db.execute(
            'select * from faculty where id = ?',(int(facid),)).fetchone()
        return render_template('editfaculty.html', uname=info['username'],subject=info['subj'],passd=info['password'],fname=info['firstname'],
        lname=info['lastname'],mail=info['email'],depta=info['dept'])


@bp.route('/editstudent', methods=('GET', 'POST'))
@login_required
def editstudent():
    db=get_db()
    student=db.execute('SELECT * FROM STUDENT where username=?',(g.user['username'],)).fetchone()
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        std=request.form['std']
        sem=request.form['sem']
        roll=request.form['roll']
        studentdata=db.execute(
                'UPDATE student SET firstname=?,lastname=?,email=?,class=?,sem=?,rollno=? where id=?',
                (firstname,lastname,email,std,sem,roll,int(student['id']),))
        db.commit()
        return redirect(url_for('auth.student', users=g.user['username']))

    if request.method=='GET':
        db=get_db()
        info=db.execute(
            'select * from student where id = ?',(int(student['id']),)).fetchone()
        return render_template('editprofile.html', uname=info['username'],sem=info['sem'],std=info['class'],fname=info['firstname'],
        lname=info['lastname'],mail=info['email'],roll=info['rollno'])

@bp.route('/exam<tid>/<num>/<mark>', methods=('GET', 'POST'))
@login_required
def exam(tid,num,mark):
    db=get_db()
    ques=db.execute('select * from test where id=?',(int(tid),)).fetchone()
    totque=ques['tnoque']    
    left=int(totque)-int(num)
    question = db.execute('select * from que where testid=? and queid=?',(int(tid),int(num))).fetchone()
    ans=question['ans']
    aval=db.execute('select * from test where id=? and tstime<CURRENT_TIMESTAMP',(int(tid),)).fetchall()
    if aval!=None:
        if request.method == 'GET':               
            return render_template('exam.html',no=num,que=question['ques'],opt1=question['opt1'],opt2=question['opt2'],opt3=question['opt3'],
            opt4=question['opt4'],left=left,total=totque)
        
        elif request.method == 'POST':
            userans=request.form['ans']
            info=db.execute('select * from marks where testid=? and userid=?',(int(tid),g.user['id'],)).fetchone()
            if info == None and userans==ans:
                mark=int(mark)+1
                db.execute('insert into marks(testid,uname,userid,mark) VALUES(?,?,?,?)',(int(tid),g.user['username'],g.user['id'],mark,))
                db.commit()
            elif info == None and userans!=ans:
                db.execute('insert into marks(testid,uname,userid,mark) VALUES(?,?,?,?)',(int(tid),g.user['username'],g.user['id'],mark,))
                db.commit()
            elif info !=None and userans==ans:
                print('enters')
                mark=int(mark)+1
                db.execute('update marks set mark=? where testid=? and userid=?',(mark,int(tid),g.user['id']))
                db.commit()

            num=int(num)+1
            left=totque-num
            if num<=totque:
                return redirect(url_for('auth.exam', tid = int(tid),num = num,mark=int(mark)))
            return redirect(url_for('auth.testtable'))
        return redirect(url_for('auth.testtable'))
    else :
        flash('EXAM CANNOT BE START BEFORE TIME')        



@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def facultydata(fid):
    faculty=get_db().execute('SELECT * FROM faculty where id=?',(int(fid),)).fetchone()
    return faculty

def studentdata(sid):
    student=get_db().execute('SELECT * FROM student where id=?',(int(sid),)).fetchone()
    return student

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))


                
    
