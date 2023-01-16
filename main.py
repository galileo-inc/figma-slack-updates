import schedule
import time
from update import slack_updates_for_figma_files

schedule.every(10).minutes.do(slack_updates_for_figma_files)
# schedule.every().day.at("18:35:00").do(slack_updates_for_figma_files)

while 1:
    n = schedule.idle_seconds()
    if n is None:
        break
    elif n > 0:
        time.sleep(n)
    schedule.run_pending()
