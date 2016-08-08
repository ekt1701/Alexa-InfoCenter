from __future__ import print_function
import json
import re
import urllib2

def lambda_handler(event, context):

    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "getForecastIntent":
        return getForecast(intent, session)
    elif intent_name == "getCurrentIntent":
        return getCurrent(intent, session)
    elif intent_name == "getAstronomyIntent":
        return getAstronomy(intent, session)
    elif intent_name == "getHumidIntent":
        return getHumidity(intent, session)
    elif intent_name == "getPressureIntent":
        return getPressure(intent, session)
    elif intent_name == "getSurfIntent":
        return getSurf(intent, session)
    elif intent_name == "getEarthquakeIntent":
        return getEarthquake(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return signoff()
    elif intent_name == "AMAZON.YesIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "What do you want to hear? You can say current, forecast, humidity, pressure, astronomy, surf, earthquakes"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, speech_output))

def getCurrent(intent, session):
    session_attributes = {}
    card_title = "Current Weather"
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%3D12795729&format=json"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    
    title = data['query']['results']['channel']['item']['title']
    
    temp = data['query']['results']['channel']['item']['condition']['temp']
    status = data['query']['results']['channel']['item']['condition']['text']
    
    humidity = data['query']['results']['channel']['atmosphere']['humidity']
    
    temppressure = data['query']['results']['channel']['atmosphere']['pressure']
    rising = data['query']['results']['channel']['atmosphere']['rising']
    
    dp =float(temppressure)
    pressure = str(round((dp*0.0295301),2))

    if rising == 1:
        rising = "Rising"
    elif rising == 2:
        rising = "Falling"
    else:
        rising = "Steady"
    wind = data['query']['results']['channel']['wind']['speed']
    winddirection = data['query']['results']['channel']['wind']['direction']
    dw = int(winddirection)
    directionnumber = round(((dw-11.25)/22.5),0)
    convertnumber=['North','North northeast','Northeast','East northeast','East','East southeast','Southeast','South southeast','South','South southwest','Southwest','West southwest','West','West northwest','Northwest','North northwest']
    dn = int(directionnumber)
    directionstring = str(convertnumber[dn])
    
    forecast = data['query']['results']['channel']['item']['forecast']
    
    day0all = forecast[0]
    day0data = ". Today it will be " + day0all['text'] + " and " + day0all['high'] + " degrees. "
  
    session_attributes = {}
    speech_output = title + ". It is " + status + ". The temperature is " + temp + " degrees. Wind Speed is " + wind + " miles per hour, the direction is " + directionstring + ". The humidity is " + humidity + " percent. " + " The pressure is " + pressure + " millibars and is " + rising + day0data + " Would you like to hear more information?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))
        
def getForecast(intent, session):
    session_attributes = {}
    card_title = "Weather Forecast"
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%3D12795729&format=json"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
        
    forecast = data['query']['results']['channel']['item']['forecast']
    
    day1all = forecast[1]
    shortname = day1all['day']
    fullday = fullname(shortname);
    
    day1data = "On " + fullday + " it will be " + day1all['text'] + " and " + day1all['high'] + " degrees. "

    day2all = forecast[2]
    shortname = day2all['day']
    fullday = fullname(shortname);
    day2data = "On " + fullday + " it will be " + day2all['text'] + " and " + day2all['high'] + " degrees. "

    day3all = forecast[3]
    shortname = day3all['day']
    fullday = fullname(shortname);
    day3data = "On " + fullday + " it will be " + day3all['text'] + " and " + day3all['high'] + " degrees. "

    day4all = forecast[4]
    shortname = day4all['day']
    fullday = fullname(shortname);
    day4data = "On " + fullday + " it will be " + day4all['text'] + " and " + day4all['high'] + " degrees. "
    
    day5all = forecast[5]
    shortname = day5all['day']
    fullday = fullname(shortname);
    day5data = "On " + fullday + " it will be " + day5all['text'] + " and " + day5all['high'] + " degrees. "
    
    day6all = forecast[6]
    shortname = day6all['day']
    fullday = fullname(shortname);
    day6data = "On " + fullday + " it will be " + day6all['text'] + " and " + day6all['high'] + " degrees. "
  
    session_attributes = {}
    speech_output = "Here is your weather forecast " + day1data + day2data + day3data + day4data + day5data + day6data + " Would you like to hear more information?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))

def fullname(shortday):
	if shortday == "Mon":
		fullday = "Monday"
	if shortday == "Tue":
		fullday = "Tuesday"
	if shortday == "Wed":
		fullday = "Wednesday"
	if shortday == "Thu":
		fullday = "Thursday"
	if shortday == "Fri":
		fullday = "Friday"
	if shortday == "Sat":
		fullday = "Saturday"
	if shortday == "Sun":
		fullday = "Sunday"
	return fullday;
	

def getHumidity(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D12795729&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    humidity = data['query']['results']['channel']['atmosphere']['humidity']

    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "The humidity is currently " + humidity + " percent. Would you like to hear something else?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))


def getPressure(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D12795729&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    temppressure = data['query']['results']['channel']['atmosphere']['pressure']
    rising = data['query']['results']['channel']['atmosphere']['rising']
    
    dp =float(temppressure)
    pressure = str(round((dp*0.0295301),2))

    if rising == 1:
        rising = "Rising"
    elif rising == 2:
        rising = "Falling"
    else:
        rising = "Steady"

    session_attributes = {}
    card_title = "Barometric Pressure"
    speech_output = "The pressure is currently " + pressure + " millibars and is " + rising + " Would you like to hear something else?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))


def getAstronomy(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20astronomy%20from%20weather.forecast%20where%20woeid%3D12795729&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    
    sunrise = data['query']['results']['channel']['astronomy']['sunrise']
    sunset = data['query']['results']['channel']['astronomy']['sunset']
    
    riseA,riseB = sunrise.split(":")
    setA,setB = sunset.split(":")
    
    if len(setB) == 4:
        timesunset = setA + ":" + "0" + setB
    else:
        timesunset = sunset
        
    if len(riseB) == 4:
        timesunrise = riseA + ":" + "0" + riseB
    else:
        timesunrise = sunrise
        
    url = "http://api.burningsoul.in/moon"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    
    moonphase = data['stage']
    moonillumination = data['illumination']
    
    textillumination = str(moonillumination)

    illumationpercent,splitB = textillumination.split(".")
    fullmoon = str(data['FM']['DT'])
    fullmoonA,fullmoonB = fullmoon.split("-")

    session_attributes = {}
    card_title = "Astronomy"
    speech_output = "Sunrise is at " + timesunrise + ". Sunset is at " + timesunset + ". Moon phase is " + moonphase + ". Illumination is at " + illumationpercent + " percent. Full moon will be on " + fullmoonB + "Would you like some other information?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))

def getSurf(intent, session):
    session_attributes = {}
    card_title = "Surf Conditions"
    url = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&num=10&q=http://feeds.feedburner.com/surfline-rss-surf-report-south-los-angeles"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    surfreports = data['responseData']['feed']['entries']
    
    titles = []
    for site in surfreports:
        titles.append(site['title'])
    
   
    session_attributes = {}
    speech_output = "Here are the surf conditions " + ' . '.join(titles) + " Would you like to hear something else?"

    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))
        
def getEarthquake(intent, session):
    session_attributes = {}
    card_title = "Earthquakes"
    url = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&num=10&q=http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.atom"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    earthquakereports = data['responseData']['feed']['entries']
    
    titles = []
    for site in earthquakereports:
        titles.append(site['title'])
   
    session_attributes = {}
    speech_output = "Here are the latest earthquakes " + ' . '.join(titles) + " Would you like to hear something else?"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))
        
def signoff():
    session_attributes = {}
    card_title = "Signing off"
    speech_output = "This is your weather center signing off"
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, "", should_end_session, speech_output))
        
def handle_session_end_request():
    should_end_session = True
    return build_response({}, build_speechlet_response(
        None, None, None, should_end_session, None))

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, card_text):
    if output == None:
        return {
            'shouldEndSession': should_end_session
        }
    elif title == None:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }
    else:
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }