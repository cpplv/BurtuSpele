from flask import Flask, render_template, jsonify, request
import json, webbrowser, os.path
import sqlite3 #bibliotēkas draiveris


app = Flask('app')
app.config['JSON_AS_ASCII'] = False


def exists():
    dbfilename = "dati/top.db"
    db = sqlite3.connect(dbfilename)
    c = db.cursor()		
    #get the count of tables with the name
    c.execute(""" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='records' """)
    #if the count is 1, then table exists
    if c.fetchone()[0]==1: 
        db.close()
        return True
    else:
        db.close()
        return False    


@app.route('/')
def galvenais():
    return render_template("index.html")


@app.route('/top.html')
def topsDB():
    return render_template("top.html")

@app.route('/topDB.html')
def tops():
    dbfilename = "dati/top.db"
    db = sqlite3.connect(dbfilename) # :memory: db tiks izveidota operatīvā atmiņā
    sql = db.cursor()
    if exists():
        sql.execute("SELECT * FROM records ORDER BY rezultats DESC")
        rezultats = sql.fetchall()
        scriptdata = '''<div id="myData"></div>
                 <script>
                    var mainContainer = document.getElementById("myData");'''
        datalist = []
        datalist.append(scriptdata)

        for row in rezultats:
            v = ''' var div = document.createElement("div");
                    div.setAttribute('class', 'timeandstart');
                    div.innerHTML = "{v}" + ": " + "{r}";
                    mainContainer.appendChild(div);
                '''.format(v=row[0], r=row[1])
            datalist.append(v)

        scriptdata = "</script>"
        datalist.append(scriptdata)

        tostring=""
        for x in datalist:
            tostring += x; 
            
        contents = '''<!DOCTYPE html>
                    <html>
                        <head>
                            <meta content="text/html; charset=utf8"
                            http-equiv="content-type">
                            <title>Tops no DB</title>
                            <link href="/static/style.css" rel="stylesheet" />
                        </head>
                        <body>
                            
                            {}
                            
                        </body>
                    </html>
                    '''.format(tostring)

        db.close()


    else:
        contents = "Vēl nebija nevienas spēles!"

    return contents
    

@app.route('/top/rezultati')
def top_rezultati():
  with open("dati/top.json", "r") as f:
    dati = json.loads(f.read()) #load string
  return dati


@app.route('/top/rezultati/jauns', methods=['POST'])
def jauns():
    # POST request
    filename = "dati/top.json"
    dbfilename = "dati/top.db"

    if (not os.path.exists(filename)):
        data = {"top": []}
        with open(filename, "w") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
    ieraksts = request.get_json()
    try:
        ieraksts["rezultats"] = int(ieraksts["rezultats"])
    except:
        return "Stop hacking!"

    with open(filename, "r") as f:
      dati = json.loads(f.read()) #load string

    ir_ieraksts = False
    for i in range(len(dati["top"])): #iešana cauri masīvam
        if dati["top"][i]["vards"] == ieraksts["vards"]:
          dati["top"][i]["rezultats"] = ieraksts["rezultats"]
          ir_ieraksts = True
  
    if not ir_ieraksts: 
        dati["top"].append(ieraksts)

    with open(filename, "w") as f:
      f.write(json.dumps(dati, indent=2, ensure_ascii=False)) #dump string

    #sorting
    with open(filename, "r") as f:
      dati = json.loads(f.read()) #load string

    for i in range(len(dati["top"])-1):
        for j in range(i, len(dati["top"])):
            if dati["top"][i]["rezultats"]<dati["top"][j]["rezultats"]:
                temp = dati["top"][i]
                dati["top"][i] = dati["top"][j]
                dati["top"][j] = temp

    with open(filename, "w") as f:
        f.write(json.dumps(dati, indent=2, ensure_ascii=False)) #dump string

    #SQL daļa
    #pieslēgties DB
    db = sqlite3.connect(dbfilename) # :memory: db tiks izveidota operatīvā atmiņā
    sql = db.cursor()
    if not exists():
        sql.execute("""CREATE TABLE records (
                vards TEXT NOT NULL,
                rezultats INTEGER NOT NULL,
                PRIMARY KEY("vards")
           )""")
        db.commit()

    vards = ieraksts["vards"]
    rezultats = str(ieraksts["rezultats"])
    
    sql.execute("SELECT * FROM records WHERE vards='"+vards+"'")
    sqlrezultats = sql.fetchone()
    
    if sqlrezultats == None:
        sql.execute("INSERT INTO records (vards, rezultats) VALUES ('"+vards+"', "+rezultats+")") 
        db.commit()
    else:
        if ieraksts["rezultats"]>sqlrezultats[1]:
            sql.execute("UPDATE records SET rezultats="+rezultats+" WHERE vards='"+vards+"'") 
            db.commit()

    db.close()
    
    return 'OK', 200



app.run(host='0.0.0.0', port=8080)

