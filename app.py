from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# USERS DATABASE (temporary)
users = {
    'admin': ['admin', 'admin'],
    'cashier': ['cashier', 'cashier']
}



# HOME (LOGIN PAGE)
@app.route('/')
def home():
    return render_template('login.html')

# LOGIN FUNCTION
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Check if username exists
        if username in users:
            # Check password
            if password == users[username][0]:

                # Check role
                if users[username][1] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif users[username][1] == 'cashier':
                    return redirect(url_for('cashier_dashboard'))

        return "Invalid username or password!"

    return render_template('login.html')


# ADMIN DASHBOARD
@app.route('/admin')
def admin_dashboard():
    return render_template('dashboard.html')


# CASHIER DASHBOARD
@app.route('/cashier')
def cashier_dashboard():
    return render_template('dashboard.html')

@app.route('/customer')
def customer_dashboard():
    return render_template('customer.html')


# LOGOUT (optional pero useful)
@app.route('/logout')
def logout():
    return redirect(url_for('home'))



# RUN APP
if __name__ == '__main__':
    app.run(debug=True)


    

    