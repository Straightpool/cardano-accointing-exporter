import time
from datetime import timedelta, timezone
from time import sleep
from typing import Any

import requests as requests
from requests import Response

import config
from config import SHELLEY_START_EPOCH, SHELLEY_START_DATETIME, KOIOS_BASE_API
from shared.representations import *


# Function to POST request the api with a specific body and simple builtin retry
def request_api(url: str, body: Any) -> Response:
    retries = 0
    response_code = None
    while response_code != 200 and retries < 20:
        if retries > 0:
            sleep(retries * 5)
            print('Response code was: ' + str(response_code) + ' -> Retrying ' + str(retries) + '...')
        response = requests.post(url, json=body)
        response_code = response.status_code
        check_cached(response)
        config.request_time = time.time()
        retries += 1
    check_content(response)
    return response


# Function to check if the response was cached; needed for limiting api requests
def check_cached(response: Response) -> None:
    config.elapsed_time = time.time() - config.start_time
    elapsed_since_request = time.time() - config.request_time
    if not getattr(response, 'from_cache', False):
        config.api_counter += 1
        if config.elapsed_time > 5 and elapsed_since_request < 0.1:
            sleep(0.1 - elapsed_since_request)
    else:
        config.cache_counter += 1


# Check if the received response content type is json
def check_content(response: Response) -> None:
    if response is not None:
        if 'json' not in response.headers.get('Content-Type'):
            print('The content type of the received data is not json but ' + response.headers)
            exit(1)
    else:
        print('No response was received -> Exiting...')
        exit(1)


def get_reward_history_for_account(stake_addr: str) -> List[Reward]:
    reward_history = []
    rewards = []
    offset = 0
    new_results = True
    while new_results:
        body = {"_stake_addresses": [stake_addr]}
        reward_history_r = request_api(KOIOS_BASE_API + 'account_rewards' + '?offset=' + str(offset), body)
        new_results = reward_history_r.json()
        reward_history.append(reward_history_r.json())
        offset += 1000

    reward_history = [item for sublist in reward_history for item in sublist]

    if len(reward_history) > 0:
        for reward in reward_history[0]['rewards']:
            epoch = reward['earned_epoch']
            datetime_delta = (epoch - SHELLEY_START_EPOCH) * 5
            reward_time = SHELLEY_START_DATETIME + timedelta(days=datetime_delta) + timedelta(days=10)
            reward_type = reward['type']
            pool_id = reward['pool_id']
            rewards.append(Reward(epoch, reward_time.replace(tzinfo=timezone.utc), reward['amount'], pool_id, reward_type))

    return rewards
