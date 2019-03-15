

import mysql.connector

mydb=mysql.connector.connect(

	host = 'localhost',
	user = 'root',
	passwd = 'gatik@123',
	database = 'test'

)


print("Db Connected")

mycursor =mydb.cursor()
name ="Asikka"
sql = """insert into demo (userid) values (?) """
value=("sugu")
mycursor.execute(sql,("sugu")
mydb.commit()
print(mycursor.rowcount,"Record inserted")
