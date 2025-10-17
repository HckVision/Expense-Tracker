from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'hckvision_secret_key_2024'

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['hckvision_expenses']
expenses_collection = db['expenses']

# Static credentials
USERNAME = 'gnana'
PASSWORD = 'Gnana@1313'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('login.html', error=True)
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html', page='expenses')

@app.route('/expenses')
def expenses():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    expenses_list = list(expenses_collection.find().sort('date', 1))
    total = sum(expense['amount'] for expense in expenses_list)
    
    return render_template('expenses.html', expenses=expenses_list, total=total)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        amount = float(request.form.get('amount'))
        date = request.form.get('date')
        
        expense = {
            'title': title,
            'description': description,
            'amount': amount,
            'date': date,
            'created_at': datetime.now()
        }
        
        expenses_collection.insert_one(expense)
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    return render_template('add.html')

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    expenses_list = list(expenses_collection.find().sort('date', -1))
    total = sum(expense['amount'] for expense in expenses_list)
    
    return render_template('history.html', expenses=expenses_list, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Vercel serverless function handler
app = app

if __name__ == '__main__':
    app.run(debug=True)