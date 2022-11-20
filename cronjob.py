# Package Scheduler.
from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
from notify_new_listing import schedule_job
from fundamental_analysis import funda_analysis_job

# Create an instance of scheduler and add function.
# scheduler1 = BlockingScheduler(timezone="Asia/Kathmandu")
scheduler2 = BlockingScheduler(timezone="Asia/Kathmandu")


# scheduler1.add_job(schedule_job, "cron", day="*", hour="7", minute=30)
scheduler2.add_job(funda_analysis_job, "cron", day_of_week="sun", hour="7", minute=30)
# scheduler.add_job(schedule_job, "interval", seconds=120)

# scheduler1.start()
scheduler2.start()
