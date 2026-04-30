import json
import os
from datetime import datetime
from telegram_channel_viewer import channel

def get_latest_posts(channel_username, limit=10):
    """
    دریافت آخرین پست‌های یک کانال عمومی تلگرام
    """
    try:
        # اتصال به کانال
        ch = channel(channel_username)
        
        # دریافت پیام‌ها
        messages = ch.messages
        
        # محدود کردن به تعداد مورد نظر
        latest_posts = messages[:limit]
        
        # پردازش و ساخت خروجی تمیز
        results = []
        for idx, post in enumerate(latest_posts):
            results.append({
                "id": idx + 1,
                "content": post.get('content', '')[:500],  # محدود کردن طول متن
                "views": post.get('views', 'نامشخص'),
                "date": post.get('date', 'نامشخص'),
                "link": f"https://t.me/{channel_username}/{post.get('id', '')}"
            })
        
        return {
            "success": True,
            "channel": channel_username,
            "last_update": datetime.now().isoformat(),
            "posts_count": len(results),
            "posts": results
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
    # نام کانال مورد نظر - می‌توانید از طریق Environment Variable هم بخوانید
    CHANNEL_NAME = os.getenv("TELEGRAM_CHANNEL", "durov")  # پیش‌فرض کانال durov
    
    print(f"در حال دریافت پست‌های کانال {CHANNEL_NAME}...")
    
    # دریافت داده‌ها
    data = get_latest_posts(CHANNEL_NAME, limit=10)
    
    # ذخیره در فایل
    save_to_json(data)
    
    # نمایش نتیجه در لاگ
    if data["success"]:
        print(f"✅ {data['posts_count']} پست با موفقیت ذخیره شد")
        for post in data["posts"]:
            print(f"  - {post['content'][:50]}...")
    else:
        print(f"❌ خطا: {data['error']}")
