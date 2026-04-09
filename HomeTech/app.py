from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# CUSTOMERS DATABASE
customers = [
    {'id': '0101', 'name': 'Juan', 'contact': '09223456789', 'address': 'Tubigon'},
    {'id': '0000', 'name': 'Jhonavie', 'contact': '09220987654', 'address': 'Clarin'},
    {'id': '0001', 'name': 'Angel', 'contact': '09123456789', 'address': 'Dagohoy'},
    {'id': '0002', 'name': 'Maria', 'contact': '09123452459', 'address': 'Danao'},
    {'id': '0003', 'name': 'John', 'contact': '09123456789', 'address': 'Mactan'},
    {'id': '0004', 'name': 'Jane', 'contact': '09123456789', 'address': 'Bantayan'},
    {'id': '0005', 'name': 'Heart', 'contact': '09958840258', 'address': 'Nahud'},
]

# PRODUCTS DATABASE
products = [
    {'id': '1001', 'name': 'Laptop', 'category': 'Electronics', 'price': 45000, 'stock': 'Available', 'status': 'active'},
    {'id': '1010', 'name': 'Television', 'category': 'Electronics', 'price': 32000, 'stock': 'Available', 'status': 'active'},
    {'id': '1234', 'name': 'Refrigerator', 'category': 'Appliances', 'price': 23000, 'stock': 'Available', 'status': 'active'},
    {'id': '1235', 'name': 'Washing Machine', 'category': 'Appliances', 'price': 18000, 'stock': 'Available', 'status': 'active'},
    {'id': '1236', 'name': 'Microwave Oven', 'category': 'Appliances', 'price': 5000, 'stock': 'Not Available', 'status': 'active'},
    {'id': '1237', 'name': 'Blender', 'category': 'Appliances', 'price': 2000, 'stock': 'Available', 'status': 'active'},
    {'id': '1238', 'name': 'Toaster', 'category': 'Appliances', 'price': 1500, 'stock': 'Available', 'status': 'active'},
]

# SALES DATABASE
sales = [
     {'id': 1, 'product': 'Television', 'quantity': 1, 'total': 32000, 'date': '2024-06-01', 'customer': 'Jhonavie'},
]

# BILLING DATABASE
bills = [
    {'id': 1, 'customer_id': '0000', 'customer': 'Jhonavie', 'amount': 32000, 'date': '2024-06-01', 'status': 'Paid', 'description': 'Television purchase'},
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
                    error = "Invalid number format for ID or Price!"

        elif 'search_product' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

        elif 'clear_form' in request.form:
            return redirect(url_for('products_management'))

    # Filter products based on search
    filtered_products = products
    if search_query:
        filtered_products = [p for p in products if search_query in str(p['id']) or search_query in p['name'].lower() or search_query in p['category'].lower()]

    return render_template('Products.html', products=filtered_products, error=error, search_query=search_query, form_data=form_data)


@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    global products
    product_id = str(product_id)
    # Find product name before deletion for logging
    product = next((p for p in products if str(p['id']) == product_id), None)
    product_name = product['name'] if product else 'Unknown'
    
    products[:] = [p for p in products if str(p['id']) != product_id]
    log_activity('product', f'Product deleted: {product_name} (ID: {product_id})', 'admin')
    return redirect(url_for('products_management'))


@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    global products
    product_id = str(product_id)
    print(f"Edit product route called with product_id: {product_id}, method: {request.method}")
    product = next((p for p in products if str(p['id']) == product_id), None)

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
            product['stock'] = stock
            product['status'] = status
            log_activity('product', f'Product updated: {product_name} (ID: {product_id})', 'admin')
            print(f"Product {product_id} updated successfully")
            return redirect(url_for('products_management'))
        except ValueError as e:
            error = "Invalid number format for Price!"
            print(f"Value error: {e}")
            return render_template('Products.html', products=products, error=error, edit_product=product)

    print(f"Showing edit form for product {product_id}")
    return render_template('Products.html', products=products, edit_product=product)


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
            payment_type = request.form.get('payment_type', '').strip()

            if not product or not customer or not date or not quantity or not total or not payment_type:
                error = 'All fields are required.'
            else:
                try:
                    quantity = int(quantity)

                    matched_product = next((p for p in products if p['name'].lower() == product.lower()), None)
                    if not matched_product:
                        error = 'Selected product not found.'
                    else:
                        price = float(matched_product['price'])
                        total_price = price * quantity
                        sale_data = {
                            'id': new_id,
                            'product': matched_product['name'],
                            'quantity': quantity,
                            'total': total_price,
                            'date': date,
                            'customer': customer,
                            'payment_type': payment_type
                        }
                        if payment_type == 'installment':
                            down_payment = request.form.get('down_payment', '0').strip()
                            installment_months = request.form.get('installment_months', '').strip()
                            if not down_payment:
                                error = 'Down payment is required for installment.'
                            elif not installment_months:
                                error = 'Please enter how many months the customer will pay.'
                            else:
                                down_payment = float(down_payment)
                                installment_months = int(installment_months)
                                if down_payment >= total_price:
                                    error = 'Down payment cannot be equal to or greater than total amount.'
                                elif installment_months < 1:
                                    error = 'Installment months must be at least 1.'
                                else:
                                    monthly_payment = round((total_price - down_payment) / installment_months, 2)
                                    sale_data.update({
                                        'down_payment': down_payment,
                                        'monthly_payment': monthly_payment,
                                        'installment_terms': installment_months,
                                        'remaining_balance': round(total_price - down_payment, 2)
                                    })
                                    # Create bill for down payment
                                    bill_id = max([b['id'] for b in bills], default=0) + 1
                                    bills.append({
                                        'id': bill_id,
                                        'customer': customer,
                                        'amount': down_payment,
                                        'date': date,
                                        'status': 'Paid',
                                        'description': f'Down payment for {matched_product["name"]} installment',
                                        'type': 'Down Payment'
                                    })
                                    log_activity('billing', f'Down payment recorded: ₱{down_payment} for {customer}', 'cashier')
                        elif payment_type == 'cash':
                            # Create bill for full payment
                            bill_id = max([b['id'] for b in bills], default=0) + 1
                            bills.append({
                                'id': bill_id,
                                'customer': customer,
                                'amount': total_price,
                                'date': date,
                                'status': 'Paid',
                                'description': f'Full payment for {matched_product["name"]}',
                                'type': 'Full Payment'
                            })
                            log_activity('billing', f'Full payment recorded: ₱{total_price} for {customer}', 'cashier')
                        if not error:
                            sales.append(sale_data)
                            log_activity('sales', f'Sale recorded: {matched_product["name"]} ({quantity}) to {customer} - {payment_type}', 'cashier')
                            return redirect(url_for('sales_management'))
                except ValueError:
                    error = 'Invalid number format for quantity or down payment.'
        elif 'search_sale' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()
    filtered_sales = sales
    if search_query:
        filtered_sales = [s for s in sales if search_query in s['product'].lower() or search_query in s['customer'].lower() or search_query in s['date']]
    return render_template('Sales.html', sales=filtered_sales, error=error, search_query=search_query, products=products)
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

    # Calculate billing summary
    total_bills = len(bills)
    paid_bills = len([b for b in bills if b['status'] == 'Paid'])
    unpaid_bills = len([b for b in bills if b['status'] == 'Unpaid'])
    pending_bills = len([b for b in bills if b['status'] == 'Pending'])
    total_collected = sum(b['amount'] for b in bills if b['status'] == 'Paid')
    outstanding_amount = sum(b['amount'] for b in bills if b['status'] != 'Paid')

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
                    bills.append({
                        'id': new_id,
                        'customer': customer,
                        'amount': amount,
                        'date': date,
                        'status': status,
                        'description': description,
                        'type': 'Manual'
                    })
                    log_activity('billing', f'Bill created for {customer}: ₱{amount}', 'cashier')
                    return redirect(url_for('billing_management'))
                except ValueError:
                    error = 'Amount must be numeric.'

        elif 'search_bill' in request.form:
            search_query = request.form.get('searchInput', '').strip().lower()

    filtered_bills = bills
    if search_query:
        filtered_bills = [b for b in bills if search_query in b['customer'].lower() 
                          or search_query in b['description'].lower() 
                          or search_query in b['date']]

    return render_template('billing.html',
                          bills=filtered_bills,
                          error=error,
                          search_query=search_query,
                          total_bills=total_bills,
                          paid_bills=paid_bills,
                          unpaid_bills=unpaid_bills,
                          pending_bills=pending_bills,
                          total_collected=total_collected,
                          outstanding_amount=outstanding_amount,
                          bills_json=json.dumps(filtered_bills))


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
        log_activity('billing', f'Bill status updated for {bill["customer"]} (ID {bill_id}) to {status}', 'cashier')
    return redirect(url_for('billing_management'))


@app.route('/generate_installment_invoices')
def generate_installment_invoices():
    global sales, bills
    from datetime import datetime, timedelta

    generated_count = 0

    for sale in sales:
        if sale.get('payment_type') == 'installment':
            customer = sale['customer']
            monthly_payment = sale.get('monthly_payment', 0)
            installment_terms = sale.get('installment_terms', 12)
            sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')

            # Check how many installment bills already exist for this sale
            existing_installments = [b for b in bills if
                                   b.get('type') == 'Installment' and
                                   b['customer'] == customer and
                                   f"Installment payment for {sale['product']}" in b['description']]

            # Generate remaining installment bills
            for month in range(len(existing_installments) + 1, installment_terms + 1):
                bill_date = sale_date + timedelta(days=30 * month)  # Approximate monthly

                bill_id = max([b['id'] for b in bills], default=0) + 1
                bills.append({
                    'id': bill_id,
                    'customer': customer,
                    'amount': monthly_payment,
                    'date': bill_date.strftime('%Y-%m-%d'),
                    'status': 'Unpaid',
                    'description': f'Installment payment {month}/{installment_terms} for {sale["product"]}',
                    'type': 'Installment',
                    'sale_id': sale['id']
                })
                generated_count += 1

    log_activity('billing', f'Generated {generated_count} installment invoices', 'cashier')
    return redirect(url_for('billing_management'))


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

