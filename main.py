"""
ربات فروشگاه مانتو تلگرام
فایل اصلی - نسخه اصلاح شده
"""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

# ایمپورت ماژول‌های پروژه
from config import BOT_TOKEN, ADMIN_ID
from database import Database
from states import (
    PRODUCT_NAME, PRODUCT_DESC, PRODUCT_PHOTO,
    PACK_NAME, PACK_QUANTITY, PACK_PRICE,
    FULL_NAME, ADDRESS_TEXT, PHONE_NUMBER
)

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    """هندلر دستور /start"""
    user_id = update.effective_user.id
    
    # Import توابع
    from handlers.admin import admin_start
    from handlers.user import user_start
    
    if user_id == ADMIN_ID:
        await admin_start(update, context)
    else:
        await user_start(update, context)


async def handle_text_messages(update: Update, context):
    """مدیریت پیام‌های متنی"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Import توابع
    from handlers.admin import add_product_start, list_products, show_statistics
    from handlers.order import view_pending_orders, view_payment_receipts
    from handlers.user import view_cart, view_my_orders, view_my_address, contact_us
    
    # دستورات ادمین
    if user_id == ADMIN_ID:
        if text == "➕ افزودن محصول":
            return await add_product_start(update, context)
        elif text == "📦 لیست محصولات":
            return await list_products(update, context)
        elif text == "📋 سفارشات جدید":
            return await view_pending_orders(update, context)
        elif text == "💳 تایید پرداخت‌ها":
            return await view_payment_receipts(update, context)
        elif text == "📊 آمار":
            return await show_statistics(update, context)
    
    # دستورات کاربر
    if text == "🛒 سبد خرید":
        await view_cart(update, context)
    elif text == "📦 سفارشات من":
        await view_my_orders(update, context)
    elif text == "📍 آدرس ثبت شده من":
        await view_my_address(update, context)
    elif text == "📞 تماس با ما":
        await contact_us(update, context)
    elif text == "ℹ️ راهنما":
        await update.message.reply_text(
            "📚 راهنمای استفاده:\n\n"
            "1️⃣ از کانال ما محصولات را مشاهده کنید: @manto_omdeh_erfan\n"
            "2️⃣ روی دکمه پک مورد نظر کلیک کنید\n"
            "3️⃣ هر بار کلیک = 1 پک به سبد اضافه می‌شود\n"
            "4️⃣ بعد تمام شدن، روی 'سبد خرید' کلیک کنید\n"
            "5️⃣ سفارش خود را نهایی کنید\n"
            "6️⃣ بعد از تایید، مبلغ را واریز کنید\n"
            "7️⃣ رسید را ارسال کنید\n"
            "8️⃣ سفارش شما ارسال می‌شود! 🎉"
        )


async def handle_photos(update: Update, context):
    """مدیریت عکس‌ها (رسیدها)"""
    from handlers.order import handle_receipt
    await handle_receipt(update, context)


async def error_handler(update: Update, context):
    """مدیریت خطاها"""
    logger.error(f"خطا: {context.error}")


def main():
    """تابع اصلی"""
    # Import توابع
    from handlers.admin import (
        add_product_start, product_name_received, product_desc_received,
        product_photo_received, add_pack_start, pack_name_received,
        pack_quantity_received, pack_price_received, view_packs,
        get_channel_link, delete_product, admin_start
    )
    from handlers.user import (
        finalize_order_start, full_name_received, address_text_received, 
        phone_number_received, use_old_address,
        use_new_address, handle_pack_selection, view_cart,
        remove_from_cart, clear_cart, handle_shipping_selection,
        final_confirm_order, final_edit_order, edit_address,
        back_to_packs, user_start, confirm_user_info, edit_user_info_for_order
    )
    from handlers.order import (
        confirm_order, reject_order, confirm_payment, reject_payment,
        remove_item_from_order, reject_full_order, back_to_order_review,
        confirm_modified_order
    )
    
    # ایجاد دیتابیس
    db = Database()
    
    # ساخت اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ذخیره دیتابیس در bot_data
    application.bot_data['db'] = db
    
    # ==================== ConversationHandler برای افزودن محصول ====================
    add_product_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ افزودن محصول$"), add_product_start)],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_name_received)],
            PRODUCT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_desc_received)],
            PRODUCT_PHOTO: [MessageHandler(filters.PHOTO, product_photo_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), admin_start)],
    )
    
    # ==================== ConversationHandler برای افزودن پک ====================
    add_pack_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_pack_start, pattern="^add_pack:")],
        states={
            PACK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, pack_name_received)],
            PACK_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, pack_quantity_received)],
            PACK_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pack_price_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), admin_start)],
    )
    
    # ==================== ConversationHandler برای نهایی کردن سفارش ====================
    finalize_order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(finalize_order_start, pattern="^finalize_order$")],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_received)],
            ADDRESS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_text_received)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), user_start)],
    )
    
    # ==================== ConversationHandler برای ویرایش آدرس ====================
    edit_address_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_address, pattern="^edit_address$")],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_received)],
            ADDRESS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_text_received)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), user_start)],
    )
    
    # ==================== ConversationHandler برای ویرایش اطلاعات موقع سفارش ====================
    edit_user_info_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_user_info_for_order, pattern="^edit_user_info$")],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_received)],
            ADDRESS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_text_received)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), user_start)],
    )
    
    # ==================== ConversationHandler برای ویرایش در فاکتور نهایی ====================
    final_edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(final_edit_order, pattern="^final_edit$")],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name_received)],
            ADDRESS_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_text_received)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number_received)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ لغو$"), user_start)],
    )
    
    # ==================== هندلرهای اصلی ====================
    application.add_handler(CommandHandler("start", start))
    application.add_handler(add_product_conv)
    application.add_handler(add_pack_conv)
    application.add_handler(finalize_order_conv)
    application.add_handler(edit_address_conv)
    application.add_handler(edit_user_info_conv)
    application.add_handler(final_edit_conv)  # اضافه شد
    
    # ==================== CallbackQuery هندلرها ====================
    application.add_handler(CallbackQueryHandler(handle_pack_selection, pattern="^select_pack:"))
    application.add_handler(CallbackQueryHandler(back_to_packs, pattern="^back_to_packs:"))
    application.add_handler(CallbackQueryHandler(view_cart, pattern="^view_cart$"))
    application.add_handler(CallbackQueryHandler(remove_from_cart, pattern="^remove_cart:"))
    application.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    application.add_handler(CallbackQueryHandler(handle_shipping_selection, pattern="^ship_"))
    application.add_handler(CallbackQueryHandler(final_confirm_order, pattern="^final_confirm$"))
    # final_edit_order حذف شد چون الان ConversationHandler داره
    application.add_handler(CallbackQueryHandler(use_old_address, pattern="^use_old_address$"))
    application.add_handler(CallbackQueryHandler(use_new_address, pattern="^use_new_address$"))
    application.add_handler(CallbackQueryHandler(confirm_user_info, pattern="^confirm_user_info$"))
    # این خط حذف شد چون الان ConversationHandler داره: application.add_handler(CallbackQueryHandler(edit_user_info_for_order, pattern="^edit_user_info$"))
    
    # هندلرهای مدیریت محصول
    application.add_handler(CallbackQueryHandler(view_packs, pattern="^view_packs:"))
    application.add_handler(CallbackQueryHandler(get_channel_link, pattern="^send_to_channel:"))
    application.add_handler(CallbackQueryHandler(delete_product, pattern="^delete_product:"))
    
    # هندلرهای سفارش
    application.add_handler(CallbackQueryHandler(confirm_order, pattern="^confirm_order:"))
    application.add_handler(CallbackQueryHandler(reject_order, pattern="^reject_order:"))
    application.add_handler(CallbackQueryHandler(remove_item_from_order, pattern="^remove_item:"))
    application.add_handler(CallbackQueryHandler(reject_full_order, pattern="^reject_full:"))
    application.add_handler(CallbackQueryHandler(back_to_order_review, pattern="^back_to_order:"))
    application.add_handler(CallbackQueryHandler(confirm_modified_order, pattern="^confirm_modified:"))
    application.add_handler(CallbackQueryHandler(confirm_payment, pattern="^confirm_payment:"))
    application.add_handler(CallbackQueryHandler(reject_payment, pattern="^reject_payment:"))
    
    # ==================== Message هندلرها ====================
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # شروع ربات
    logger.info("🤖 ربات شروع به کار کرد!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
