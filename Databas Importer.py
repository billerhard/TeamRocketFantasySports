import mysql.connector
conn = mysql.connector.connect (user = 'admin', password = 'password',
                                host ='127.0.0.1', port='8889', database= 'FantaasySports')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS teams(id INTEGER, teamsname TEXT,  wins INTEGER, losses INTEGER, scores INTEGER, description TEXT);")
cursor.execute("INSERT INTO teams(id, teamsname, wins, losses, scores, description"
               ") VALUES(0, 'loopback', '5', '5', '55', 'Local DB');")


results = cursor.fetchall()
print ("Great Success")
