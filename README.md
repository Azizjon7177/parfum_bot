# parfum_bot

Telegram bot for SHAik Perfume shop management.

## Local run

1. Create a virtual environment and install `requirements.txt`.
2. Copy `.env.example` to `.env`.
3. Set `BOT_TOKEN` and `DIRECTOR_ID` in `.env` (do not commit this file).
4. Run `python bot.py`.

## Railway deployment

1. Create a new Railway project and choose **Deploy from GitHub repo**.
2. Select this repository and keep the service as a long-running service.
3. In the service **Variables**, add `BOT_TOKEN` and `DIRECTOR_ID`.
4. Add a **Volume** mounted at `/data`, then add `DATA_DIR=/data` to Variables.
5. Deploy. Railway starts the bot with the Dockerfile and restarts it after a failure.

`parfum.db` is stored under `DATA_DIR`; it must be on the mounted volume in production so shop, seller, and stock data survives redeployments.
