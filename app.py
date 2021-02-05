from cultisk import app, db
from flask import Blueprint

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

if __name__ == '__main__':
    #context = ('ssl.crt', 'ssl.key')
    app.run(debug=True)
