from flask import Flask,render_template,request,json,jsonify,session,g,url_for
import pickle

from flask_mysqldb import MySQL
import numpy as np



app= Flask(__name__)


#################################################
#################################################

app.secret_key="MYKEY360"
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_DB']='nodes'
app.config['MYSQL_CURSOR']='DictCursor'

mysql = MySQL(app)

################################################
#################################################
import model_api as m_api
from mypanel import panel_
app.register_blueprint(panel_)



@app.before_request
def before_request():
    g.user=None
    g.name=None
    if 'user' in session:
        g.user=session['user']
        g.name=session['name']
        g.id=session['id']


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/about')
def about_view():
    return render_template('about.html')

@app.route('/predict',methods=['POST'])
def predict():
    if g.user:
        cur = mysql.connection.cursor()
        node1 = request.form['n1']
        node2 = request.form['n2']
        
        cur.execute("SELECT * FROM tbl_predicted where user_id=%s and node1=%s and node2=%s",[int(g.id),node1,node2])
        result=cur.fetchall()

        cur.execute("SELECT * FROM tbl_predicted where user_id=%s and node1=%s and node2=%s",[int(g.id),node2,node1])
        result2=cur.fetchall()

        if(len(result)>0 or len(result2)>0):
            return "Previously Predicted Edge"
        else:
            if(node1.isdigit()==False):
                return jsonify("-2")
            elif(node2.isdigit()==False):
                return jsonify("-2")
            else:
                cur.execute("SELECT * FROM embeds where node = %s",[str(node1)])
                results1=cur.fetchall()
                cur.execute("SELECT * FROM embeds where node = %s",[str(node2)])
                results2=cur.fetchall()
                if(len(results1) == 0):
                    return jsonify("Node 1 not found")
                elif(len(results2)==0):
                    return jsonify("Node 2 not found")
                else:
                    results1=np.array(results1)
                    results1=np.delete(results1,0)
                    results2=np.array(results2)
                    results2=np.delete(results2,0)
                    edge_emb=np.multiply(results1,results2)
                    edge_emb=np.append(edge_emb,int(node1))
                    edge_emb=np.append(edge_emb,int(node2))
                    api_call=m_api.controller(edge_emb)
                    if(api_call=="positive"):
                        cur.execute("INSERT INTO tbl_predicted (user_id,node1,node2,sign) VALUES (%s,%s,%s,%s)",[int(session['id']),int(node1),int(node2),"pos"])
                        mysql.connection.commit()
                        return jsonify("You Predicted a Positive Edge")
                    elif(api_call=="negative"):
                        cur.execute("INSERT INTO tbl_predicted (user_id,node1,node2,sign) VALUES (%s,%s,%s,%s)",[int(session['id']),int(node1),int(node2),"neg"])
                        mysql.connection.commit()
                        return jsonify("You Predicted a Negative Edge")
                    elif(api_call=="no"):
                        cur.execute("INSERT INTO tbl_predicted (user_id,node1,node2,sign) VALUES (%s,%s,%s,%s)",[int(session['id']),int(node1),int(node2),"no"])
                        mysql.connection.commit()
                        return jsonify("You Predicted a Missing Edge")
                    else:
                        return jsonify("Something went wrong")
    else:
        session["refer"]='http.index'
        return jsonify("-1")


if __name__ == "__main__":
    app.run(debug=True)