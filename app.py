import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# Replace with your bot token
BOT_TOKEN = "7847884105:AAEyQHdFOG1uFo0ARTtcRFMeZsNK7AZyGX8"

# Replace with your API base URL
API_BASE_URL = "https://backend-mumbai-production.up.railway.app/api/employeesemployeesemployeesemployees"

# Default RSVP link (replace with your preferred link)
DEFAULT_employeesemployees://yourwebsite.com/contact"  # Example: Link to your website's contact page

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Fetch all employees (treated as events) from your API (with retries)
def fetch_events(max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(API_BASE_URL, timeout=10)  # Add timeout
            response.raise_for_status()
            return response.json().get("data", {}).get("employees", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching employees (attempt {retries + 1}): {e}")
            retries += 1
            time.sleep(2)  # Wait before retrying
    return []


# Fetch employee details by ID (treated as event details) with retries
def fetch_event_by_id(event_id, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(f"{API_BASE_URL}/{event_id}", timeout=10)  # Add timeout
            response.raise_for_status()
            return response.json().get("data", {})
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching employee details (attempt {retries + 1}): {e}")
            retries += 1
            time.sleep(2)  # Wait before retrying
    return None


# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /events to see the list of current events.")


# Command: /events
async def list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching events... Please wait.")

    events = fetch_events()
    if not events:
        await update.message.reply_text("No events found or the backend is having issues. Please try again later.")
        return

    keyboard = []
    for event in events:
        keyboard.append([InlineKeyboardButton(event["name"], callback_data=f"event_{event['_id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Here are the current events:", reply_markup=reply_markup)


# Handle event selection
async def event_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    event_id = query.data.split("_")[1]
    event = fetch_event_by_id(event_id)

    if event:
        # Use default RSVP link if 'rsvp_link' is missing or empty
        rsvp_link = event.get("rsvp_link", DEFAULT_RSVP_LINK)

        # Prepare the event details message
        message = (
            f"**Title:** {event['name']}\n"
            f"**Description:** {event['about']}\n"
            f"**Location:** {event['location']}\n"
            f"**Type:** {event.get('Breed', 'N/A')}\n"
            f"**Capacity:** {event.get('capacity', 'N/A')}\n"
            f"**RSVP Link:** [Click Here]({rsvp_link})"
        )

        # Check if profileImage (Cloudinary URL) is available
        profile_image = event.get("profileImage")
        if profile_image:
            # Send the profile image as a photo with the event details as the caption
            await query.message.reply_photo(photo=profile_image, caption=message, parse_mode="Markdown")
        else:
            # Send only the text if no profile image is available
            await query.edit_message_text(message, parse_mode="Markdown")

        # Add RSVP button
        keyboard = [[InlineKeyboardButton("RSVP", url=rsvp_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Click below to RSVP:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Event not found or the backend is having issues. Please try again later.")


# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("events", list_events))
    application.add_handler(CallbackQueryHandler(event_detail, pattern="^event_"))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
