from flask import Blueprint, request, jsonify, current_app, send_from_directory, send_file
from app.models import db, Customer, Professional, Admin, Service, ServiceRequest
from sqlalchemy import or_, and_
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime, timedelta
from app import cache, limiter


main = Blueprint('main', __name__)

#-----------------------------------------------------------------------------------------------#

#---------------
# Home Page API
#---------------

@main.route('/api/home', methods=['GET'])
@cache.cached(timeout=300)
def home():
    return jsonify({
        "title": "Welcome to Household Services",
        "description": "Your one-stop solution for your household needs",
        "actions": [
            {"label": "Admin Login", "url": "/admin/login"},
            {"label": "Professional Login", "url": "/professional/login"},
            {"label": "Customer Login", "url": "/customer/login"},
            {"label": "Register as a new user", "url": "/register"}
        ]
    })

#-----------------------------------------------------------------------------------------------#

#------------------------------------------
# Registation API and Documents Upload API
#------------------------------------------

@main.route('/api/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    location = request.form.get('location')
    pin_code = request.form.get('pin_code')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    address = request.form.get('address')

    document_filename = None
    if role == 'professional':
        document_file = request.files.get('documents')
        
        if not document_file:
            return jsonify({"success": False, "message": "Please upload required documents."}), 400

        allowed_extensions = ['.pdf', '.txt', '.png', '.jpg', '.jpeg', '.xlsx', '.xls']
        
        if document_file.filename.endswith(tuple(allowed_extensions)):
            document_filename = secure_filename(document_file.filename)
            upload_folder = current_app.config.get('UPLOAD_FOLDER', './uploads')
            os.makedirs(upload_folder, exist_ok=True)
            document_path = os.path.join(upload_folder, document_filename)
            document_file.save(document_path)
        else:
            return jsonify({"success": False, "message": "Invalid file type."}), 400

    existing_user = None

    if role == 'customer':
        existing_user = Customer.query.filter(
            (Customer.username == username) |
            (Customer.email == email) |
            (Customer.phone_number == phone_number)
        ).first()
    elif role == 'professional':
        existing_user = Professional.query.filter(
            (Professional.username == username) |
            (Professional.email == email) |
            (Professional.phone_number == phone_number)
        ).first()

    if existing_user:
        return jsonify({"success": False, "message": "Username, email or phone number already exists."}), 400

    if role == 'professional':
        expertise = request.form.get('expertise')
        documents = request.form.get('documents')
        new_user = Professional(
            username=username,
            expertise=expertise,
            location=location,
            pin_code=pin_code,
            phone_number=phone_number,
            address=address,
            email=email,
            documents=document_filename
        )
    else:
        new_user = Customer(
            username=username,
            location=location,
            pin_code=pin_code,
            phone_number=phone_number,
            address=address,
            email=email
        )

    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Registration successful!"}), 201

@main.route('/api/documents/<path:filename>', methods=['GET'])
def get_document(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', './uploads')
    secure_name = secure_filename(filename)
    full_path = os.path.join(upload_folder, secure_name)

    full_path = os.path.abspath(full_path)

    if secure_name != filename:
        return jsonify({"error": "Invalid filename"}), 400

    if not os.path.exists(full_path):
        return jsonify({"error": f"File not found at {full_path}"}), 404

    return send_from_directory(os.path.abspath(upload_folder), secure_name)

#------------------------------------------------------------------------------------------------------------#

#-------------------
# Refresh Token API
#-------------------

@main.route('/api/refresh-token', methods=['POST'])
@limiter.limit("3 per minute") 
def refresh_token():
    try:
        refresh_token = request.json.get('refreshToken')
        if not refresh_token:
            return jsonify({"success": False, "message": "Refresh token is required."}), 400

        user_identity = get_jwt_identity()
        if not user_identity:
            return jsonify({"success": False, "message": "Invalid refresh token."}), 401

        new_access_token = create_access_token(identity=user_identity)

        return jsonify({"success": True, "token": new_access_token}), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

#------------------------------------------------------------------------------------------------------------#
#------------
# Admin APIs
#------------

@main.route('/api/admin/login', methods=['GET', 'POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    
    if admin and admin.check_password(password):
        access_token = create_access_token(identity=json.dumps({"id": admin.id, "role": "admin"}))
        return jsonify({"success": True, "access_token": access_token}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401
    
@main.route('/api/admin/dashboard', methods=['GET'])
@cache.cached(timeout=120)
@limiter.limit("5 per minute")
@jwt_required()
def admin_dashboard():
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        customers = Customer.query.all()
        professionals = Professional.query.all()
        services = Service.query.all()

        active_customers = sum(1 for c in customers if not c.is_blocked)
        blocked_customers = sum(1 for c in customers if c.is_blocked)
        active_professionals = sum(1 for p in professionals if p.is_approved)
        inactive_professionals = sum(1 for p in professionals if not p.is_approved)
        total_services = len(services)      

        dashboard_data = {
            "active_customers": active_customers,
            "blocked_customers": blocked_customers,
            "active_professionals": active_professionals,
            "inactive_professionals": inactive_professionals,
            "total_services": total_services
        }

        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
@main.route('/api/admin/export_closed_requests', methods=['POST'])
@jwt_required()
def trigger_export():
    from app.tasks import export_closed_requests_task  
    try:
        current_user = get_jwt_identity()
        user_data = json.loads(current_user)
        admin_id = user_data["id"]
        if user_data["role"] != "admin":
            return jsonify({"success": False, "message": "Unauthorized access."}), 403
        
        admin = Admin.query.get(admin_id)

        admin_email = admin.email
        admin_phone = None
        admin_gchat_webhook = None

        task = export_closed_requests_task.apply_async(args=[admin_email, admin_phone, admin_gchat_webhook])

        return jsonify({"successf": True, "message": "Export job started.", "task_id": task.id}), 202

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
   
@main.route('/api/admin/customer_info', methods=['GET'])
@jwt_required()
def api_customer_info():
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        search_query = request.args.get('search_query', '')
        
        if search_query:
            customers = Customer.query.filter(Customer.username.ilike(f'%{search_query}%')).all()
        else:
            customers = Customer.query.all()
        
        customers_data = [{
            'id': customer.id,
            'username': customer.username,
            'location': customer.location,
            'pin_code': customer.pin_code,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'address': customer.address,
            'is_blocked': customer.is_blocked
        } for customer in customers]
        
        return jsonify(customers_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
@main.route('/api/admin/block_user/<int:id>', methods=['POST'])
@jwt_required()
def api_block_user(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        customer = Customer.query.get_or_404(id)
        customer.is_blocked = True
        db.session.commit()
        
        return jsonify({'message': f'{customer.username} has been blocked'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/unblock_user/<int:id>', methods=['POST'])
@jwt_required()
def api_unblock_user(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        customer = Customer.query.get_or_404(id)
        customer.is_blocked = False
        db.session.commit()
        
        return jsonify({'message': f'{customer.username} has been unblocked'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/professional_info', methods=['GET'])
@jwt_required()
def api_professional_info():
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        search_query = request.args.get('search_query', '')
        
        if search_query:
            professionals = Professional.query.filter(Professional.username.ilike(f'%{search_query}%')).all()
        else:
            professionals = Professional.query.all()
        
        professionals_data = [{
            'id': professional.id,
            'username': professional.username,
            'expertise': professional.expertise,
            'rating': professional.rating,
            'num_reviews': professional.num_reviews,
            'location': professional.location,
            'pin_code': professional.pin_code,
            'phone_number': professional.phone_number,
            'email': professional.email,
            'address': professional.address,
            'documents': professional.documents,
            'is_approved': professional.is_approved
        } for professional in professionals]
        
        return jsonify(professionals_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
@main.route('/api/admin/approve/<int:id>', methods=['POST'])
@jwt_required()
def api_approve_user(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        professional = Professional.query.get_or_404(id)
        professional.is_approved = True
        db.session.commit()
        
        return jsonify({'message': f'{professional.username} has been approved'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/unapprove/<int:id>', methods=['POST'])
@jwt_required()
def api_unapprove_user(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        professional = Professional.query.get_or_404(id)
        professional.is_approved = False
        db.session.commit()
        
        return jsonify({'message': f'{professional.username} has been blocked'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/services', methods=['GET'])
@jwt_required()
def api_services():
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        services = Service.query.all()
        
        services_data = [{
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'time_required': service.time_required,
            'description': service.description,
            'field_of_service': service.field_of_service
        } for service in services]
        
        return jsonify(services_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/create_service', methods=['POST'])
@jwt_required()
def api_create_service():
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        data = request.json
        name = data.get('name')
        price = data.get('price')
        time_required = data.get('time_required')
        description = data.get('description')
        field_of_service = data.get('field_of_service')
        
        service = Service(
            name=name, 
            price=price, 
            time_required=time_required, 
            description=description, 
            field_of_service=field_of_service
        )
        db.session.add(service)
        db.session.commit()
        
        return jsonify({'message': 'Service created successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/update_service/<int:id>', methods=['POST'])
@jwt_required()
def api_update_service(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        service = Service.query.get_or_404(id)
        
        data = request.json
        service.name = data.get('name')
        service.price = data.get('price')
        service.time_required = data.get('time_required')
        service.description = data.get('description')
        
        db.session.commit()
        
        return jsonify({'message': 'Service updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/admin/delete_service/<int:id>', methods=['POST'])
@jwt_required()
def api_delete_service(id):
    try:
        user = json.loads(get_jwt_identity())

        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        service = Service.query.get_or_404(id)

        if service.requests:
            return jsonify({'error': 'Cannot delete service with active requests'}), 400

        db.session.delete(service)
        db.session.commit()
        
        return jsonify({'message': 'Service deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

    
@main.route('/api/admin/logout', methods=['POST'])
@jwt_required()
def api_admin_logout():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "admin":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

#--------------------------------------------------------------------------------------------------------------#


#---------------
# Customer APIs
#---------------        

@main.route('/api/customer/login', methods=['POST'])
def customer_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    customer = Customer.query.filter_by(username=username).first()

    if not customer:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

    if not customer.check_password(password):
        return jsonify({"success": False, "message": "Invalid username or password."}), 401
    
    if customer.is_blocked:
        return jsonify({"success": False, "message": "You are blocked. Please contact admin."}), 403

    access_token = create_access_token(identity=json.dumps({"id": customer.id, "role": "customer"}))
    return jsonify({"success": True, "access_token": access_token}), 200

@main.route('/api/customer/dashboard', methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("10 per minute")  
@jwt_required()
def customer_dashboard():
    try:
        user = json.loads(get_jwt_identity())
        customer_id = user["id"]
        role = user["role"]
        if role != "customer":
            return jsonify({"success": False, "message": "Unauthorized access."}), 403

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"success": False, "message": "Customer not found."}), 404
        
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid token data."}), 401

    service_requests = ServiceRequest.query.filter_by(customer_id = customer.id).all()

    services = Service.query.all() or []

    pending = sum(1 for s in service_requests if s.service_status == "pending" or s.service_status == "rejected")
    accepted = sum(1 for s in service_requests if s.service_status == "accepted")
    in_progress = sum(1 for s in service_requests if s.service_status == "in_progress")
    completed = sum(1 for s in service_requests if s.service_status == "completed")
    closed = sum(1 for s in service_requests if s.service_status == "closed")

    dashboard_data = {
        "customer_info": {
            "username": customer.username,
            "location": customer.location,
            "pin_code": customer.pin_code,
            "phone_number": customer.phone_number,
            "email": customer.email,
            "address": customer.address,
        },
        "service_requests": {
            "pending": pending,
            "accepted": accepted,
            "in_progress": in_progress,
            "completed": completed,
            "closed": closed,
        },
        "services_available": [{"id": service.id, "name": service.name} for service in services],
    }

    return jsonify({"success": True, "data": dashboard_data}), 200

@main.route('/api/customer/create_request', methods=['GET'])
@jwt_required()
def api_create_request():
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

    services = Service.query.all()
    locations = Customer.query.with_entities(Customer.location).union(Professional.query.with_entities(Professional.location)).distinct().all()
    pincodes = Customer.query.with_entities(Customer.pin_code).union(Professional.query.with_entities(Professional.pin_code)).distinct().all()
    
    services_data = [{
        'id': service.id,
        'name': service.name,
        'price': service.price,
        'time_required': service.time_required,
        'description': service.description,
        'field_of_service': service.field_of_service
    } for service in services]
    
    return jsonify({
        'services': services_data,
        'locations': [location[0] for location in locations],
        'pincodes': [pincode[0] for pincode in pincodes]
    }), 200


@main.route('/api/customer/search_services', methods=['GET'])
@jwt_required()
def api_search_services():
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

    query = request.args.get('search_query', '')
    results = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
        
    results_data = [{
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'time_required': service.time_required,
            'description': service.description,
            'field_of_service': service.field_of_service
        } for service in results]
        
    return jsonify({
            'results': results_data
        }), 200

@main.route('/api/customer/request_service', methods=['POST'])
@jwt_required()
def api_request_service():
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
    data = request.json
    service = Service.query.get(data['service_id'])
    new_request = ServiceRequest(
        customer_id=user['id'],
        service_id=data['service_id'],
        date_of_request=datetime.utcnow() + timedelta(hours=5, minutes=30),
        location=data['location'],
        pin_code=data['pin_code'],
        field_of_service=service.field_of_service
    )
    db.session.add(new_request)
    db.session.commit()
    
    return jsonify({'message': 'Service request submitted successfully!'}), 201

@main.route('/api/customer/service_requests', methods=['GET'])
@jwt_required()
def api_service_requests():
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

    service_requests = ServiceRequest.query.filter(
        ServiceRequest.customer_id == user['id'],
        ServiceRequest.service_status != 'closed'
    ).all()
    
    requests_data = []
    for req in service_requests:
        service_data = {
            'id': req.associated_service.id,
            'name': req.associated_service.name,
            'price': req.associated_service.price,
            'time_required': req.associated_service.time_required,
            'description': req.associated_service.description,
            'field_of_service': req.associated_service.field_of_service
        } if req.associated_service else None
        
        professional_data = {
            'id': req.assigned_professional.id,
            'username': req.assigned_professional.username,
            'rating': req.assigned_professional.rating,
            'num_reviews': req.assigned_professional.num_reviews,
            'phone_number': req.assigned_professional.phone_number,
            'email': req.assigned_professional.email
        } if req.assigned_professional else None
        
        request_data = {
            'id': req.id,
            'customer_id': req.customer_id,
            'service_id': req.service_id,
            'date_of_request': req.date_of_request.isoformat() if req.date_of_request else None,
            'date_of_acceptance': req.date_of_acceptance.isoformat() if req.date_of_acceptance else None,
            'date_of_completion': req.date_of_completion.isoformat() if req.date_of_completion else None,
            'location': req.location,
            'pin_code': req.pin_code,
            'service_status': req.service_status,
            'field_of_service': req.field_of_service,
            'remarks': req.remarks,
            'associated_service': service_data,
            'assigned_professional': professional_data
        }
        requests_data.append(request_data)
    
    return jsonify({
        'service_requests': requests_data
    }), 200


@main.route('/api/customer/update_request/<int:id>', methods=['PUT'])
@jwt_required()
def api_update_request(id):
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
    request_service = ServiceRequest.query.get_or_404(id)
    request_service.remarks = request.json.get('remarks')
    db.session.commit()
    
    return jsonify({'message': 'Service request updated'}), 200

@main.route('/api/customer/close_request/<int:id>', methods=['POST'])
@jwt_required()
def api_close_request(id):
    try:
        user = json.loads(get_jwt_identity())
        
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

    service_request = ServiceRequest.query.get_or_404(id)
    service_request.service_status = 'closed'
    professional = service_request.assigned_professional
    
    rating = request.json.get('rating')
    if rating and 1 <= rating <= 5 and professional:
        new_total_rating = (professional.rating * professional.num_reviews + rating) / (professional.num_reviews + 1)
        professional.rating = round(new_total_rating, 2)
        professional.num_reviews += 1
    
    db.session.commit()
    return jsonify({'message': 'Service request closed.'}), 200

@main.route('/api/customer/logout', methods=['POST'])
@jwt_required()
def api_customer_logout():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "customer":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

#--------------------------------------------------------------------------------------------------------------------------------#

@main.route('/api/professional/login', methods=['POST'])
def professional_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    professional = Professional.query.filter_by(username=username).first()

    if not professional:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

    if not professional.check_password(password):
        return jsonify({"success": False, "message": "Invalid username or password."}), 401

    if not professional.is_approved:
        return jsonify({"success": False, "message": "Your account is not approved yet."}), 403

    access_token = create_access_token(identity=json.dumps({"id": professional.id, "role": "professional"}))

    return jsonify({"success": True, "access_token": access_token}), 200

@main.route('/api/professional/dashboard', methods=['GET'])
@cache.cached(timeout=60)
@limiter.limit("10 per minute")  
@jwt_required()
def professional_dashboard():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        rejected_requests_list = professional.rejected_requests.split(',') if professional.rejected_requests else []
        accepted_requests_list = professional.accepted_requests.split(',') if professional.accepted_requests else []
        completed_requests_list = professional.completed_requests.split(',') if professional.completed_requests else []
        
        num_rejected = len(rejected_requests_list) if rejected_requests_list else 0
        num_completed = len(completed_requests_list) if completed_requests_list else 0

        accepted_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['accepted'])).all()
        accepted_requests = [req for req in accepted_requests if req.id in map(int, accepted_requests_list)]
        num_accepted = len(accepted_requests)
        
        in_progress_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['in_progress'])).all()
        in_progress_requests = [req for req in in_progress_requests if req.id in map(int, accepted_requests_list)]
        num_in_progress = len(in_progress_requests)
        
        rejected_requests = [int(id) for id in rejected_requests_list if id]
        pending_requests = ServiceRequest.query.filter(
            ServiceRequest.service_status.in_(['pending', 'rejected']),
            ServiceRequest.field_of_service == professional.expertise
        ).all()
        
        filtered_pending = []
        for req in pending_requests:
            if req.id not in rejected_requests:
                if (not req.location and not req.pin_code) or \
                   (req.location == professional.location or req.pin_code == professional.pin_code):
                    filtered_pending.append(req)
        
        num_pending = len(filtered_pending)
        
        dashboard_data = {
            "professional_info": {
                "username": professional.username,
                "rating": professional.rating,
                "num_reviews": professional.num_reviews,
                "expertise": professional.expertise,
                "is_approved": professional.is_approved
            },
            "request_stats": {
                "rejected": num_rejected,
                "accepted": num_accepted,
                "completed": num_completed,
                "pending": num_pending,
                "in_progress": num_in_progress
            }
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

from flask import current_app
@main.route('/api/professional/export_pending_requests', methods=['POST'])
@jwt_required()
def trigger_professional_export():
    from app.tasks import export_pending_requests_task  
    try:
        current_user = get_jwt_identity()
        user_data = json.loads(current_user)
        
        if user_data["role"] != "professional":
            return jsonify({"success": False, "message": "Unauthorized access."}), 403

        professional = Professional.query.get(user_data["id"])
        if not professional or not professional.is_approved:
            return jsonify({"success": False, "message": "Unauthorized or unapproved professional."}), 403
        
        professional_email = professional.email
        
        task = export_pending_requests_task.apply_async(args=[professional.id, professional_email])

        return jsonify({"success": True, "message": "Export job started.", "task_id": task.id}), 202

    except Exception as e:
        current_app.logger.error(f"Error in export_pending_requests: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@main.route('/api/professional/download_export', methods=['GET'])
@jwt_required()
def download_professional_export():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
    BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  
    EXPORT_DIR = os.path.join(BACKEND_DIR, "exports") 
    try:
        user_data = json.loads(get_jwt_identity())

        if user_data["role"] != "professional":
            return jsonify({"success": False, "message": "Unauthorized access."}), 403

        professional_id = user_data["id"]
        professional = Professional.query.get(professional_id)

        if not professional or not professional.is_approved:
            return jsonify({"success": False, "message": "Unauthorized or unapproved professional."}), 403

        files = [
            os.path.join(EXPORT_DIR, f) 
            for f in os.listdir(EXPORT_DIR) 
            if f.startswith(f"requests_summary_{professional_id}_") and f.endswith(".csv")
        ]

        if not files:
            return jsonify({"success": False, "message": "No exported CSV found."}), 404

        latest_file = os.path.join(EXPORT_DIR, files[-1])

        return send_file(latest_file, as_attachment=True)

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@main.route('/api/professional/pending_requests', methods=['GET'])
@jwt_required()
def api_pending_requests():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
            
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        rejected_requests = professional.rejected_requests.split(',') if professional.rejected_requests else []
        rejected_requests = [int(id) for id in rejected_requests if id]
        
        pending_requests = ServiceRequest.query.filter(
            ServiceRequest.service_status.in_(['pending', 'rejected']),
            ServiceRequest.field_of_service == professional.expertise,
            or_(
                and_(
                    ServiceRequest.location.in_([None, ""]),
                    ServiceRequest.pin_code.in_([None, ""])
                ),
                or_(
                    ServiceRequest.location == professional.location,
                    ServiceRequest.pin_code == professional.pin_code
                )
            )
        ).all()
        
        pending_requests_data = []
        for req in pending_requests:
            if req.id not in rejected_requests:
                service_data = {
                    'id': req.associated_service.id,
                    'name': req.associated_service.name,
                    'price': req.associated_service.price,
                    'time_required': req.associated_service.time_required,
                    'description': req.associated_service.description,
                    'field_of_service': req.associated_service.field_of_service
                } if req.associated_service else None
                
                customer_data = {
                    'username': req.requesting_customer.username
                } if req.requesting_customer else None
                
                request_data = {
                    'id': req.id,
                    'service_status': req.service_status,
                    'associated_service': service_data,
                    'requesting_customer': customer_data
                }
                pending_requests_data.append(request_data)
        
        return jsonify({'pending_requests': pending_requests_data}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/professional/accept_service/<int:id>', methods=['POST'])
@jwt_required()
def api_accept_service_request(id):
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
            
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        request_service = ServiceRequest.query.get_or_404(id)
        
        request_service.service_status = 'accepted'
        request_service.date_of_acceptance = datetime.utcnow() + timedelta(hours=5, minutes=30)
        request_service.professional_id = professional.id
        
        accepted_requests_list = professional.accepted_requests.split(',') if professional.accepted_requests else []
        
        if str(id) not in accepted_requests_list:
            accepted_requests_list.append(str(id))
        
        professional.accepted_requests = ','.join(accepted_requests_list)
        
        db.session.commit()
        
        return jsonify({'message': 'You have accepted the service request.'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/professional/reject_service/<int:id>', methods=['POST'])
@jwt_required()
def api_reject_service_request(id):
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
            
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        request_service = ServiceRequest.query.get_or_404(id)
        
        request_service.service_status = 'rejected'
        
        rejected_requests = professional.rejected_requests.split(',') if professional.rejected_requests else []
        
        if str(id) not in rejected_requests:
            rejected_requests.append(str(id))
        
        professional.rejected_requests = ','.join(rejected_requests)
        
        db.session.commit()
        
        return jsonify({'message': 'You have rejected the service request.'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
@main.route('/api/professional/accepted_requests', methods=['GET'])
@jwt_required()
def api_accepted_requests():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
            
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        accepted_requests = ServiceRequest.query.filter(
            ServiceRequest.service_status.in_(['accepted', 'in_progress']),
            ServiceRequest.professional_id == professional.id
        ).all()
        
        customer_data_list = []
        for req in accepted_requests:
            customer = Customer.query.get(req.customer_id)
            
            service_data = {
                'id': req.associated_service.id,
                'name': req.associated_service.name,
                'price': req.associated_service.price,
                'time_required': req.associated_service.time_required,
                'description': req.associated_service.description,
                'field_of_service': req.associated_service.field_of_service
            } if req.associated_service else None
            
            customer_info = {
                'username': customer.username,
                'location': customer.location,
                'pin_code': customer.pin_code,
                'phone_number': customer.phone_number,
                'email': customer.email,
                'address': customer.address
            } if customer else None
            
            request_data = {
                'id': req.id,
                'service_status': req.service_status,
                'remarks': req.remarks,
                'date_of_request': req.date_of_request.isoformat() if req.date_of_request else None,
                'date_of_acceptance': req.date_of_acceptance.isoformat() if req.date_of_acceptance else None,
                'associated_service': service_data,
                'customer': customer_info
            }
            customer_data_list.append(request_data)
        
        return jsonify({'accepted_requests': customer_data_list}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@main.route('/api/professional/update_service_status/<int:id>', methods=['POST'])
@jwt_required()
def api_update_service_status(id):
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
            
        professional = Professional.query.get(user["id"])
        
        if not professional or not professional.is_approved:
            return jsonify({'error': 'Unauthorized or unapproved professional'}), 403
            
        request_service = ServiceRequest.query.get_or_404(id)
        
        new_status = request.json.get('service_status')
        request_service.service_status = new_status
        
        if new_status == 'completed':
            request_service.date_of_completion = datetime.utcnow() + timedelta(hours=5, minutes=30)
            
            completed_requests_list = professional.completed_requests.split(',') if professional.completed_requests else []
            
            if str(id) not in completed_requests_list:
                completed_requests_list.append(str(id))
            
            professional.completed_requests = ','.join(completed_requests_list)
        
        db.session.commit()
        
        return jsonify({'message': 'Service status updated successfully.'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
@main.route('/api/professional/logout', methods=['POST'])
@jwt_required()
def api_professional_logout():
    try:
        user = json.loads(get_jwt_identity())
        if user["role"] != "professional":
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500
    
#--------------------------------------------------------------------------------------------------------------------------------------#
