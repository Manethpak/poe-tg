from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from telegram.ext import Application, ApplicationBuilder
from argparse import ArgumentParser

from poe_tg import config
from poe_tg.telegram_handler import setup_handlers
from poe_tg.database import init_db


polling_app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()
setup_handlers(polling_app)

webhook_app = Application.builder().token(config.TELEGRAM_TOKEN).updater(None).build()
setup_handlers(webhook_app)


def run_polling():
    init_db()

    if not config.TELEGRAM_TOKEN:
        config.logger.error(
            "No Telegram token provided. Set the TELEGRAM_TOKEN in environment variables."
        )
        return

    polling_app.run_polling()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Sets the webhook for the Telegram Bot and manages its lifecycle (start/stop)."""
    init_db()

    if not config.WEBHOOK_URL:
        config.logger.error(
            "WEBHOOK_URL not found. Please set it in your environment or .env file."
        )

    if not config.TELEGRAM_TOKEN:
        config.logger.error(
            "No Telegram token provided. Set the TELEGRAM_TOKEN in environment variables."
        )
        return

    await webhook_app.bot.set_webhook(url=config.WEBHOOK_URL + "/webhook")

    async with webhook_app:
        await webhook_app.start()
        yield
        await webhook_app.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def process_update(request: Request):
    """Handles incoming Telegram updates and processes them with the bot."""
    message = await request.json()
    update = Update.de_json(data=message, bot=webhook_app.bot)
    await webhook_app.process_update(update)
    return Response(status_code=HTTPStatus.OK)


def main():
    parser = ArgumentParser(
        description="Run the Telegram bot in polling or webhook mode"
    )
    parser.add_argument("--poll", action="store_true", help="Run in polling mode")
    args = parser.parse_args()

    if args.poll:
        config.logger.info("Starting bot in polling mode...")
        run_polling()

    else:
        config.logger.info("Starting bot in webhook mode...")
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
