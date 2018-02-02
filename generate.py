from flask import Flask, render_template,make_response,request,redirect,url_for,flash
from flask import send_from_directory
from flask_mysqldb  import MySQL 
import pdfkit
import os
UPLOAD_FOLDER = '/Users/tnvmadhav/Desktop/myflaskapp4/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "first_db"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

mysql = MySQL(app)

@app.route('/')
def index():
	return render_template('imageFileUpload.html')


@app.route('/upload', methods = ['POST'])
def upload():
	file = request.files['inputFile']
	filename = file.filename
	file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
	#return redirect(url_for('uploaded_file',filename=filename))

	cur = mysql.connection.cursor()

	cur.execute("INSERT into first_table(name,id) VALUES(%s,%s)",(filename,11))

	mysql.connection.commit()

	cur.close()

	flash("Successful upload",'success')
	return render_template('imageFileUpload.html')


@app.route('/view_upload',methods = ['POST'])
def view_upload():

	cur = mysql.connection.cursor();

	result = cur.execute("SELECT name from first_table where id='11'")
	filename = cur.fetchone();

	cur.close()

	return redirect(url_for('uploaded_file',filename=filename['name']))



@app.route('/uploads/<filename>')
def uploaded_file(filename):

	

	return render_template('yo.html',filename = filename)
	#return send_from_directory(app.config['UPLOAD_FOLDER'],filename)



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)


