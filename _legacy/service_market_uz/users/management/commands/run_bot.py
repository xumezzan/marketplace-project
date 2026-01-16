import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from users.models import User
from asgiref.sync import sync_to_async

class Command(BaseCommand):
    help = 'Runs the Telegram Bot'

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stdout.write(self.style.ERROR('TELEGRAM_BOT_TOKEN is not set'))
            return

        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        start_handler = CommandHandler('start', self.start)
        contact_handler = MessageHandler(filters.CONTACT, self.contact)
        
        application.add_handler(start_handler)
        application.add_handler(contact_handler)
        
        self.stdout.write(self.style.SUCCESS('Bot started...'))
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        button = KeyboardButton("Share Phone Number", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Welcome to ServiceMarket UZ! 🇺🇿\nPlease share your phone number to link your account.", 
            reply_markup=reply_markup
        )

    async def contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        contact = update.effective_message.contact
        phone_number = contact.phone_number
        chat_id = update.effective_chat.id
        
        # Normalize phone number (ensure + prefix)
        if not phone_number.startswith('+'):
            phone_number = f'+{phone_number}'
            
        user = await self.find_user(phone_number)
        
        if user:
            await self.update_user_chat_id(user, str(chat_id))
            await update.message.reply_text(
                f"✅ Successfully connected! Hello, {user.first_name or 'User'}.\nYou will now receive new orders here."
            )
        else:
            await update.message.reply_text(
                "❌ Phone number not found in our system.\nPlease register on the website first."
            )

    @sync_to_async
    def find_user(self, phone):
        try:
            return User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def update_user_chat_id(self, user, chat_id):
        user.telegram_chat_id = chat_id
        user.save()
