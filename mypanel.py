from flask import Blueprint,render_template,jsonify,redirect,request,url_for,session,g
from flask_mysqldb import MySQL
from app import mysql
panel_=Blueprint('panel_',__name__)



@panel_.before_request
def before_request():
    g.user=None
    g.name=None
    g.id=None
    g.refer=None

    if 'user' in session:
        g.user=session['user']
        g.name=session['name']
        g.id=session['id']
    if 'refer' in session:
        g.refer=session['refer']

@panel_.route('/login/logout',methods=['GET'])
def logout():
    if g.user:
        session.pop('user',None)
        session.pop('name',None)
        session.pop('id',None)
        return redirect(request.referrer)
    else:
        return redirect('/login/index')

@panel_.route('/login/dashboard',methods=['GET'])
def dashboard_view():
    if g.user:
        if g.name:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM tbl_predicted where user_id= %s ",[int(g.id)])
            results=cur.fetchall()

            cur.execute("SELECT * FROM tbl_predicted where user_id= %s and sign='pos' ",[int(g.id)])
            pos_results=cur.fetchall()

            cur.execute("SELECT * FROM tbl_predicted where user_id= %s and sign='neg' ",[int(g.id)])
            neg_results=cur.fetchall()

            cur.execute("SELECT * FROM tbl_predicted where user_id=%s and sign='no' ",[int(g.id)])
            missing_results=cur.fetchall()

            neg_score=int((len(neg_results)*2))
            pos_score=len(pos_results)
            missing_score=int((len(missing_results)*0.5))
            return render_template('login/dashboard.html',name=g.name,total=len(results),pos=len(pos_results),neg=len(neg_results),no=len(missing_results),neg_score=neg_score,pos_score=pos_score,missing_score=missing_score)
    else:
        return redirect(url_for('panel_.index_login'))


@panel_.route('/login/history',methods=['GET'])
def history_view():
    if g.user:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM tbl_predicted where user_id=%s',[int(g.id)])
        history=cur.fetchall()

        return render_template('login/history.html',hist=history,len=len(history))
    else:
        return redirect(url_for('panel_.index_login'))

@panel_.route('/login/profile',methods=['GET'])
def profile_view():
    if g.user:
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM tbl_users where id=%s and email=%s',[int(g.id),g.user])
        results=cur.fetchall()
        return render_template('login/profile.html',email=results[0][1],name=results[0][3])





@panel_.route('/login/index',methods=['GET'])
def index_login():
    if g.user:
        return redirect(url_for('panel_.dashboard_view'))
    else:
        return render_template('login/index.html')



@panel_.route('/login/auth',methods=['POST'])
def login_auth():
    if request.method=='POST':
        cur = mysql.connection.cursor()
        session.pop('user',None)
        email=str(request.form["email"])
        password=str(request.form["password"])
        cur.execute("SELECT * FROM tbl_users where email = %s and password= %s",[email,password])
        results=cur.fetchall()
        if(len(results)>0):
            if(email==results[0][1] and password==results[0][2]):
                session['user']=email
                session['name']=results[0][3]
                session['id']=results[0][0]
                if g.refer=='http.index':
                    session.pop('refer',None)
                    return redirect('/')
                else:
                    return redirect(url_for('panel_.dashboard_view'))
            else:
                return redirect(url_for('panel_.index_login',res="eRR"))
        else:
            return redirect(url_for('panel_.index_login',res="eRR"))




@panel_.route('/login/signup',methods=['GET'])
def signup_view():
    return render_template('login/signup.html')




@panel_.route('/login/signup_process',methods=['POST'])
def signup_process():
    try:
        cur = mysql.connection.cursor()
        name=str(request.form['name'])
        password=str(request.form['passwd'])
        email=str(request.form['email'])
        cur.execute("SELECT * FROM tbl_users where email = %s",[email])
        result=cur.fetchall()
        if(len(result)==0):
            cur.execute("INSERT INTO tbl_users (email,password,name) VALUES (%s,%s,%s)",[email,password,name])
            mysql.connection.commit()
            return "Done"
        else:
            return "exists"
    except Exception as e:
        return "Something went wrong"


@panel_.route('/login/pass_update',methods=['POST'])
def update_pass():
    if g.user:
        cur=mysql.connection.cursor()
        if request.method=='POST':
            new_pass=request.form['n_psw']
            old_pass=request.form['o_psw']

            cur.execute("SELECT password FROM tbl_users where email=%s",[g.user])
            result=cur.fetchall()
            if(old_pass !=result[0][0]):
                return redirect(url_for('panel_.profile_view',res="nt"))
            else:
                cur.execute("UPDATE tbl_users SET password=%s where email=%s",[new_pass,g.user])
                mysql.connection.commit()
                return redirect(url_for('panel_.profile_view',res="up"))
    else:
        return redirect(url_for('panel_.index_login'))

@panel_.route('/login/profile_update',methods=['POST'])
def update_profile():
    if g.user:
        cur=mysql.connection.cursor()
        if request.method=='POST':
            email=request.form['emaiL']
            name=request.form['namE']
            
            if(email==g.user):
                return redirect(url_for('panel_.profile_view',res="eRR-S"))
            else:
                cur.execute("SELECT * FROM tbl_users where email = %s",[email])
                result=cur.fetchall()
                if(len(result)>0):
                    return redirect(url_for('panel_.profile_view',res="eRR-X"))
                else:
                    cur.execute("UPDATE tbl_users SET email=%s,name=%s where id=%s",[str(email),str(name),g.id])
                    mysql.connection.commit()
                    session['name']=name
                    session['user']=email
                    return redirect(url_for('panel_.profile_view',res="-C"))
    else:
        return redirect(url_for('panel_.index_login'))