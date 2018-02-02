from flask import Flask , render_template, flash , redirect, url_for , session , request, logging,make_response
from flask_mysqldb  import MySQL 
from wtforms import Form,StringField ,  TextAreaField , PasswordField , validators
from  passlib.hash import sha256_crypt  
from functools import wraps
import os
import pdfkit
from wtforms.fields.html5 import EmailField
from flask.ext.uploads import UploadSet , configure_uploads , IMAGES
UPLOAD_FOLDER = '/Users/tnvmadhav/Desktop/myflaskapp4/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#config MySQL

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "myFlaskApp"
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

#init mysql
mysql = MySQL(app)


@app.route('/')
def index():

	# Create Cursor
	cur = mysql.connection.cursor()
	cur1 = mysql.connection.cursor()
	cur2  = mysql.connection.cursor()


	#Cursor execution

	result = cur.execute("SELECT * from report ORDER BY rand() LIMIT 1;")


	if result > 0:
		data = cur.fetchone()

	cur.close()

	return render_template('home.html' , data = data)





@app.route('/about')
def about():
	return render_template('about.html')
    #FAQS

@app.route('/faqs', methods = ['GET','POST'])
def faqs():

	cur = mysql.connection.cursor()
	cur1 = mysql.connection.cursor()

	
	

	result = cur.execute("SELECT * from faqs")
	cur1.execute("INSERT into faqs(questions) VALUES(%s)",[request.args.get('question')])
	mysql.connection.commit()
	faqs = cur.fetchall()
	if result > 0:
		return render_template('faqs.html' , faqs = faqs)

	else:
		flash("There are no questions as of yet", 'danger')
		return redirect(url_for('index'))
	cur1.close()
	cur.close()


class RegisterForm(Form):
	name = StringField('Name',[validators.Length(min=1, max = 50)])
	username  = StringField('Username',[validators.Length(min = 4 , max=25)])
	email  = StringField('Email', [validators.Length(min = 6, max = 50),validators.Email()])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm',message='Passwords do not match')
   	])
	confirm = PasswordField('Confirm Password') 


class DetailForm(Form):
	username = StringField('Username',[validators.Length(min = 4 , max=25)])
	gender = StringField('Gender',[validators.DataRequired()])
	date_of_birth  = StringField('Date of Birth',[validators.Length(min = 6, max = 50)])
	religion = StringField('Religion', [validators.Length(min = 3, max = 50)])
	mother_tongue = StringField('Mother Tongue',[validators.Length(min = 3, max = 50)])
	living_in_country = StringField('Living In',[validators.Length(min = 3, max = 50)]) 
	state = StringField('State',[validators.DataRequired()])
	city = StringField('City',[validators.DataRequired()])
	marital_status = StringField('Marital Status',[validators.DataRequired()])
	education_level = StringField('Education Level',[validators.DataRequired()])
	education_field = StringField('Education Field',[validators.DataRequired()])
	employed_in = StringField('Employed In',[validators.DataRequired()])
	employed_as = StringField('Employed As',[validators.DataRequired()])
	annual_income = StringField('Annual Income',[validators.DataRequired()])




@app.route('/user_details/form1',methods = ['GET','POST'])
def user_details():
	form = DetailForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		gender = form.gender.data
		date_of_birth = form.date_of_birth.data
		religion = form.religion.data
		mother_tongue = form.mother_tongue.data
		living_in_country = form.living_in_country.data
		state = form.state.data
		city = form.city.data
		marital_status = form.marital_status.data
		education_level = form.education_level.data
		education_field = form.education_field.data
		employed_in = form.employed_in.data
		employed_as = form.employed_as.data
		annual_income = form.annual_income.data

		cur  = mysql.connection.cursor()
		cur1 = mysql.connection.cursor()

		result = cur1.execute('SELECT * from users where username = %s',[username])

		if result > 0:
			data = cur1.fetchone()

			profile_id = data['id']

			cur.execute("INSERT INTO user_profile_details(profile_id,gender,date_of_birth,religion,mother_tongue,living_in_country,state,city,marital_status,education_level,education_field,employed_in,employed_as,annual_income) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(profile_id,gender,date_of_birth,religion,mother_tongue,living_in_country,state,city,marital_status,education_level,education_field,employed_in,employed_as,annual_income))


		#Commit to DB 
			mysql.connection.commit()


		#close connection
			cur.close()
			cur1.close()


			flash('You have completed the process of giving us your information.Now login to get on your Dashboard','success')
			return redirect(url_for('login'))
	return render_template('user_profile_details.html' ,form = form)


@app.route('/register', methods = ['GET','POST'])   
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		#Create a cursor 

		cur  = mysql.connection.cursor()

		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))


		#Commit to DB 
		mysql.connection.commit()


		#close connection
		cur.close()


		flash("You are now registered",'success')

		return redirect(url_for('user_details'))


	return render_template('register.html',form = form)



#User Login 
@app.route('/login', methods = ['GET','POST'])
def login():
   if request.method == 'POST':
   	 #get form fields
   	 username = request.form['username']
   	 password_candidate = request.form['password']

   	 #Create cursor
   	 cur = mysql.connection.cursor()

   	 #get user by username

   	 result = cur.execute("select * from users where username = %s ",[username]) 

   	 if result>0:
   	 	#get stored hash
   	 	data = cur.fetchone()
   	 	password = data['password']

   	 	#Compare the passwords 

   	 	if sha256_crypt.verify(password_candidate, password):
   	 		#passed
   	 		session['logged_in'] = True
   	 		session['username'] = username


   	 		flash('You have now logged in' , 'success')
   	 		return redirect(url_for('dashboard'))

   	 	else:
   	 		error = 'Invalid login'
   	 		return render_template('login.html', error=error) 
   	 	#close connection 
   	 	cur.close()



   	 else:
   	 	error = 'Username not found'
   	 	return render_template('login.html', error=error)

   return render_template('login.html')



   #Admin Login 
@app.route('/adminlogin' , methods = ['GET','POST'])
def adminlogin():
   	if request.method == 'POST':
   	 	#get form fields
   	 username = request.form['username']
   	 password_candidate = request.form['password']

   	 	#Create cursor
   	 cur = mysql.connection.cursor()

   		 #get user by username

   	 result = cur.execute("select * from admin where admin_username= %s ",[username]) 

   	 if result>0:
   	 		#get stored hash
   	 	data = cur.fetchone()
   	 	password = data['admin_password']

   	 		#Compare the passwords 

   	 	if password_candidate == password:  #possible error temporarily
   	 			#passed
   	 		session['admin_logged_in'] = True
   	 		session['username'] = username


   	 		flash('You have now logged in as Admin' , 'success')
   	 		return redirect(url_for('backend'))

   	 	else:
   	 		error = 'Invalid login'
   	 		return render_template('adminlogin.html', error=error)
   	 	cur.close()
   	 else:
   	 	error = 'Username not found'
   	 	return render_template('adminlogin.html', error=error)
   	return render_template('adminlogin.html')


#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args , **kwargs)
		else:
			flash('Unauthorized , Please log in' , 'danger')
			return redirect(url_for('login'))
	return wrap		


#check if admin logged in
def is_admin_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'admin_logged_in' in session:
			return f(*args , **kwargs)
		else:
			flash('Unauthorized , Please log in' , 'danger')
			return redirect(url_for('adminlogin'))
	return wrap		


#Logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

#dashboard
@app.route('/dashboard/')
@is_logged_in
def dashboard():

	#Create cursor
	cur = mysql.connection.cursor()
	cur1 = mysql.connection.cursor()
	cur2 = mysql.connection.cursor()
	cur3 = mysql.connection.cursor()
	cur4 = mysql.connection.cursor()
	cur5 = mysql.connection.cursor()
	cur6 = mysql.connection.cursor()
	cur7 = mysql.connection.cursor()


	#Get user information
	usrnm = session['username']
	result  = cur.execute('SELECT id,name,email,username,register_data from users where username = %s',[usrnm])
	result2 = cur2.execute('SELECT id from users where username = %s',[usrnm])
	result3 = cur3.execute('SELECT profile_id,email,age,marital_status,have_children,height,mother_tongue,physical_status,religion,education_level,education_field,employed_as,living_in_country,state,is_smoke,is_drink from Matrimony_Partner_Specification where profile_id = (SELECT id from users where username = %s)',[usrnm])
	result4 = cur4.execute("SELECT * from messages where target_id = (SELECT id from users where username = %s)",[usrnm])
	result7 = cur7.execute("SELECT id,username,name from users")
	lookup = cur7.fetchall()
	idd = cur2.fetchone()
	result1 = cur1.execute('SELECT gender,date_of_birth,religion,mother_tongue,living_in_country,state,city,marital_status,education_level,education_field,employed_in,employed_as,annual_income,photo FROM user_profile_details where profile_id = (SELECT id from users where username = %s)',[usrnm])
	users = cur.fetchall()
	user_d = cur1.fetchall()
	partner_spe = cur3.fetchone()
	messag = cur4.fetchall()
	yess  = messag
	yess1 = idd
	if result3 > 0:
		result5 = cur5.execute("SELECT * from user_profile_details where age=%s or marital_status=%s or height=%s or mother_tongue=%s or religion=%s or education_level=%s or education_field=%s or employed_as=%s or living_in_country=%s or state=%s or is_smoke=%s or is_drink=%s",[partner_spe['age'],partner_spe['marital_status'],partner_spe['height'],partner_spe['mother_tongue'],partner_spe['religion'],partner_spe['education_level'],partner_spe['education_field'],partner_spe['employed_as'],partner_spe['living_in_country'],partner_spe['state'],partner_spe['is_smoke'],partner_spe['is_drink']])
		yess = cur5.fetchall()
		result6 = cur6.execute("SELECT username from users where email = %s",[partner_spe['email']])
		yess1 = cur6.fetchone()


	
	 
	return render_template('dashboard.html',users = users , user_d = user_d , partner_spe = partner_spe , messag = messag , yess =  yess , yess1 = yess1, lookup = lookup)

	cur.close()
	cur1.close()
	cur2.close() 
	cur3.close()
	cur4.close()
	cur5.close()
	cur6.close()
	cur7.close()
	return render_template('dashboard.html')

# Admin dashboard or Backend

@app.route('/backend/')
@is_admin_logged_in
def backend():
	# Create cursor
	cur = mysql.connection.cursor()
	cur1 = mysql.connection.cursor()
	cur2 = mysql.connection.cursor()
	cur3 = mysql.connection.cursor()
	cur4 = mysql.connection.cursor()
	cur5 = mysql.connection.cursor()
	cur6 = mysql.connection.cursor()

	#Get  Users
	result  = cur.execute('SELECT id,name,email,username,register_data from users')
	admin_result = cur1.execute('SELECT admin_id,admin_username,admin_register_data from admin')
	faq = cur2.execute('SELECT faq_id,questions,answers from faqs')
	basicd = cur3.execute('SELECT * from user_profile_details')
	partner_sp_result = cur4.execute('SELECT * from Matrimony_Partner_Specification')
	report_result = cur5.execute("SELECT * from report")
	messsage_result = cur6.execute("SELECT * from messages")

	users = cur.fetchall()
	admin = cur1.fetchall() 
	faqs  = cur2.fetchall()
	user_profile_details = cur3.fetchall()
	partner_sp = cur4.fetchall()
	report = cur5.fetchall()
	messages = cur6.fetchall()
	  #Fetching in dictionary form 

	if  result >0 and admin_result > 0 and faq > 0 and basicd > 0 and partner_sp_result > 0:
		return render_template('backend.html' ,admin = admin,users = users, faqs = faqs , user_profile_details=user_profile_details , partner_sp = partner_sp , report = report,messages = messages)
	else:
		msg = 'No Users Found'
		return render_template('backend.html', msg = msg)

	#Close connection
	cur.close()		
	cur1.close()
	cur2.close()
	cur3.close()
	cur4.close()
	cur5.close()
	cur6.close()



@app.route('/delete_user' , methods = ['GET','POST'])
def delete_user():

	cur = mysql.connection.cursor()

	iid = request.form['id']

	
	k = cur.execute("DELETE from users where id = %s",[iid])
	
	mysql.connection.commit()

	cur.close()
	if k>0:
		flash("User deleted" , 'success')
	else:
		flash(" Entered User id doesnt exist", 'danger')


	return redirect(url_for('backend'))	

	





class PartnerForm(Form):
	email = StringField('Email')
	age = StringField('Age')
	marital_status = StringField('Marital Status')
	have_children  = StringField('Have Children')
	height = StringField('Height')
	mother_tongue = StringField('Mother Tongue')
	physical_status = StringField('Physical Status')
	religion = StringField('Religion')
	education_level = StringField('Education Level')
	education_field = StringField('Education Field')
	employed_as = StringField('Employed As')
	living_in_country = StringField('Living In',[validators.Length(min = 3, max = 50)]) 
	state = StringField('State')
	is_smoke = StringField('Smoking')
	is_drink = StringField('Drinking')


@app.route('/insert_partner_info', methods = ['GET','POST'])
@is_logged_in
def search():
	form = PartnerForm(request.form)
	if request.method =='POST' and form.validate():
	#get form fields
		email = form.email.data
		age = form.age.data
		marital_status = form.marital_status.data
		have_children = form.have_children.data
		height = form.height.data
		mother_tongue = form.mother_tongue.data
		physical_status = form.physical_status.data
		religion = form.religion.data
		education_level= form.education_level.data
		education_field = form.education_field.data
		employed_as = form.employed_as.data
		living_in_country = form.living_in_country.data
		state = form.state.data
		is_smoke = form.is_smoke.data
		is_drink = form.is_drink.data
   	 #Create cursor
		cur = mysql.connection.cursor()
		cur1 = mysql.connection.cursor()
		username = session['username']
		result1 = cur1.execute("SELECT id from users where username = %s",[username])
		idd = cur1.fetchone()
		profile_id = idd['id']
   	
		cur.execute("INSERT into Matrimony_Partner_Specification(profile_id,email,age,marital_status,have_children,height,mother_tongue,physical_status,religion,education_level,education_field,employed_as,living_in_country,state,is_smoke,is_drink) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(profile_id,email,age,marital_status,have_children,height,mother_tongue,physical_status,religion,education_level,education_field,employed_as,living_in_country,state,is_smoke,is_drink))
		mysql.connection.commit()
		cur.close()
		cur1.close()
		flash('You have successfully updated your choices','success')
		return redirect(url_for('dashboard'))
	return render_template('insert_partner_info.html',form = form)


@app.route('/update_partner_info', methods = ['GET','POST'])
@is_logged_in
def update_partner_info():
	form = PartnerForm(request.form)
	if request.method =='POST' and form.validate():
	#get form fields
		email = form.email.data
		age = form.age.data
		marital_status = form.marital_status.data
		have_children = form.have_children.data
		height = form.height.data
		mother_tongue = form.mother_tongue.data
		physical_status = form.physical_status.data
		religion = form.religion.data
		education_level= form.education_level.data
		education_field = form.education_field.data
		employed_as = form.employed_as.data
		living_in_country = form.living_in_country.data
		state = form.state.data
		is_smoke = form.is_smoke.data
		is_drink = form.is_drink.data
   	 #Create cursor
		cur = mysql.connection.cursor()
		cur1 = mysql.connection.cursor()
		username = session['username']
		result1 = cur1.execute("SELECT id from users where username = %s",[username])
		idd = cur1.fetchone()
		profile_id = idd['id']
   	
		cur.execute("UPDATE Matrimony_Partner_Specification SET  email = %s , age = %s ,marital_status = %s,have_children = %s,height = %s,mother_tongue = %s,physical_status = %s,religion = %s,education_level = %s,education_field = %s,employed_as = %s,living_in_country = %s,state = %s,is_smoke = %s,is_drink = %s where profile_id = %s",(email,age,marital_status,have_children,height,mother_tongue,physical_status,religion,education_level,education_field,employed_as,living_in_country,state,is_smoke,is_drink,profile_id))
		mysql.connection.commit()
		cur.close()
		cur1.close()
		flash('You have successfully updated your choices','success')
		return redirect(url_for('dashboard'))
	return render_template('update_partner_info.html',form = form)

# Message form class
class MessageForm(Form):

	rusername  = StringField("Receiver's Username",[validators.Length(min = 4 , max=25)])
	title = StringField('Title',[validators.Length(min=1, max = 200)])
	message = TextAreaField('Message',[validators.Length(min=1)])

#Message writing method
@app.route('/write_message',methods = ['GET','POST'])
@is_logged_in
def write_message():
	form = MessageForm(request.form)
	if request.method == 'POST' and form.validate():
		rusername = form.rusername.data
		title = form.title.data
		message = form.message.data
		susername = session['username']


		#Create cursor
		cur = mysql.connection.cursor()
		cur1 = mysql.connection.cursor()
		cur2 = mysql.connection.cursor()

		result1 =  cur1.execute("SELECT id from users where username = %s",[rusername])
		result2 = cur2.execute("SELECT id from users where username = %s",[susername])
		if result1 > 0 and result2 > 0:
			idd = cur1.fetchone()
			idd1 = cur2.fetchone()
			tid = idd['id']
			sid = idd1['id']

		#execute statement 
			cur.execute("INSERT into messages(susername,source_id,target_id,title,message) values(%s,%s,%s,%s,%s)",(susername,sid,tid,title,message))
		#Commit statement
			mysql.connection.commit()

	    #Close cursors
			cur.close()
			cur1.close()
			cur2.close()
			flash('Message Sent','success')
			return redirect(url_for('dashboard'))
	return render_template('write_message.html', form = form)



#The partner finalization form
class FinalizeForm(Form):
	t_username = StringField('Partner Username',[validators.Length(min=1, max = 50)])
	status  = StringField('Status')
	marriage_date = StringField('Marriage Date')
	remarks = TextAreaField('Remarks')
# The partner finalization method
@app.route('/finalize', methods = ['GET','POST'])
@is_logged_in
def finalize():
	form = FinalizeForm(request.form)
	if request.method == 'POST' and form.validate():
		t_username = form.t_username.data
		status = form.status.data
		marriage_date = form.marriage_date.data
		remarks = form.remarks.data
		s_username =session['username']

		#Create a cursor
		cur = mysql.connection.cursor()
		cur1 = mysql.connection.cursor()
		cur2 = mysql.connection.cursor()

		result1 = cur1.execute("SELECT id from users where username = %s",[s_username])
		result2 = cur2.execute("SELECT id from users where username = %s",[t_username])
		if result1 > 0:
			idd = cur1.fetchone()
			s_id = idd['id']
		if result2 > 0:
			iddd = cur2.fetchone()
			t_id = iddd['id']

		cur.execute("INSERT into report(report_source_id,report_target_id,status,marriage_date,remarks) values(%s,%s,%s,%s,%s)",(s_id,t_id,status,marriage_date,remarks))

		#Commit

		mysql.connection.commit()

		cur.close()
		cur1.close()
		cur2.close()
		flash('Congratulations! Wish You a happy married life', 'success')
		return redirect(url_for('dashboard'))
	return render_template('finalize.html', form = form)


@app.route('/delete_FAQ' , methods = ['GET','POST'])
def delete_FAQ():

	cur = mysql.connection.cursor();

	iid = request.form['faq_id']

	k = cur.execute("DELETE from faqs where faq_id = %s",[iid])

	mysql.connection.commit()

	cur.close()
	if k>0:
		flash("Question successfully Deleted by Admin",'success')
	else:
		flash("Entered FAQ id doesnt exist", 'danger')

	return redirect(url_for('backend'))


@app.route('/delete_message' , methods = ['GET','POST'])
def delete_message():

	cur = mysql.connection.cursor()

	iid = request.form['id']

	
	k = cur.execute("DELETE from messages where msgid = %s",[iid])
	
	mysql.connection.commit()

	cur.close()
	if k>0:
		flash("Message deleted" , 'success')
	else:
		flash(" Entered Message id doesnt exist", 'danger')


	return redirect(url_for('backend'))

@app.route('/delete_report' , methods = ['GET','POST'])
def delete_report():

	cur = mysql.connection.cursor()

	iid = request.form['report_source_id']

	
	k = cur.execute("DELETE from report where report_source_id = %s",[iid])
	
	mysql.connection.commit()

	cur.close()
	if k>0:
		flash("Admin deleted invalid report" , 'success')
	else:
		flash("Entered report source id doesnt exist", 'danger')


	return redirect(url_for('backend'))


@app.route('/<name>/<location>')
def pdf_template(name,location):
	rendered = render_template('pdf_template.html', name = name , location = location)
	pdf = pdfkit.from_string(rendered,False)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename = output.pdf' 


	return response

@app.route('/upload', methods = ['POST'])
def upload():
	file = request.files['inputFile']
	filename = file.filename
	file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
	#return redirect(url_for('uploaded_file',filename=filename))
	usrnm = session['username']
	cur = mysql.connection.cursor()

	cur.execute("UPDATE user_profile_details set photo = %s WHERE profile_id = (SELECT id from users where username = %s)",(filename,usrnm)) 

	mysql.connection.commit()

	cur.close()

	flash("Successful upload",'success')
	return redirect(url_for('dashboard'))


@app.route('/view_upload',methods = ['POST'])
def view_upload():
	usrnm = session['username']
	cur = mysql.connection.cursor();

	result = cur.execute("SELECT photo from user_profile_details where profile_id = (SELECT id from users where username = %s)",[usrnm])
	filename = cur.fetchone();

	cur.close()

	return redirect(url_for('uploaded_file',filename=filename['photo']))



@app.route('/uploads/<filename>')
def uploaded_file(filename):



	return render_template('yo.html',filename = filename)


@app.route('/delete_info')
def delete_info():

	usrnm = session['username']
	cur = mysql.connection.cursor()

	cur.execute("DELETE from Matrimony_Partner_Specification where profile_id = (SELECT id from users where username = %s)",[usrnm])

	mysql.connection.commit()

	cur.close()

	flash("Successfully deleted partner specifications",'success')
	return redirect(url_for('dashboard'))



@app.route('/delete_basic')
def delete_basic():

	usrnm = session['username']
	cur = mysql.connection.cursor()


	cur.execute("DELETE from user_profile_details where profile_id = ( SELECT id from users where username = %s)",[usrnm])

	mysql.connection.commit()

	cur.close()


	flash("Successfully deleted user details",'success')
	return redirect(url_for('dashboard'))

if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug = True)
