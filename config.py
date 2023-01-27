import glob
import time
from datetime import datetime
from typing import Set

# Configuration variables
PROJECT_ID = ''
BLOCKFROST_BASE_API = 'https://cardano-mainnet.blockfrost.io/api/v0/'
KOIOS_BASE_API = 'https://api.koios.rest/api/v0/'
SHELLEY_START_EPOCH = 208
SHELLEY_START_DATETIME = datetime(2020, 7, 29, 21, 44, 51)
LINE_CLEAR = '\x1b[2K'
# Configure how long rewards and transactions should stay in cache (in seconds). Using the defaults new rewards will
# only be requested every 5 days (60 * 60 * 24 * 5) and transactions will only be requested every 24 hours (60 * 60 * 24 * 1).
URLS_EXPIRE_AFTER = {KOIOS_BASE_API + 'account_rewards': 60 * 60 * 24 * 5,
                     BLOCKFROST_BASE_API + 'addresses/*/transactions': 60 * 60 * 24 * 1,
                     BLOCKFROST_BASE_API + 'accounts/*': 60 * 60 * 24 * 5, }

# Change this parameter to limit the cache size if you run out of memory (e.g. to '16000' entries) if
cache_limit = None
# Change this parameter if you want to specify another subdirectory for your .wallet files
wallet_files = glob.glob('wallets/*.wallet')
# You should not need to change anything below this line
addresses = set()   # type: Set[str]
api_counter = 0
classify_internal_txs = False
start_time = time.time()
elapsed_time = time.time() - start_time
ondisk_cache_counter = 0
request_time = time.time()
