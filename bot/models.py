import peewee
import datetime


models = peewee.SqliteDatabase('user_database.sqlite')

class BaseModel(peewee.Model):
    class Meta:
        database = models

class TelegramUser(BaseModel):
    telegram_id = peewee.IntegerField(primary_key=True)
    username = peewee.CharField(max_length=255)
    balance = peewee.IntegerField(default=0)

class Deposit(BaseModel): 
    telegram_user = peewee.ForeignKeyField(TelegramUser, backref='deposits') 
    now_id = peewee.IntegerField()
    amount = peewee.DecimalField(max_digits=10, decimal_places=2)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    status = peewee.CharField(max_length=10, default='waiting', choices=[
        ('waiting', 'Waiting'),
        ('confirming', 'Confirming'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ])


class Withdraw(BaseModel): 
    telegram_user = peewee.ForeignKeyField(TelegramUser, backref='deposits') 
    amount = peewee.DecimalField(max_digits=10, decimal_places=2)
    created_at = peewee.DateTimeField(default=datetime.datetime.now)
    solana_address = peewee.CharField(max_length=50)
    status = peewee.CharField(max_length=10, default='waiting', choices=[
        ('pending', 'Pending'),
        ('confirming', 'Confirming'),
        ('confirmed', 'Confirmed'),
        ('refunded', 'Refunded'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ])

class MevSniper(BaseModel):
    telegram_user = peewee.ForeignKeyField(TelegramUser, backref='deposits')
    status = peewee.CharField(max_length=10, default='off', choices = [
        ('off', 'Off'),
        ('on', 'On')
    ])
models.create_tables([TelegramUser, Deposit, MevSniper, Withdraw])