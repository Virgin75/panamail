import psycopg2


conn = psycopg2.connect(
  host='0.0.0.0',
  port='5432',
  database='default_database',
  user='username',
  password='password'
)
cursor = conn.cursor()
cursor.execute('SELECT * FROM utilisateur')
conn.commit()

print(cursor.fetchall())
cursor.close()


# Display all results : cursor.fetchall()

"""
'CREATE TABLE utilisateur' +
'(' +
    'id INT PRIMARY KEY NOT NULL,' +
    'nom VARCHAR(100),' +
    'prenom VARCHAR(100),' +
    'email VARCHAR(255),' +
    'date_naissance DATE,' +
    'pays VARCHAR(255),' +
    'ville VARCHAR(255),' +
    'code_postal VARCHAR(5),' +
    'nombre_achat INT' +
')'
"""

"""
"INSERT INTO utilisateur (email, nom, id) VALUES(%s, %s, %s)", ('paul@gmail.com', 'PAul', 1)
"""