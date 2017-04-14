import argparse
import os
import pyowm


def show_weather(place):
    owm = pyowm.OWM(os.environ['OWM_KEY'])
    observation = owm.weather_at_place(place)
    weather = observation.get_weather()
    placename = observation.get_location().get_name()
    print(
        "Current weather in {}: {}".format(
            placename,
            weather.get_detailed_status()
        )
    )

    # 5 days forecast in 3 hr intervals
    forecast = owm.three_hours_forecast(place)
    next_3 = pyowm.timeutils.next_three_hours()
    willberainy = forecast.will_be_rainy_at(next_3)
    if willberainy:
        print(
            "Rain is forecast in next 3 hrs in {}".format(placename)
        )
    else:
        print(
            "Rain is not forecast in the next 3 hrs in {}".format(placename)
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--place')
    args = parser.parse_args()
    place = args.place
    if not place:
        place = "Bonnyrigg,gb"
    show_weather(place)



