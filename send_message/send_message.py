import gammu


def send_message(data,username,db_session):
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()
    message = {'Text': str(data.get('message')), 'SMSC': {'Location': 1},
               'Number': str(data.get('cell_no')) }
    sm.SendSMS(message)


