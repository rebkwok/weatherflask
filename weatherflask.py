import nexmo
import os
import pyowm

from flask import Flask, render_template, request

app = Flask(__name__)

api_key = os.environ['NEXMO_KEY']
api_secret = os.environ['NEXMO_SECRET']
owm = pyowm.OWM(os.environ['OWM_KEY'])
ALLOWED_NUMBERS = os.environ['ALLOWED_NUMBERS'].split(',')


def sendmsg(to, text):
    client = nexmo.Client(key=api_key, secret=api_secret)
    response = client.send_message(
        {'from': 'WeatherFlask', 'to': to, 'text': text}
    )

    message = response['messages'][0]

    if message['status'] == '0':
        return 'Sent message {}; Remaining balance is {}'.format(
            message['message-id'], message['remaining-balance']
        )
    else:
        return 'Error: {}'.format(message['error-text'])


@app.route('/')
def show_weather():
    place = request.args.get('text')
    if not place:
        place = request.args.get('place', 'Bonnyrigg,gb')

    observation = owm.weather_at_place(place)
    weather = observation.get_weather()
    placename = observation.get_location().get_name()
    current_weather = "Current weather in {}: {}".format(
            placename,
            weather.get_detailed_status()
        )

    # 5 days forecast in 3 hr intervals
    forecast = owm.three_hours_forecast(place)
    next_3 = pyowm.timeutils.next_three_hours()
    willberainy = forecast.will_be_rainy_at(next_3)
    if willberainy:
        rain_forecast = "Rain is forecast in next 3 hrs in {}".format(
            placename
        )
    else:
        rain_forecast = "Rain is not forecast in the next 3 hrs in {}".format(
            placename
        )

    to = request.args.get('msisdn')
    if to:
        if to in ALLOWED_NUMBERS:
            return sendmsg(to, current_weather)
        else:
            return 'Number not allowed'
    else:
        return render_template(
            'weather.html',
            placename=placename,
            current=current_weather,
            rain=rain_forecast
        )
