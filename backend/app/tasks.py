from app import celery, create_app, make_celery
from app.models import Professional, Customer, ServiceRequest
from flask import render_template
from app.utils import send_email
from celery.schedules import crontab
from datetime import datetime
import csv
import os
from celery import shared_task

EXPORT_DIR = "exports"

app = create_app()
celery = make_celery(app)

#---------------------------------------------------------------------------------------------------------------------------------------#

#---------------------
# Daily Reminder Task
#---------------------

@celery.task(name="send_daily_reminders")
def send_daily_reminders():

    with app.app_context():
        print(f"Starting daily reminders task at {datetime.now()}")

        professionals = Professional.query.filter_by(is_approved=True).all()
        reminder_count = 0

        for professional in professionals:
            if professional.has_pending_requests:
                message = (
                    f"Dear {professional.username}, you have pending service requests awaiting your attention. "
                    f"Please log in to your account to review, accept, or decline them at your earliest convenience. "
                    f"Thank you for your prompt action."
                )

                success = False
                
                success = send_email(
                    professional.email,
                    "Pending Service Requests Reminder",
                    message
                    )

                if success:
                    reminder_count += 1

        print(f"Daily reminders task completed. Sent {reminder_count} reminders.")
        return f"Sent {reminder_count} reminders"

#-----------------------------------------------------------------------------------------------------------------------------------#

#---------------------
# Monthly Report Task
#---------------------

@celery.task(name="send_monthly_report")  
def send_monthly_report():

    with app.app_context():
        print(f"Starting Monthly Report Task at {datetime.now()}")

        customers = Customer.query.all()
        report_count = 0

        for customer in customers:
            services_requested = ServiceRequest.query.filter_by(customer_id=customer.id).count()
            services_closed = ServiceRequest.query.filter_by(customer_id=customer.id, service_status="closed").count()
            
            html_content = render_template(
                "monthly_report.html",
                customer=customer,
                services_requested=services_requested,
                services_closed=services_closed,
                date=datetime.utcnow().strftime("%B %Y"),
            )

            subject = f"Monthly Activity Report - {datetime.utcnow().strftime('%B %Y')}"
            success = send_email(
                recipient=customer.email,
                subject=subject,
                body="Please find your monthly activity report attached.",
                html_content=html_content
            )

            if success:
                report_count += 1
        
        print(f"Monthly Report Task completed. Sent {report_count} reports.")
        return f"Sent {report_count} reports."

#-------------------------------------------------------------------------------------------------------------------------#

#-----------------
# CSV Export Task
#-----------------

@shared_task
def export_pending_requests_task(professional_id, professional_email):
    with app.app_context():
        try:
            print(f"Starting CSV export task for professional {professional_id} at {datetime.now()}")
            os.makedirs(EXPORT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            file_name = f"requests_summary_{professional_id}_{timestamp}.csv"
            file_path = os.path.join(EXPORT_DIR, file_name)

            professional = Professional.query.get(professional_id)
            if not professional or not professional.is_approved:
                return {"success": False, "error": "Unauthorized or unapproved professional."}

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

            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Service ID", "Customer ID", "Date of Request", "Remarks", "Status"])
                for req in filtered_pending + accepted_requests + in_progress_requests:
                    writer.writerow([req.id, req.customer_id, req.date_of_request, req.remarks, req.service_status])

                writer.writerow([])
                writer.writerow(["Summary"])
                writer.writerow(["Total Pending Requests", num_pending])
                writer.writerow(["Total Accepted Requests", num_accepted])
                writer.writerow(["Total In-Progress Requests", num_in_progress])
                writer.writerow(["Total Completed Requests", num_completed])
                writer.writerow(["Total Rejected Requests", num_rejected])

            subject = "Your Service Requests Summary Export is Complete Successfully"
            message = f"Hello {professional.username},\n\nYour service requests summary CSV is successfully complete and can be downloaded from your dashboard."

            if professional_email:
                send_email(professional_email, subject, message)

            return {"success": True, "file_path": file_path}
        
        except Exception as e:
            return {"success": False, "error": str(e)}

#-------------------------------------------------------------------------------------------------------------------------#