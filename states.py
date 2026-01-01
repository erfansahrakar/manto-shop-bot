"""
تعریف State های مکالمه برای ConversationHandler ها
"""

# State های محصول و پک (ادمین)
PRODUCT_NAME, PRODUCT_DESC, PRODUCT_PHOTO = range(3)
PACK_NAME, PACK_QUANTITY, PACK_PRICE = range(3, 6)

# State های اطلاعات کاربر
FULL_NAME, ADDRESS_TEXT, PHONE_NUMBER = range(6, 9)
