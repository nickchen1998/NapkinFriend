import os
from dotenv import load_dotenv

load_dotenv()


class Setting:
    database_url = os.getenv("DATABASE_URL")
    google_map_key = os.getenv("GOOGLE_MAP_KEY")
    channel_token = os.getenv("CHANNEL_TOKEN")
    channel_secret = os.getenv("CHANNEL_SECRET")
    first_time_liff_id = os.getenv("FIRST_TIME_LIFF_ID")
    update_cotton_liff_id = os.getenv("UPDATE_COTTON_LIFF_ID")
