# Package Scheduler.
from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
from notify_new_listing import schedule_job
from fundamental_analysis import funda_analysis_job

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler(timezone="Asia/Kathmandu")


scheduler.add_job(schedule_job, "cron", day="*", hour="7", minute=30)
scheduler.add_job(schedule_job, "cron", day="sat,sun", hour="7", minute=30)
# scheduler.add_job(schedule_job, "interval", seconds=120)

scheduler.start()