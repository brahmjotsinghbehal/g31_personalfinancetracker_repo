from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'a'

DATABASE = "expense_tracker.db"  # SQLite database file



#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/register', methods=['POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        account = query_db('SELECT * FROM register WHERE username = ?', (username,), one=True)
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        else:
            conn = get_db()
            conn.execute('INSERT INTO register (username, email, password) VALUES (?, ?, ?)', (username, email, password))
            conn.commit()
            msg = 'You have successfully registered!'
            return redirect('/signin')

    return render_template('signup.html', msg=msg)

@app.route("/signin")
def signin():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        account = query_db('SELECT * FROM register WHERE username = ? AND password = ?', (username, password), one=True)
        
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect('/home')
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/home")
def user_home():
    return render_template('home.html')

@app.route("/add")
def adding():
    return render_template('add.html')

@app.route('/addexpense', methods=['POST'])
def addexpense():
    if 'loggedin' not in session:
        return redirect('/signin')

    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']

    conn = get_db()
    conn.execute('INSERT INTO expenses (userid, date, expensename, amount, paymode, category) VALUES (?, ?, ?, ?, ?, ?)',
                 (session['id'], date, expensename, amount, paymode, category))
    conn.commit()
    
    return redirect("/display")

@app.route("/display")
def display():
    if 'loggedin' not in session:
        return redirect('/signin')

    expenses = query_db('SELECT * FROM expenses WHERE userid = ? ORDER BY date DESC', (session['id'],))
    return render_template('display.html', expense=expenses)

@app.route('/delete/<int:id>')
def delete(id):
    if 'loggedin' not in session:
        return redirect('/signin')

    conn = get_db()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    return redirect("/display")

@app.route('/edit/<int:id>')
def edit(id):
    if 'loggedin' not in session:
        return redirect('/signin')

    expense = query_db('SELECT * FROM expenses WHERE id = ?', (id,), one=True)
    return render_template('edit.html', expenses=expense)

@app.route("/limit")
def limit():
    return redirect('/limitn')

@app.route("/limitnum", methods=['POST'])
def limitnum():
    if request.method == "POST":
        number = request.form['number']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO limits (userid, limitss) VALUES (?, ?)', (session['id'], number))
        conn.commit()
        conn.close()
        return redirect('/limitn')

@app.route("/limitn")
def limitn():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT limitss FROM limits ORDER BY id DESC LIMIT 1')
    x = cursor.fetchone()
    conn.close()

    if x:
        s = x[0]
    else:
        s = "No limit set"

    return render_template("limit.html", y=s)


@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if 'loggedin' not in session:
        return redirect('/signin')

    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']

    conn = get_db()
    conn.execute('UPDATE expenses SET date = ?, expensename = ?, amount = ?, paymode = ?, category = ? WHERE id = ?',
                 (date, expensename, amount, paymode, category, id))
    conn.commit()
    return redirect("/display")

@app.route("/today")
def today():
    if 'loggedin' not in session:
        return redirect('/signin')

    expenses = query_db('SELECT * FROM expenses WHERE userid = ? AND date = DATE("now") ORDER BY date DESC', (session['id'],))
    return render_template('today.html', expense=expenses)

@app.route("/month")
def month():
    if 'loggedin' not in session:
        return redirect('/signin')

    expenses = query_db('SELECT * FROM expenses WHERE userid = ? AND strftime("%m", date) = strftime("%m", "now") ORDER BY date DESC', (session['id'],))
    return render_template('today.html', expense=expenses)

@app.route("/year")
def year():
    if 'loggedin' not in session:
        return redirect('/signin')

    expenses = query_db('SELECT * FROM expenses WHERE userid = ? AND strftime("%Y", date) = strftime("%Y", "now") ORDER BY date DESC', (session['id'],))
    return render_template('today.html', expense=expenses)

# Get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db




@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to execute queries
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

if __name__ == "__main__":
    app.run(debug=True)
