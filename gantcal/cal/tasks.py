from celery.utils.log import get_task_logger
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from cal.emails import send_feedback_email

logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute='*/30',day_of_week='tue')), name="send_feedback_email_task", ignore_result=True)
def send_feedback_email_task():
    logger.info("Sent feedback email")
    return send_feedback_email("Alex.Miller@devinit.org", "Hello world")