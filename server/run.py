from myapp.app import *
from myapp.app.routes import *
from myapp.app.schedules import *

def start_scheduler():
    scheduler = BackgroundScheduler()
    execution_hours = [5, 12, 17, 21]
    for hour in execution_hours:
        scheduler.add_job(recalculate_eta, trigger='cron', hour = hour, minute = 0)
    flow_prediction_hours =  list(range(24))
    minutes = [0, 10, 20, 30, 40, 50]
    for hour in flow_prediction_hours:
      for minute in minutes:
        args_for_recalculate_flow_prediction = (minute,)
        scheduler.add_job(recalculate_flow_prediction, args=args_for_recalculate_flow_prediction, trigger='cron', hour=hour, minute=minute)

    scheduler.start()

app = Flask(__name__)
run_with_ngrok(app)

with open('myapp/app/templates/home.html', 'r') as file:
    html_content = file.read()

app.register_blueprint(routeOpt, url_prefix='/route')
app.register_blueprint(edge, url_prefix='/edge')


@app.route("/")
def home():
    return html_content



if __name__ == '__main__':
    start_scheduler()  # Start the scheduler
    traci.start(["sumo", "-c", 'myapp/app/sumoFiles/newyork_city.sumocfg'])
    app.run()
    traci.close()


