import schedule
import time
import trader
import analyzer
import db.db as db

trader = trader.Trader()

def trader_loop():
    trader.loop()

def analyzer_loop():
    analyzer.loop()

def activate():
    schedule.clear(tag='fx')
    schedule.every(60).seconds.do(trader_loop).tag('fx')
    schedule.every(60).seconds.do(analyzer_loop).tag('fx')

def deactivate():
    trader.exit()
    schedule.clear(tag='fx')

def delete_old_log():
    db.delete_old_log()

schedule.every().monday.at('08:00').do(activate)
schedule.every().tuesday.at('08:00').do(activate)
schedule.every().wednesday.at('08:00').do(activate)
schedule.every().thursday.at('08:00').do(activate)
schedule.every().friday.at('08:00').do(activate)
schedule.every().saturday.at('05:00').do(deactivate)

schedule.every(1).weeks.do(delete_old_log)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        db.write_log('exception', str(e))
        continue