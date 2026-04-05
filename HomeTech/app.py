from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# CUSTOMERS DATABASE
customers = [
    {'id': 'I Love You', 'name': 'Jhonavie', 'contact': '0922 Ikaw nay bahala sa pito', 'address': 'Sa imong Heart', 'status': 'Active'},
]

# PRODUCTS DATABASE
products = [
    {'id': 'Gwapa', 'name': 'Wala pa', 'category': 'Secret', 'price': 150, 'stock': 'Mangita pa hatagi ko bi', 'status': 'Minyo na'},
]

# SALES DATABASE
sales = [
     {'id': 1, 'product': 'Wala pa', 'quantity': 1, 'total': 150, 'date': '2024-06-01', 'customer': 'Jhonavie'},
]

# BILLING DATABASE
bills = [
    {'id': 1, 'customer': 'Jhonavie', 'amount': 150, 'date': '2024-06-01', 'status': 'Paid', 'description': 'Sale of Wala pa'},
]

# RECENT ACTIVITIES DATABASE
activities = []

# USERS DATABASE (temporary)
users = {
    'admin': {'password': 'admin', 'role': 'admin'},
    'cashier': {'password': 'cashier', 'role': 'cashier'}
}

# ACTIVITY LOGGING FUNCTION
def log_activity(activity_type, description, user="System"):
    global activities
    from datetime import datetime
    activity = {
        'id': len(activities) + 1,
        'type': activity_type,
        'description': description,
        'user': user,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    activities.insert(0, activity)  # Add to beginning of list
    # Keep only last 20 activities
    if len(activities) > 20:
        activities = activities[:20]



# HOME (LOGIN PAGE)
@app.route('/')
def home():
    return render_template('login.html')

# LOGIN FUNCTION
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '').strip()

        # Check if username exists
        if username in users:
            # Check password
            if password == users[username]['password']:
                # Log successful login
                log_activity('login', f'User {username} logged in', username)

                # Check role and redirect accordingly
                role = users[username]['role']
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'cashier':
                    return redirect(url_for('cashier_dashboard'))
            else:
                error = "Invalid username or password!"
        else:
            error = "Invalid username or password!"

    return render_template('login.html', error=error)


def get_dashboard_metrics():
    total_customers = len(customers)
    total_sales = sum(s['total'] for s in sales)  # Connected to real sales dataset
    total_products = len(products)  # Connected to products dataset
    total_products_sold = sum(s['quantity'] for s in sales)  # Total quantity of products sold
    pending_payments = sum(b['amount'] for b in bills if b['status'] == 'Unpaid')  # Connected to real billing dataset

    # Billing metrics
    total_bills = len(bills)
    paid_bills = len([b for b in bills if b['status'] == 'Paid'])
    unpaid_bills = len([b for b in bills if b['status'] == 'Unpaid'])
    total_revenue = sum(b['amount'] for b in bills if b['status'] == 'Paid')

    return total_customers, total_sales, total_products, total_products_sold, pending_payments, total_bills, paid_bills, unpaid_bills, total_revenue


# ADMIN DASHBOARD
@app.route('/admin')
def admin_dashboard():
    total_customers, total_sales, total_products, total_products_sold, pending_payments, total_bills, paid_bills, unpaid_bills, total_revenue = get_dashboard_metrics()
    recent_activities = activities[:10]  # Show last 10 activities
    recent_bills = bills[-5:]  # Show last 5 bills
    return render_template('dashboard.html',
                           total_customers=total_customers,
                           total_sales=total_sales,
                           total_products=total_products,
                           total_products_sold=total_products_sold,
                           pending_payments=pending_payments,
                           total_bills=total_bills,
                           paid_bills=paid_bills,
                           unpaid_bills=unpaid_bills,
                           total_revenue=total_revenue,
                           recent_activities=recent_activities,
                           recent_bills=recent_bills)


# CASHIER DASHBOARD
@app.route('/cashier')
def cashier_dashboard():
    total_customers, total_sales, total_products, total_products_sold, pending_payments, total_bills, paid_bills, unpaid_bills, total_revenue = get_dashboard_metrics()
    recent_activities = activities[:10]  # Show last 10 activities
    recent_bills = bills[-5:]  # Show last 5 bills
    return render_template('dashboard.html',
                           total_customers=total_customers,
                           total_sales=total_sales,
                           total_products=total_products,
                           total_products_sold=total_products_sold,
                           pending_payments=pending_payments,
                           total_bills=total_bills,
                           paid_bills=paid_bills,
                           unpaid_bills=unpaid_bills,
                           total_revenue=total_revenue,
                           recent_activities=recent_activities,
                           recent_bills=recent_bills)


@app.route('/customer_management', methods=['POST', 'GET'])
def customer_management():
    global customers
    error = None
    search_query = ''
    form_data = None

    if request.method == 'POST':
        if 'save_customer' in request.form:
            customer_id = request.form.get('customerId', '').strip()
            customer_name = request.form.get('customerName', '').strip()
            contact = request.form.get('contactNo', '').strip()
            address = request.form.get('address', '').strip()
            status = request.form.get('status', 'Active')

            if not customer_id or not customer_name or not contact:
                error = "Customer ID, Name, and Contact are required!"
            else:
                # Check if customer already exists
                existing = [c for c in customers if c['id'] == customer_id]
                if existing:
                    error = "Customer ID already exists!"
                else:
                    customers.append({
                        'id': customer_id,
                        'name': customer_name,
                        'contact': contact,
                        'address': address,
                        'status': status
                    })
                    log_activity('customer', f'New customer added: {customer_name} (ID: {customer_id})', 'admin')
                    return redirect(url_for('customer_management'))

        elif 'search_customer' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

        elif 'clear_form' in request.form:
            return redirect(url_for('customer_management'))

    # Do not mutate global customers on search filter.
    filtered_customers = customers
    if search_query:
        filtered_customers = [c for c in customers if search_query in c['id'].lower() or search_query in c['name'].lower()]

    return render_template('customer.html', customers=filtered_customers, error=error, search_query=search_query, form_data=form_data)

@app.route('/delete_customer/<customer_id>')
def delete_customer(customer_id):
    global customers
    # Find customer name before deletion for logging
    customer = next((c for c in customers if c['id'] == customer_id), None)
    customer_name = customer['name'] if customer else 'Unknown'
    
    customers[:] = [c for c in customers if c['id'] != customer_id]
    log_activity('customer', f'Customer deleted: {customer_name} (ID: {customer_id})', 'admin')
    return redirect(url_for('customer_management'))


# PRODUCTS MANAGEMENT
@app.route('/products', methods=['POST', 'GET'])
def products_management():
    global products
    error = None
    search_query = ''
    form_data = None

    print(f"Products route called with method: {request.method}")

    if request.method == 'POST':
        print(f"POST data: {request.form}")
        if 'save_product' in request.form:
            product_id = request.form.get('productId', '').strip()
            product_name = request.form.get('productName', '').strip()
            category = request.form.get('category', '').strip()
            price = request.form.get('price', '').strip()
            stock = request.form.get('stock', '').strip()
            status = request.form.get('status', 'active')

            if not product_id or not product_name or not category or not price or not stock:
                error = "All fields are required!"
            else:
                try:
                    product_id = int(product_id)
                    price = float(price)
                    stock = int(stock)

                    # Check if product already exists
                    existing = [p for p in products if p['id'] == product_id]
                    if existing:
                        error = "Product ID already exists!"
                    else:
                        products.append({
                            'id': product_id,
                            'name': product_name,
                            'category': category,
                            'price': price,
                            'stock': stock,
                            'status': status
                        })
                        log_activity('product', f'New product added: {product_name} (ID: {product_id})', 'admin')
                        return redirect(url_for('products_management'))
                except ValueError:
                    error = "Invalid number format for ID, Price, or Stock!"

        elif 'search_product' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

        elif 'clear_form' in request.form:
            return redirect(url_for('products_management'))

    # Filter products based on search
    filtered_products = products
    if search_query:
        filtered_products = [p for p in products if search_query in str(p['id']) or search_query in p['name'].lower() or search_query in p['category'].lower()]

    return render_template('Products.html', products=filtered_products, error=error, search_query=search_query, form_data=form_data)


# SALES MANAGEMENT
@app.route('/sales', methods=['GET', 'POST'])
def sales_management():
    global sales
    error = None
    search_query = ''

    if request.method == 'POST':
        if 'add_sale' in request.form:
            new_id = max([s['id'] for s in sales], default=0) + 1
            product = request.form.get('product', '').strip()
            customer = request.form.get('customer', '').strip()
            date = request.form.get('date', '').strip()
            quantity = request.form.get('quantity', '').strip()
            total = request.form.get('total', '').strip()

            if not product or not customer or not date or not quantity or not total:
                error = 'All fields are required.'
            else:
                try:
                    quantity = int(quantity)
                    total = float(total)
                    sales.append({'id': new_id, 'product': product, 'quantity': quantity, 'total': total, 'date': date, 'customer': customer})
                    log_activity('sales', f'Sale recorded: {product} ({quantity}) to {customer}', 'cashier')
                    return redirect(url_for('sales_management'))
                except ValueError:
                    error = 'Quantity must be integer and total must be numeric.'

        elif 'search_sale' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

    filtered_sales = sales
    if search_query:
        filtered_sales = [s for s in sales if search_query in s['product'].lower() or search_query in s['customer'].lower() or search_query in s['date']]

    return render_template('Sales.html', sales=filtered_sales, error=error, search_query=search_query)


@app.route('/delete_sale/<int:sale_id>')
def delete_sale(sale_id):
    global sales
    sale = next((s for s in sales if s['id'] == sale_id), None)
    sales[:] = [s for s in sales if s['id'] != sale_id]
    if sale:
        log_activity('sales', f'Sale deleted: {sale["product"]} (ID {sale_id})', 'cashier')
    return redirect(url_for('sales_management'))


# BILLING MANAGEMENT
@app.route('/billing', methods=['GET', 'POST'])
def billing_management():
    global bills
    error = None
    search_query = ''

    if request.method == 'POST':
        if 'add_bill' in request.form:
            new_id = max([b['id'] for b in bills], default=0) + 1
            customer = request.form.get('customer', '').strip()
            amount = request.form.get('amount', '').strip()
            date = request.form.get('date', '').strip()
            status = request.form.get('status', 'Unpaid')
            description = request.form.get('description', '').strip()

            if not customer or not amount or not date:
                error = 'Customer, Amount, and Date are required.'
            else:
                try:
                    amount = float(amount)
                    bills.append({'id': new_id, 'customer': customer, 'amount': amount, 'date': date, 'status': status, 'description': description})
                    log_activity('billing', f'Bill created for {customer}: ${amount}', 'cashier')
                    return redirect(url_for('billing_management'))
                except ValueError:
                    error = 'Amount must be numeric.'

        elif 'search_bill' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

    filtered_bills = bills
    if search_query:
        filtered_bills = [b for b in bills if search_query in b['customer'].lower() or search_query in b['description'].lower() or search_query in b['date']]

    return render_template('billing.html', bills=filtered_bills, error=error, search_query=search_query)


@app.route('/delete_bill/<int:bill_id>')
def delete_bill(bill_id):
    global bills
    bill = next((b for b in bills if b['id'] == bill_id), None)
    bills[:] = [b for b in bills if b['id'] != bill_id]
    if bill:
        log_activity('billing', f'Bill deleted for {bill["customer"]} (ID {bill_id})', 'cashier')
    return redirect(url_for('billing_management'))


@app.route('/update_bill_status/<int:bill_id>/<status>')
def update_bill_status(bill_id, status):
    global bills
    bill = next((b for b in bills if b['id'] == bill_id), None)
    if bill:
        bill['status'] = status
        log_activity('billing', f'Bill status updated to {status} for {bill["customer"]} (ID {bill_id})', 'cashier')
    return redirect(url_for('billing_management'))


@app.route('/delete_product/<int:product_id>')
def delete_product(product_id):
    global products
    # Find product name before deletion for logging
    product = next((p for p in products if p['id'] == product_id), None)
    product_name = product['name'] if product else 'Unknown'
    
    products[:] = [p for p in products if p['id'] != product_id]
    log_activity('product', f'Product deleted: {product_name} (ID: {product_id})', 'admin')
    return redirect(url_for('products_management'))


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    global products
    print(f"Edit product route called with product_id: {product_id}, method: {request.method}")
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        print(f"Product {product_id} not found")
        return "Product not found", 404

    if request.method == 'POST':
        print(f"POST data for edit: {request.form}")
        product_name = request.form.get('productName', '').strip()
        category = request.form.get('category', '').strip()
        price = request.form.get('price', '').strip()
        stock = request.form.get('stock', '').strip()
        status = request.form.get('status', 'active')

        if not product_name or not category or not price or not stock:
            error = "All fields are required!"
            print(f"Validation error: {error}")
            return render_template('Products.html', products=products, error=error, edit_product=product)

        try:
            product['name'] = product_name
            product['category'] = category
            product['price'] = float(price)
            product['stock'] = int(stock)
            product['status'] = status
            log_activity('product', f'Product updated: {product_name} (ID: {product_id})', 'admin')
            print(f"Product {product_id} updated successfully")
            return redirect(url_for('products_management'))
        except ValueError as e:
            error = "Invalid number format for Price or Stock!"
            print(f"Value error: {e}")
            return render_template('Products.html', products=products, error=error, edit_product=product)

    print(f"Showing edit form for product {product_id}")
    return render_template('Products.html', products=products, edit_product=product)


# LOGOUT (optional pero useful)
@app.route('/logout')
def logout():
    return redirect(url_for('home'))



# RUN APP
if __name__ == '__main__':
    # Add some initial activities for demonstration
    log_activity('system', 'System initialized', 'System')
    log_activity('product', 'Initial products loaded', 'System')
    log_activity('customer', 'Customer database initialized', 'System')
    app.run(debug=True)


    

    