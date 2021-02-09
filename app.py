from cultisk import app, db
from cultisk import MI_model
from flask import Blueprint
from apscheduler.schedulers.background import BackgroundScheduler
from cultisk.SpamFilter_Api import MainFilter
import threading


db_commands = Blueprint('db', __name__)


@db_commands.cli.command('create')
def db_create():
    db.create_all()
    print('Database Created!')


@db_commands.cli.command('drop')
def db_drop():
    db.drop_all()
    print('Database Dropped!')


@db_commands.cli.command('reset')
def db_drop():
    db.drop_all()
    db.create_all()
    print('Database Reset!')


app.register_blueprint(db_commands)


def func3():
    lock = threading.Lock()

    def func1():
        lock.acquire()
        MI_model.update_mi()
        lock.release()

    def func2():
        lock.acquire()
        MainFilter.get()
        lock.release()

    func1()
    func2()
    print("finished running")


sched = BackgroundScheduler(daemon=True)
sched.add_job(func3, 'interval', minutes=30, id='my_func3_id')
sched.start()
#sched.remove_all_jobs()
# # #sched.remove_job('my_func3_id')
sched.shutdown()



if __name__ == '__main__':
    app.run()
