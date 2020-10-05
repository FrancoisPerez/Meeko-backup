import requests
import argparse
import logging
import pathlib
import time
import json
import os

AUTHORIZATION_BEARER = "" #= "Bearer cHecTjbI4CTu7TrqlAKOVicGNnx65dKwhs4SvdqPXXzN7AXClnW4uDX4m0oJ"
CURRENT_PATH = pathlib.Path(__file__).parent.absolute()
START_TIMESTAMP = 0 #1567296000
END_TIMESTAMP =  0 #1598918400
SECONDS_IN_A_DAY = 60 * 60 * 24

def get_authentication_headers():
    headers = {
        'Authorization': AUTHORIZATION_BEARER,
        'Accept-Encoding': 'gzip,deflate,br',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Host': 'api.meeko.app',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) Mobile/15E148',
        'X-Protected-By':'Sqreen',
        'X-Requested-With':'XMLHttpRequest'
    }
    return headers


def save_to_file(filename, data):
    file = open(filename, 'w')
    file.write(json.dumps(data, indent=4))
    file.close()


def request_nursery():
    endpoint = "https://api.meeko.app/family/v1/nurseries"
    headers = get_authentication_headers()
    response = requests.get(endpoint, headers=headers)
    logging.info("Saving nursery file : nursery.json")
    save_to_file("nursery/nursery.json", response.json())

def request_photos():
    endpoint = "https://api.meeko.app/family/v1/photos?per_page=100"
    headers = get_authentication_headers()
    response = requests.get(endpoint, headers=headers)
    parsed_response = response.json()

    # Download photos
    for photo in parsed_response['data'] :
        logging.info("Downloading file : {0}".format(photo["photo_url"]))
        r = requests.get(photo["photo_url"], allow_redirects=True)
        if r.status_code == 200:
            with open('{0}/photos/{1}_{2}.png'.format(CURRENT_PATH,
                                                      photo['taken_at'],
                                                      photo['id']), 'wb') as f:
                f.write(r.content)

    # Save data
    filename = "photos_page_{0}.json".format(parsed_response["current_page"])
    logging.info("Saving photo file : {0}".format(filename))
    save_to_file(filename, response.json())

    if parsed_response["next_page_url"]:
        request_photos(parsed_response["next_page_url"])

def build_array_of_dates(START_TIMESTAMP, END_TIMESTAMP):
    start = START_TIMESTAMP
    end = END_TIMESTAMP
    array_of_dates = []

    while end <= END_TIMESTAMP:
        array_of_dates.append([start, start + SECONDS_IN_A_DAY])

        # Re-init of start and end
        start += SECONDS_IN_A_DAY
        end = start + SECONDS_IN_A_DAY

    return array_of_dates

def request_kids_news():
    array_of_dates = build_array_of_dates(START_TIMESTAMP,END_TIMESTAMP)

    for dates in array_of_dates:
        endpoint = "https://api.meeko.app/family/v1/kids?from={0}&to={1}".format(dates[0],dates[1])
        logging.info("Getting {0}".format(endpoint))
        headers = get_authentication_headers()
        response = requests.get(endpoint, headers=headers)
        parsed_response = response.json()

        # Save data
        date_from_start_timestamp = time.strftime("%Y-%m-%d", time.gmtime(dates[0]))
        filename = "kids/kids_news_{0}.json".format(date_from_start_timestamp)
        logging.info("Saving Kids News file : {0}".format(filename))
        save_to_file(filename, response.json())

def request_news(endpoint = "https://api.meeko.app/family/v1/news?page=1"):
    headers = get_authentication_headers()
    response = requests.get(endpoint, headers=headers)
    parsed_response = response.json()

    # Save data
    filename = "news/news_page_{0}.json".format(parsed_response["current_page"])
    logging.info("Saving News file : {0}".format(filename))
    save_to_file(filename, response.json())

    if parsed_response["next_page_url"]:
        request_news(parsed_response["next_page_url"])

def request_messages(endpoint = "https://api.meeko.app/family/v1/messages?page=1"):
    headers = get_authentication_headers()
    response = requests.get(endpoint, headers=headers)
    parsed_response = response.json()

    # Save data
    filename = "messages/messages_page_{0}.json".format(parsed_response["current_page"])
    logging.info("Saving Messages file : {0}".format(filename))
    save_to_file(filename, response.json())

    if parsed_response["next_page_url"]:
        request_news(parsed_response["next_page_url"])

def make_folders():
    try:
        os.mkdir("nursery/")
        os.mkdir("kids/")
        os.mkdir("photos/")
        os.mkdir("messages/")
        os.mkdir("news/")
    except OSError:
        logging.info("Couldn't create base directory (or maybe it already exists).")

def main():
    global AUTHORIZATION_BEARER
    global START_TIMESTAMP
    global END_TIMESTAMP

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-b",
        "--bearer",
        required=True,
        type=str,
        help="The Authorization Bearer token (without \"Bearer \"")
    parser.add_argument(
        "-s",
        "--start_timestamp",
        required=True,
        type=int,
        help="The migration start timestamp ")
    parser.add_argument(
        "-e",
        "--end_timestamp",
        required=True,
        type=int,
        help="The migration end timestamp")
    args = parser.parse_args()

    AUTHORIZATION_BEARER = "Bearer " + args.bearer
    START_TIMESTAMP = args.start_timestamp
    END_TIMESTAMP = args.end_timestamp

    log_format = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
    date_format = "%H:%M:%S"
    logging.basicConfig(format=log_format, datefmt=date_format, level=logging.INFO)

    make_folders()

    request_nursery()
    request_photos()
    request_kids_news()
    request_news()
    request_messages()

if __name__ == "__main__":
    main()