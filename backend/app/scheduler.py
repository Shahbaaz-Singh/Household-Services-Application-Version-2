from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks import send_daily_reminders, send_monthly_report

def start_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        lambda: send_daily_reminders.delay(),
        CronTrigger(hour=12, minute=30, timezone="UTC"), 
        id="daily_reminders",
        replace_existing=True
    )


    scheduler.add_job(
        lambda: send_monthly_report.delay(), 
        CronTrigger(day=1, hour=18, minute=30, timezone="UTC"), 
        id="monthly_report",
        replace_existing=True
    )

    scheduler.start()