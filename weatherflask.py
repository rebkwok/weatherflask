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
    text = request.args.get('text')
    place = request.args.get('place')
    place = text or place or 'Bonnyrigg,gb'

    error = None
    context = {}
    try:
        observation = owm.weather_at_place(place)
    except pyowm.exceptions.not_found_error.NotFoundError:
        current_weather = None
        error = 'Place not found'
        context['error'] = error
    else:
        weather = observation.get_weather()
        placename = observation.get_location().get_name()
        country = observation.get_location().get_country()
        current_weather = weather.get_detailed_status()
        temp = weather.get_temperature('celsius')['temp']

        # 5 days forecast in 3 hr intervals
        forecast = owm.three_hours_forecast(place)
        next_3 = pyowm.timeutils.next_three_hours()
        willberainy = forecast.will_be_rainy_at(next_3)

        context['placename'] = placename
        context['country'] = country
        context['current'] = current_weather
        context['temp'] = temp
        context['rain'] = willberainy

    to = request.args.get('msisdn')
    msg =  "Current weather in {}: {}; temp {}C".format(
                placename, current_weather, temp
            ) if current_weather else error
    if to:
        if to in ALLOWED_NUMBERS:
            return sendmsg(to, msg)
        else:
            return 'Phone number not allowed'
    else:
        return render_template('weather.html', **context)
