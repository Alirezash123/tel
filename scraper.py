import json
import os
from datetime import datetime
from telegram_channel_viewer import channel

def get_latest_posts(channel_username, limit=10):
    """
    دریافت آخرین پست‌های یک کانال عمومی تلگرام
    """
    if not channel_username:
        return {
            "success": False,
            "error": "نام کانال وارد نشده است",
            "channel": "",
            "last_update": datetime.now().isoformat()
        }
    
    try:
        # اتصال به کانال
        ch = channel(channel_username)
        
        # دریافت پیام‌ها - ببینیم دقیقاً چه شکلی است
        messages = ch.messages
        
        # دیباگ: ببینیم ساختار messages چیست
        print(f"🔍 نوع داده messages: {type(messages)}")
        if messages:
            print(f"🔍 نمونه اول: {messages[0] if messages else 'empty'}")
            print(f"🔍 نوع اولین المان: {type(messages[0]) if messages else 'unknown'}")
        
        # اگر messages یک لیست از رشته‌ها (str) بود
        if messages and isinstance(messages[0], str):
            # خروجی رشته‌ای است - احتمالاً HTML یا متن ساده
            results = []
            for idx, post_text in enumerate(messages[:limit]):
                results.append({
                    "id": idx + 1,
                    "content": post_text[:500],
                    "views": "نامشخص",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "link": f"https://t.me/{channel_username}/{idx+1}"
                })
            
            return {
                "success": True,
                "channel": channel_username,
                "last_update": datetime.now().isoformat(),
                "posts_count": len(results),
                "posts": results
            }
        
        # اگر messages یک لیست از دیکشنری بود (حالت عادی)
        elif messages and isinstance(messages[0], dict):
            results = []
            for idx, post in enumerate(messages[:limit]):
                # بررسی کنیم کلیدهای موجود چیست
                print(f"🔍 کلیدهای موجود در پست: {post.keys() if isinstance(post, dict) else 'not dict'}")
                
                results.append({
                    "id": idx + 1,
                    "content": post.get('text', post.get('content', str(post)))[:500],
                    "views": post.get('views', post.get('view_count', 'نامشخص')),
                    "date": post.get('date', post.get('datetime', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                    "link": f"https://t.me/{channel_username}/{post.get('id', idx+1)}"
                })
            
            return {
                "success": True,
                "channel": channel_username,
                "last_update": datetime.now().isoformat(),
                "posts_count": len(results),
                "posts": results
            }
        
        # اگر هیچ پستی نبود
        else:
            return {
                "success": False,
                "error": "هیچ پستی یافت نشد یا ساختار خروجی نامشخص است",
                "channel": channel_username,
                "last_update": datetime.now().isoformat(),
                "raw_messages": str(messages)[:500]  # برای دیباگ
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "channel": channel_username,
            "last_update": datetime.now().isoformat()
        }

def save_to_json(data, filename="output.json"):
    """ذخیره داده‌ها در فایل JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # خواندن نام کانال
    CHANNEL_NAME = os.getenv("TELEGRAM_CHANNEL", "bbcpersian")  # یک کانال پیش‌فرض معتبر
    
    if not CHANNEL_NAME:
        print("❌ خطا: نام کانال مشخص نشده است")
        CHANNEL_NAME = input("نام کانال را وارد کنید (مثال: bbcpersian): ").strip()
    
    print(f"📡 در حال دریافت پست‌های کانال {CHANNEL_NAME}...")
    
    # دریافت داده‌ها
    data = get_latest_posts(CHANNEL_NAME, limit=5)  # اول با 5 تا تست کن
    
    # ذخیره در فایل
    save_to_json(data)
    
    # نمایش نتیجه در لاگ
    print("\n" + "="*50)
    if data["success"]:
        print(f"✅ موفق: {data['posts_count']} پست ذخیره شد")
        for post in data["posts"]:
            print(f"  📝 {post['content'][:80]}...")
    else:
        print(f"❌ خطا: {data['error']}")
        if 'raw_messages' in data:
            print(f"🔍 داده خام: {data['raw_messages']}")
    
    print("="*50)
    print("📁 فایل output.json ذخیره شد")
