# Standard Library Imports
import os
import logging
import asyncio
import json

# Third-Party Library Imports
from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sentry_sdk
from app.src.config.config import settings

# Local Application/Library Imports
from app.src.handlers.instances import messenger
from app.src.routers.route import router
from app.src.translation.translation_script import *
from app.src.config.database import (
    check_mongo_db_collections, 
    create_or_fetch_user,
    get_mongo_db_user_collection
)
from app.src.handlers.state_manager import AppState
from app.src.handlers.onboarding import OnboardingProcess
from app.src.handlers.analytics import user_analytics
from app.src.handlers.conversation import ConversationHandler
from app.src.schema.schemas import user_serial_list_entity
from app.src.config.config import settings

# Initialize Sentry
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# Logging
logging.basicConfig(
    filename="cra_bot.log", 
    level=logging.ERROR, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S'
)

# Check mongodb collection
check_mongo_db_collections()

# Initialize FastAPI
app = FastAPI()

# Include the router
app.include_router(router, prefix="/api/v1")

@app.get("/webhook/")
async def verify_token(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: int = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_HOOK_TOKEN:
        return JSONResponse(status_code=200, content=int(hub_challenge))
    return JSONResponse(status_code=403, content="Forbidden")

@app.post("/webhook/")
async def webhook_whatsapp(request: Request):
    try:
        data = await request.json()
        state = AppState()

        changed_field = messenger.changed_field(data)

        delivery_status = messenger.get_delivery(data)

        if changed_field == "messages":
            new_message = messenger.is_message(data)

            if new_message:
                mobile = messenger.get_mobile(data)
                name = messenger.get_name(data)
                message_type = messenger.get_message_type(data)

                if message_type in ["text", "audio", "interactive"]:
                                
                    logging.info(f"New Message; sender:{mobile} name:{name}")

                    state.mobile = mobile
                    state.display_phone_number = messenger.get_display_mobile(data)
                    state.create_or_fetch_user()
                    state.save()

                    if message_type == "text" and messenger.get_message(data) == "/reset":
                        # Reset the state and save
                        state.reset(state.mobile)
                        state.save()
                        logging.info(f"User: {state.mobile} has reset their data.")
                        messenger.send_message(user_phone_number=state.mobile, message="Your data has been reset. Starting onboarding process again.")
                        await asyncio.sleep(1.5)

                    if state.onboarded is False:
                        logging.info(f"Starting onboarding Process for user: {state.mobile}")
                        onboarding_process = OnboardingProcess(data, state)
                        await onboarding_process.start()
                        state = onboarding_process.state
                    else:
                        logging.info("Starting Conversation Engien for user: {state.mobile}")
                        conversation_handler = ConversationHandler(data, state)
                        await conversation_handler.chat()

    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return JSONResponse(content={"status": "200 OK HTTPS."}, status_code=200)

@app.get("/dl/user/{filename}")
async def download_user_file(filename: str):
    file_path = f"app/data/output/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/dl/static/{filename}")
async def download_static_file(filename: str):
    file_path = f"app/data/static/{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

app.mount("/static", StaticFiles(directory="app/templates"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get_analytics_page(request: Request):
    user_analytics_data = user_analytics()
    user_analytics_data["request"] = request
    return templates.TemplateResponse("analytics.html", user_analytics_data)

@app.head("/")
async def head_analytics_page():
    return HTMLResponse(content="")
