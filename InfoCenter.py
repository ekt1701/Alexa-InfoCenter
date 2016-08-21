from __future__ import print_function
import json
import re
import urllib2
import urllib
import csv
import subprocess
import random

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
    elif intent_name == "getAirQualityIntent":
        return getAirQuality(intent, session)
    elif intent_name == "getHeadlineNewsIntent":
        return getHeadlineNews(intent, session)
    elif intent_name == "getRandomQuoteIntent":
        return getRandomQuote(intent, session)
    elif intent_name == "getJokeIntent":
        return getJoke(intent, session)
    elif intent_name == "getCatFactsIntent":
        return getCatFacts(intent, session)
    elif intent_name == "getStocksIntent":
        return getStocks(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return signoff()
    elif intent_name == "AMAZON.YesIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_help()
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
    speech_output = "What do you want to hear?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help():
    session_attributes = {}
    card_title = "Help"
    speech_output = " You can say current, forecast, humidity, pressure, astronomy, surf, earthquakes, air quality, news, stocks, quote, joke or cat. What would you like to hear?"
    should_end_session = False
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getCurrent(intent, session):
    session_attributes = {}
    card_title = "Current Weather"
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%3D12795652&format=json"
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
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getForecast(intent, session):
    session_attributes = {}
    card_title = "Weather Forecast"
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%3D12795652&format=json"
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
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

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
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D12795652&format=json&diagnostics=true&callback="
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    humidity = data['query']['results']['channel']['atmosphere']['humidity']

    session_attributes = {}
    card_title = "Yahoo Weather"
    speech_output = "The humidity is currently " + humidity + " percent. Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def getPressure(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20atmosphere%20from%20weather.forecast%20where%20woeid%3D12795652&format=json&diagnostics=true&callback="
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
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def getAstronomy(intent, session):
    url = "https://query.yahooapis.com/v1/public/yql?q=select%20astronomy%20from%20weather.forecast%20where%20woeid%3D12795652&format=json&diagnostics=true&callback="
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
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

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

    temp1 = '. '.join(titles)
    temp = re.sub("SHITPIPE.*?ft.", "", temp1)

    replace = {
        "Surf: " : "",
        ".." : "."
         }

    surfreport = multiple_replace(replace, temp)

    session_attributes = {}
    if surfreport == "":
        text = "The surf report feed appears to be down, please try again later. Would you like to hear something else?"
    else:
        text = "Here are the surf conditions. " + surfreport + " Would you like to hear something else?"
    speech_output = text
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getEarthquake(intent, session):
    session_attributes = {}
    card_title = "CA earthquakes"
    records = fetchRecords(pullFeed())
    quakes = compile(records)
    titles = []
    for quake in quakes:
        replace = {
            "'" : "\\",
            "CA" : "",
            "California" : ""
            }

        quakereport = multiple_replace(replace, quake)
        titles.append(quakereport)
    temp1 = '. '.join(titles)

    if temp1 == "":
        text = "There were no magnitude 2.5 or larger earthquakes in California in the past day. Would you like to hear something else?"
    else:
        text = "Here are latest magnitude 2.5+ earthquakes in California " + str(temp1) + ". Would you like to hear something else?"

    speech_output = text
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def pullFeed():
    """Pulls the 24 hour feed of all 2.5+ earthquakes"""
    url = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.csv"
    #Other feeds that are available for the Past Day.
    #url = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.csv"
    #url = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_day.csv"
    #url = "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.csv"
    return [line.decode('utf-8') for line in urllib.urlopen(url).readlines()]

def fetchRecords(contents):
    """Filters out the feed contents to just records containing "CA"."""
    Records = []
    for record in csv.reader(contents):
        for element in record:
            if "CA" in element:
                Records.append(record)
            elif "California" in element:
                Records.append(record)
    return Records

def build(record):
    """Translates a record into a event."""
    date_time = record[0]
    date,time = date_time.split("T")
    time,B = time.split(".")
    return "{0} magnitude, {1} at: {2} {3}, Zulu Time".format(record[4], record[13], date, time)

def compile(Records):
    """Passes each selected record over the build function."""
    return [build(record) for record in Records]

def getAirQuality(intent, session):
    session_attributes = {}
    card_title = "Air Quality"

    aqicn_url = "http://feed.aqicn.org/feed/los-angeles/en/feed.v1.json"
    aqicn_response = urllib2.urlopen(aqicn_url)
    aqicn_data = json.loads(aqicn_response.read())

    date = aqicn_data['aqi']['date']
    aqi_value = aqicn_data['aqi']['val']
    rating = aqicn_data['aqi']['impact']
    if rating != "no data":
        o3_value = aqicn_data['iaqi']['o3']['val']
        co_value = aqicn_data['iaqi']['co']['val']
        no2_value = aqicn_data['iaqi']['no2']['val']
        text = "On " + str(date) +  ", Air Now reports the aqi as " + str(aqi_value) + ", which is " + rating + ". The ozone level was " + str(o3_value) + ". The carbon monoxide level was " + str(co_value) + ". The sulfur dioxide level was " + str(no2_value) + ". Would you like to hear something else?"
    else:
        text = "The Air Now feed appears to be down, please try again later. Would you like to hear something else?"

    speech_output = text
    reprompt_text = ""

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def getHeadlineNews(intent, session):
    session_attributes = {}
    card_title = "Headline News"
    url = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&num=10&q=http://www.latimes.com/local/lanow/rss2.0.xml"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    newsreports = data['responseData']['feed']['entries']

    titles = []
    for site in newsreports:
        titles.append(site['title'])

    newsreport = '. '.join(titles)

    speech_output = "Here are the latest news from the Los Angeles Times. " + newsreport + ". Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getRandomQuote(intent, session):
    session_attributes = {}
    card_title = "Random Quote"
    randomwords = ['positive', 'funny', 'inspiration', 'nature', 'courage', 'laugh', 'tech', 'exercise', 'health', 'fitness', 'laughter', 'silly', 'sunny', 'happy', 'cheerful', 'animals', 'friendship', 'success', 'patience', 'love', 'peace']
    randomstring = str(randomwords[random.randint(0,20)])
    url = "http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&num=1&q=https://www.quotesdaddy.com/feed/tagged/"+randomstring
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    RandomQuote = data['responseData']['feed']['entries']
    titles = []
    for site in RandomQuote:
        titles.append(site['title'])

    quoterandom = '. '.join(titles)
    speech_output = "Here is a quote for you. " + quoterandom + ". Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getCatFacts(intent, session):
    session_attributes = {}
    card_title = "Cat facts"
    url = "http://catfacts-api.appspot.com/api/facts?number=1"
    response = urllib2.urlopen(url)
    data = dict(json.loads(response.read()))
    catfact = data['facts']
    temp = str(catfact)
    replace = {
    "'" : "\'",
    "[u" : "",
    "]" : ""
    }
    webtext = multiple_replace(replace, temp)
    speech_output = "Here is a cat fact " + str(webtext) + " Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def getJoke(intent, session):
    session_attributes = {}
    card_title = "Random Jokes"
    i = random.randint(0,99)
    if i < 50:
        url = "http://api.icndb.com/jokes/random"
        response = urllib2.urlopen(url)
        data = dict(json.loads(response.read()))
        randomjoke = data['value']['joke']
    else:
        url = "http://tambal.azurewebsites.net/joke/random"
        response = urllib2.urlopen(url)
        data = dict(json.loads(response.read()))
        randomjoke = data['joke']

    speech_output = "Here is joke for you: " + randomjoke + " Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def getStocks(intent, session):
    session_attributes = {}
    card_title = "Dow Jones"
    stocklist = ["983582", "660463", "304466804484872"]
    myreport = []
    i=0
    while i<len(stocklist):
        url = "https://www.google.com/finance?cid="+stocklist[i]
        file = urllib.urlopen(url)
        text = file.read()

        namelocation = '<title>(.+?):'
        pricelocation = '<span id="ref_'+stocklist[i]+'_l">(.+?)</span>'
        changelocation = '<span class="chg" id="ref_'+stocklist[i]+'_c">(.+?)</span>'
        changelocation2 = '<span class="chr" id="ref_'+stocklist[i]+'_c">(.+?)</span>'

        namepattern = re.compile(namelocation)
        pricepattern = re.compile(pricelocation)
        changepattern = re.compile(changelocation)
        changepattern2 = re.compile(changelocation2)

        name = re.findall(namepattern,text)
        price = re.findall(pricepattern,text)
        change = re.findall(changepattern,text)
        change2 = re.findall(changepattern2,text)

        stock = str(name) + " price was " + str(price) +  " the change was " +  str(change) + str(change2)

        replace = {
            "[" : "",
            "]" : ""
            }

        stockreport = multiple_replace(replace, stock)

        myreport.append(stockreport)
        i+=1

    speech_output = '. '.join(myreport) + " Would you like to hear something else?"
    reprompt_text = ""
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def signoff():
    session_attributes = {}
    card_title = "Signing off"
    speech_output = "This is your Info Center signing off"
    should_end_session = True
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    should_end_session = True
    return build_response({}, build_speechlet_response(
        None, None, None, should_end_session))

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
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
