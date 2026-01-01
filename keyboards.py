"""
کیبوردها و دکمه‌های ربات
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def admin_main_keyboard():
    """منوی اصلی ادمین"""
    keyboard = [
        ["➕ افزودن محصول", "📦 لیست محصولات"],
        ["📋 سفارشات جدید", "💳 تایید پرداخت‌ها"],
        ["📊 آمار"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def user_main_keyboard():
    """منوی اصلی کاربر"""
    keyboard = [
        ["🛒 سبد خرید", "📦 سفارشات من"],
        ["📍 آدرس ثبت شده من"],
        ["📞 تماس با ما", "ℹ️ راهنما"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def cancel_keyboard():
    """دکمه لغو"""
    keyboard = [["❌ لغو"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def product_inline_keyboard(product_id, packs):
    """دکمه‌های انتخاب پک برای محصول - برای کانال"""
    keyboard = []
    for pack in packs:
        pack_id, prod_id, name, quantity, price, *_ = pack
        button_text = f"📦 {name} - {price:,.0f} تومان"
        keyboard.append([InlineKeyboardButton(
            button_text, 
            callback_data=f"select_pack:{product_id}:{pack_id}"
        )])
    return InlineKeyboardMarkup(keyboard)


def quantity_keyboard(product_id, pack_id, max_quantity=10):
    """دکمه‌های انتخاب تعداد - دیگه استفاده نمیشه"""
    # این تابع رو نگه داشتیم برای سازگاری با کد قدیمی
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data=f"back_to_packs:{product_id}")]]
    return InlineKeyboardMarkup(keyboard)


def cart_keyboard(cart_items):
    """دکمه‌های سبد خرید"""
    keyboard = []
    for item in cart_items:
        cart_id, product_name, pack_name, pack_qty, price, quantity = item
        keyboard.append([InlineKeyboardButton(
            f"🗑 حذف {product_name} ({pack_name})",
            callback_data=f"remove_cart:{cart_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("✅ نهایی کردن سفارش", callback_data="finalize_order")])
    keyboard.append([InlineKeyboardButton("🗑 خالی کردن سبد", callback_data="clear_cart")])
    return InlineKeyboardMarkup(keyboard)


def order_confirmation_keyboard(order_id):
    """دکمه‌های تایید سفارش برای ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"confirm_order:{order_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_order:{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def payment_confirmation_keyboard(order_id):
    """دکمه‌های تایید پرداخت برای ادمین"""
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید رسید", callback_data=f"confirm_payment:{order_id}"),
            InlineKeyboardButton("❌ رد رسید", callback_data=f"reject_payment:{order_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def product_management_keyboard(product_id):
    """دکمه‌های مدیریت محصول"""
    keyboard = [
        [InlineKeyboardButton("➕ افزودن پک", callback_data=f"add_pack:{product_id}")],
        [InlineKeyboardButton("👁 مشاهده پک‌ها", callback_data=f"view_packs:{product_id}")],
        [InlineKeyboardButton("📤 ارسال به کانال", callback_data=f"send_to_channel:{product_id}")],
        [InlineKeyboardButton("🗑 حذف محصول", callback_data=f"delete_product:{product_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_products_keyboard():
    """دکمه بازگشت به لیست محصولات"""
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_products")]]
    return InlineKeyboardMarkup(keyboard)


def view_cart_keyboard():
    """دکمه مشاهده سبد خرید"""
    keyboard = [[InlineKeyboardButton("🛍 مشاهده سبد خرید", callback_data="view_cart")]]
    return InlineKeyboardMarkup(keyboard)


def address_selection_keyboard():
    """دکمه‌های انتخاب آدرس - DEPRECATED"""
    keyboard = [
        [InlineKeyboardButton("📍 استفاده از آدرس قبلی", callback_data="use_old_address")],
        [InlineKeyboardButton("✏️ وارد کردن آدرس جدید", callback_data="use_new_address")]
    ]
    return InlineKeyboardMarkup(keyboard)


def shipping_method_keyboard():
    """دکمه‌های انتخاب نحوه ارسال"""
    keyboard = [
        [InlineKeyboardButton("🚌 ترمینال", callback_data="ship_terminal")],
        [InlineKeyboardButton("🚚 باربری", callback_data="ship_barbari")],
        [InlineKeyboardButton("📦 تیپاکس", callback_data="ship_tipax")],
        [InlineKeyboardButton("🏃 چاپار", callback_data="ship_chapar")]
    ]
    return InlineKeyboardMarkup(keyboard)


def final_confirmation_keyboard():
    """دکمه‌های تایید نهایی فاکتور"""
    keyboard = [
        [InlineKeyboardButton("✅ تایید و ثبت نهایی", callback_data="final_confirm")],
        [InlineKeyboardButton("✏️ ویرایش اطلاعات", callback_data="final_edit")]
    ]
    return InlineKeyboardMarkup(keyboard)


def edit_address_keyboard():
    """دکمه ویرایش آدرس"""
    keyboard = [[InlineKeyboardButton("✏️ ویرایش آدرس", callback_data="edit_address")]]
    return InlineKeyboardMarkup(keyboard)


def confirm_info_keyboard():
    """دکمه‌های تایید یا ویرایش اطلاعات"""
    keyboard = [
        [InlineKeyboardButton("✅ بله، اطلاعات صحیح است", callback_data="confirm_user_info")],
        [InlineKeyboardButton("✏️ خیر، ویرایش مشخصات", callback_data="edit_user_info")]
    ]
    return InlineKeyboardMarkup(keyboard)


def order_items_removal_keyboard(order_id, items):
    """دکمه‌های حذف آیتم‌های سفارش"""
    keyboard = []
    for idx, item in enumerate(items):
        product_name = item.get('product', 'محصول')
        pack_name = item.get('pack', 'پک')
        button_text = f"❌ حذف: {product_name} - {pack_name}"
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"remove_item:{order_id}:{idx}"
        )])
    
    # دکمه تایید با تغییرات
    keyboard.append([InlineKeyboardButton("✅ تایید سفارش با تغییرات", callback_data=f"confirm_modified:{order_id}")])
    
    # دکمه رد کامل سفارش
    keyboard.append([InlineKeyboardButton("🗑 رد کامل سفارش", callback_data=f"reject_full:{order_id}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"back_to_order:{order_id}")])
    
    return InlineKeyboardMarkup(keyboard)
