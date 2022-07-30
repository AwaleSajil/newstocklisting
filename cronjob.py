# Package Scheduler.
from apscheduler.schedulers.blocking import BlockingScheduler

# Main cronjob function.
from notify_new_listing import schedule_job

# Create an instance of scheduler and add function.
scheduler = BlockingScheduler()
scheduler.add_job(schedule_job, "interval", seconds=1800)

scheduler.start()