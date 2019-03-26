import random
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.db import connections
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from reminders.models import Appointment, ValidationError


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def dictfetchall(days_in_advance):
    "Return all rows from a cursor as a dict"
    sql = '''
    SELECT DISTINCT profile.prof_c_profilenum as profile_id,
                    prof_c_ip1firstname as name,
                    /*sch5event_contact_cell_phone as phone_number,*/
                    '2013814330' as phone_number,
                    'E' as comm_pref,
                    /*prof_c_commpref as comm_pref,*/
                    '5555555555' as home_phone,
    				/*profile.prof_c_arpphone as home_phone,*/
    				/*profile.prof_c_ip1p_email as email,*/
                    'apptreminder@mailinator.com' as email,
                    sch5event_id as id,
                    sch5appt_datetime as time
    FROM   scheduling_appointment
           JOIN scheduling_event
             ON sch5appt_eventid = sch5event_id
           JOIN profile
             ON prof_c_profilenum = sch5event_profile
    WHERE  Date(sch5appt_datetime) = {}
    ORDER  BY sch5appt_datetime
    '''
    appt_date = str(datetime.date.today() +
                    datetime.timedelta(days=days_in_advance))
    cursor = connections['emr'].cursor()
    cursor.execute(sql.format("'" + appt_date + "'"))
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# Schedule at random intervals because rundramatiq and django each spawn this
@register_job(scheduler, "interval", seconds=random.randint(90, 1200), replace_existing=True)
def populate_appt_database():
    """Specify the days in advance to send out reminders"""
    reminders = (1, 3)
    print("Scraping Evident db for schedule info")
    for i in reminders:
        rows = dictfetchall(i)
        for r in rows:
            appt = Appointment.objects.all()
            if appt.filter(emr_id=r['id'], reminder_days=i):
                print("{0}-day appointment reminder already exists".format(i))
            else:
                a = Appointment(profile_id=r['profile_id'],
                                emr_id=r['id'],
                                name=r['name'].capitalize(),
                                time=r['time'],
                                phone_number=r['phone_number'],
                                home_phone=r['home_phone'],
                                email=r['email'],
                                comm_pref=r['comm_pref'],
                                reminder_days=i)
                try:
                    a.clean()
                except ValidationError:
                    print("Appointment in the past")
                else:
                    a.save()


register_events(scheduler)
scheduler.start()
print("{} - Scheduler started!".format(datetime.datetime.now()))