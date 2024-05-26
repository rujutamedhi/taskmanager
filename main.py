from flask import Flask, render_template, request, redirect, url_for,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime, timedelta
import schedule
import time
from threading import Thread
from flask_mail import Message
import json
from datetime import datetime, timedelta, timezone

local_server =True
app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
    
with open("C:\\projects\\netflix\\config.json") as c:
     params=json.load(c)["params"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:rujutamedhi%4004@localhost/taskmanager'
app.config.update(
   MAIL_SERVER='Smtp.gmail.com',
   MAIL_PORT='465',
   MAIL_USE_SSL=True,
   MAIL_USERNAME=params['gmail-user'],
   MAIL_PASSWORD=params['gmail-password'],
   MAIL_DEFAULT_SENDER=params['gmail-user']

)
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phno = db.Column(db.String(20))
    password = db.Column(db.String(100))

# Create the database tables
    with app.app_context():

      db.create_all()
class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    email = db.Column(db.String(100), db.ForeignKey('users.email'))
    user = db.relationship('User', backref='data')
    type=db.Column(db.String(100))
     
    def __init__(self, title, date, description, email,type):
        self.title = title
        self.date = date
        self.description = description
        self.email = email
        self.type=type

    def __repr__(self):
        return '<Data %r>' % self.title


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
    
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/complete', methods=['GET', 'POST'])
def comp():
    
    print("heyyyyaaaaa")
    if request.method=='GET':
        type='complete'
        tasks = Data.query.filter_by(email=email,type='complete').all()
        return render_template('comp.html',tasks=tasks)
    
    

@app.route('/view', methods=['GET', 'POST'])
def view():
    if request.method=='GET':
        tasks = Data.query.filter_by(email=email,type='view').all()
        return render_template('view.html',tasks=tasks)



@app.route('/completed/<int:task_id>', methods=['GET'])
def completed(task_id):
    print("holaaaa")
    global task
    task = Data.query.get_or_404(task_id)
    task.type = 'complete'
    db.session.commit()
    tasks = Data.query.filter_by(email=email, type='view').all()
    return render_template('view.html', tasks=tasks)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        print("test")
        global title,date,description
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        # email = request.form['email']
        print(email)
        print(title)
        print(date)
        print(description)
        # Create a new user instance
        new_user = Data(title=title, date=date, description=description,email=email,type='view')
        
        # Add the new user to the database session
        db.session.add(new_user)
        db.session.commit()
        
    return render_template('create.html',task=None)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    if task_id == 0:
        task = None  # For creating a new task
    else:
        task = Data.query.get_or_404(task_id)

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        
        # Check if task exists, then update, else create new entry
        if task:
            task.title = title
            task.date = date
            task.description = description
        else:
            task = Data(title=title, date=date, description=description,email=email,type='view')
            db.session.add(task)
        
        db.session.commit()
        return redirect(url_for('view'))  # Redirect to view page or any other page

    return render_template('create.html', task=task)

@app.route('/delete/<int:task_id>', methods=['GET','POST'])
def delete(task_id):
     
    task = Data.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('view'))
@app.route('/Logout', methods=['GET'])
def logout():
    confirm = session.get('confirm')
    print(f'Confirm value: {confirm}')  # Debugging: print the value of confirm to check if it's being received
    session.pop('confirm', None)  # Clear the confirm session variable

    if confirm == 'yes':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('main'))

@app.route('/confirm-logout', methods=['POST'])
def confirm_logout():
    data = request.json
    confirm = data.get('confirm')
    session['confirm'] = 'yes' if confirm else 'no'  # Store the confirm value in the session
    return jsonify({'status': 'success'})




@app.route('/success')
def success():
    return 'User added successfully!'

@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global email
        # Get the email and password from the form
        email = request.form['email']
        password = request.form['password']
        
        # Query the database to check if the email and password match
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            last_task = Data.query.order_by(Data.id.desc()).first()

    # Calculate the next ID
            task_id = last_task.id + 1 if last_task else 1
            
            # If a user with the provided email and password exists, redirect to index page
            return render_template('main.html',task_id=task_id)
        else:
            # If no matching user found, redirect back to the login page
            return redirect(url_for('login'))

    # Render the login page template for GET requests
    return render_template('signin.html')

@app.route("/signup",methods=['GET', 'POST'])
def signup():
    print("test0")
    print(request.method)
    if request.method == 'POST':
        print("test")
        global email
        name = request.form['name']
        email = request.form['email']
        phno = request.form['phno']
        password = request.form['password']
        
        # Create a new user instance
        new_user = User(name=name, email=email, phno=phno, password=password)
        
        # Add the new user to the database session
        db.session.add(new_user)
        
        # Commit the session to the database
        db.session.commit()
        
        
    return render_template('signup.html',params=params)
mail = Mail(app)

def send_reminder_emails():
    with app.app_context():
        current_time = datetime.now(timezone.utc)
        tasks_to_remind = Data.query.filter(Data.date == current_time.date() + timedelta(days=1)).all()
        for task in tasks_to_remind:
            user = User.query.filter_by(email=task.email).first()
            if user:
                msg = Message('Task Reminder', recipients=[user.email])
                msg.body = f"Don't forget to complete your task: {task.title}"
                mail.send(msg)

def schedule_reminder_emails():
    schedule.every().day.at("21:34").do(send_reminder_emails)

schedule_reminder_emails()

def scheduler_thread():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    scheduler_thread = Thread(target=scheduler_thread)
    scheduler_thread.start()
    app.run(debug=True)