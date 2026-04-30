import json
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def get_telegram_posts(channel_url, limit=10):
    """
    دریافت آخرین پست‌های کانال تلگرام با BeautifulSoup
    """
    try:
        # ساخت آدرس RSS یا صفحه HTML کانال
        if "/s/" not in channel_url and "/" in channel_url:
            # تبدیل لینک معمولی به لینک ساده شده
            channel_name = channel_url.rstrip('/').split('/')[-1]
            url = f"https://t.me/s/{channel_name}"
        else:
            url = channel_url
        
        print(f"🔍 در حال دریافت از: {url}")
        
        # هدرهای مرورگر برای جلوگیری از بلاک
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
        }
        
        # دریافت صفحه
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # پردازش HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # پیدا کردن پست‌ها
        posts = []
        
        # روش اول: پیدا کردن divهای حاوی پیام
        message_divs = soup.find_all('div', class_='tgme_widget_message')
        
        if not message_divs:
            # روش دوم: جستجوی عمومی‌تر
            message_divs = soup.find_all('div', attrs={'data-post': True})
        
        for idx, msg in enumerate(message_divs[:limit]):
            try:
                # متن پست
                text_elem = msg.find('div', class_='tgme_widget_message_text')
                if not text_elem:
                    text_elem = msg.find('div', class_='message_text')
                
                text = text_elem.get_text(strip=True) if text_elem else ""
                
                # تعداد بازدید
                views_elem = msg.find('span', class_='tgme_widget_message_views')
                if not views_elem:
                    views_elem = msg.find('span', class_='message_views')
                
                views = views_elem.get_text(strip=True) if views_elem else "نامشخص"
                
                # زمان
                date_elem = msg.find('time', class_='datetime')
                if not date_elem:
                    date_elem = msg.find('a', class_='tgme_widget_message_date')
                
                date = date_elem.get('datetime', '') if date_elem else ""
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # لینک پست
                link_elem = msg.find('a', class_='tgme_widget_message_date')
                post_link = link_elem.get('href', '') if link_elem else ""
                
                posts.append({
                    "id": idx + 1,
                    "content": text[:1000] if text else "بدون متن",
                    "views": views,
                    "date": date,
                    "link": post_link if post_link else f"https://t.me/{channel_name}/{idx+1}"
                })
                
            except Exception as e:
                print(f"⚠️ خطا در پست {idx+1}: {e}")
                continue
        
        # اگر پستی پیدا نشد، خطای خاص برگردان
        if not posts:
            # برای دیباگ، بخشی از HTML را ذخیره کن
            debug_sample = str(soup)[:1000]
            return {
                "success": False,
                "error": "هیچ پستی پیدا نشد - ممکن است ساختار صفحه تغییر کرده باشد",
                "debug_html_sample": debug_sample,
                "url": url
            }
        
        # استخراج نام کانال از صفحه
        channel_name_elem = soup.find('div', class_='tgme_channel_info_header_title')
        channel_name = channel_name_elem.get_text(strip=True) if channel_name_elem else channel_url
        
        return {
            "success": True,
            "channel_name": channel_name,
            "channel_url": channel_url,
            "last_update": datetime.now().isoformat(),
            "posts_count": len(posts),
            "posts": posts
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"خطای شبکه: {str(e)}",
            "url": url if 'url' in locals() else channel_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"خطای پیش‌بینی‌نشده: {str(e)}",
            "url": channel_url
        }

def save_to_json(data, filename="output.json"):
    """ذخیره در فایل JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # کانال مورد نظر
    CHANNEL_URL = "https://t.me/drtel"
    
    print(f"📡 در حال دریافت از کانال {CHANNEL_URL}...")
    print("⏱️  این عملیات چند ثانیه طول می‌کشد...")
    
    # دریافت پست‌ها (حداکثر 10 تای اخیر)
    result = get_telegram_posts(CHANNEL_URL, limit=10)
    
    # ذخیره خروجی
    save_to_json(result)
    
    # نمایش نتیجه
    print("\n" + "="*60)
    if result["success"]:
        print(f"✅ نام کانال: {result['channel_name']}")
        print(f"✅ تعداد پست‌های دریافتی: {result['posts_count']}")
        print("\n📝 آخرین پست‌ها:")
        for post in result["posts"][:3]:
            print(f"\n--- پست {post['id']} ---")
            print(f"متن: {post['content'][:150]}...")
            print(f"بازدید: {post['views']}")
            print(f"لینک: {post['link']}")
    else:
        print(f"❌ خطا: {result['error']}")
    print("="*60)
    print("📁 فایل output.json ذخیره شد")