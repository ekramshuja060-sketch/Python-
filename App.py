# app.py - نسخه Replit
import streamlit as st
import sqlite3
import hashlib
import random
from datetime import datetime
import os

# === تنظیمات برای Replit ===
PORT = int(os.environ.get("PORT", 8080))

# === اتصال به دیتابیس SQLite ===
conn = sqlite3.connect('mega_platform.db', check_same_thread=False)
c = conn.cursor()

# ایجاد جدول‌ها
tables = [
    '''CREATE TABLE IF NOT EXISTS users 
       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        username TEXT UNIQUE, 
        password TEXT, 
        bio TEXT,
        created_at TEXT)''',
    
    '''CREATE TABLE IF NOT EXISTS posts 
       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user TEXT, 
        content TEXT, 
        type TEXT, 
        likes INTEGER DEFAULT 0,
        time TEXT)''',
    
    '''CREATE TABLE IF NOT EXISTS games 
       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user TEXT, 
        game TEXT, 
        score INTEGER, 
        time TEXT)''',
    
    '''CREATE TABLE IF NOT EXISTS chat_messages 
       (id INTEGER PRIMARY KEY AUTOINCREMENT, 
        room TEXT DEFAULT 'عمومی',
        sender TEXT, 
        content TEXT, 
        time TEXT)'''
]

for table in tables:
    c.execute(table)
conn.commit()

# === توابع کمکی ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, bio=""):
    try:
        c.execute("INSERT INTO users (username, password, bio, created_at) VALUES (?, ?, ?, ?)",
                  (username, hash_password(password), bio, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone() is not None

def get_user_info(username):
    c.execute("SELECT username, bio, created_at FROM users WHERE username=?", (username,))
    return c.fetchone()

# === تنظیمات Streamlit ===
st.set_page_config(
    page_title="مگا پلتفرم",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚀"
)

# استایل زیبا
st.markdown("""
<style>
    /* هدر اصلی */
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* کارت */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-right: 5px solid #1E88E5;
    }
    
    /* دکمه */
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #0D47A1);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }
    
    /* ورودی */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E0E0E0;
        padding: 10px;
    }
    
    /* برای موبایل */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .card { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# === مدیریت وضعیت ===
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.page = "home"

# === صفحه ورود ===
def login_page():
    st.markdown('<div class="main-header">🚀 مگا پلتفرم پرو آنلاین</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🌟 اولین شبکه اجتماعی ایرانی با بازی آنلاین!
        
        **امکانات رایگان:**
        - 💬 **چت آنلاین** - با دوستان گپ بزنید
        - 🎮 **بازی تعاملی** - حدس عدد و سوالات هوش
        - 📱 **پست گذاری** - افکارتون رو به اشتراک بگذارید
        - 👥 **کاربران فعال** - با دیگران آشنا شوید
        - ⚡ **سریع و سبک** - روی همه دستگاه‌ها
        
        **همین حالا رایگان عضو شوید!**
        """)
        
        # آمار
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM posts")
        post_count = c.fetchone()[0]
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("👥 کاربران", user_count)
        with col_stat2:
            st.metric("📝 پست‌ها", post_count)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 ورود", "📝 ثبت‌نام"])
        
        with tab1:
            st.subheader("ورود به حساب")
            username = st.text_input("نام کاربری")
            password = st.text_input("رمز عبور", type="password")
            
            if st.button("ورود به پنل", type="primary"):
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.page = "home"
                        st.success(f"✅ خوش آمدید {username}!")
                        st.rerun()
                    else:
                        st.error("❌ نام کاربری یا رمز عبور اشتباه است")
                else:
                    st.warning("⚠️ لطفا اطلاعات را وارد کنید")
        
        with tab2:
            st.subheader("ایجاد حساب جدید")
            new_user = st.text_input("نام کاربری جدید")
            new_pass = st.text_input("رمز عبور جدید", type="password")
            new_pass2 = st.text_input("تکرار رمز عبور", type="password")
            bio = st.text_area("معرفی خودتون (اختیاری)")
            
            if st.button("عضویت رایگان"):
                if new_user and new_pass:
                    if new_pass == new_pass2:
                        if create_user(new_user, new_pass, bio):
                            st.success("🎉 حساب شما ساخته شد!")
                            st.info("حالا می‌توانید وارد شوید")
                            st.balloons()
                        else:
                            st.error("⚠️ این نام کاربری قبلاً ثبت شده")
                    else:
                        st.error("❌ رمزهای عبور مطابقت ندارند")
                else:
                    st.warning("⚠️ لطفا اطلاعات را کامل کنید")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # آموزش نصب
    with st.expander("📱 آموزش نصب روی موبایل"):
        st.markdown("""
        1. **در مرورگر موبایل** (Chrome یا Safari) لینک بالا را باز کنید
        2. روی **منو (⋯)** کلیک کنید
        3. گزینه **"Add to Home Screen"** را انتخاب کنید
        4. روی **"Add"** کلیک کنید
        5. ✅ اپ روی صفحه اصلی نصب شد!
        
        🔥 **مزایای نصب:** سریع‌تر، آفلاین کار می‌کند، مثل اپ واقعی
        """)

# === صفحه اصلی ===
def home_page():
    # منوی کناری
    with st.sidebar:
        st.markdown(f"### 👋 سلام {st.session_state.username}!")
        
        user_info = get_user_info(st.session_state.username)
        if user_info:
            st.markdown(f"**بیوگرافی:** {user_info[1] if user_info[1] else 'تعیین نشده'}")
            st.caption(f"عضو از: {user_info[2]}")
        
        st.markdown("---")
        
        # انتخاب صفحه
        page = st.radio(
            "منوی اصلی:",
            ["🏠 خانه", "💬 چت آنلاین", "🎮 بازی‌ها", "📝 پست جدید", "👤 پروفایل", "⚙️ تنظیمات"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # آمار سریع
        c.execute("SELECT COUNT(*) FROM posts WHERE user=?", (st.session_state.username,))
        my_posts = c.fetchone()[0]
        st.metric("پست‌های من", my_posts)
        
        if st.button("🚪 خروج", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    # محتوای صفحه
    if "🏠 خانه" in page:
        st.markdown('<div class="main-header">🏠 فید پست‌ها</div>', unsafe_allow_html=True)
        
        # پست جدید سریع
        with st.form("quick_post", clear_on_submit=True):
            post_content = st.text_area("چه خبر؟", placeholder="چه چیزی در ذهنت میگذره؟...")
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("📤 ارسال پست")
            with col2:
                st.form_submit_button("پاک کردن")
            
            if submit and post_content:
                c.execute("INSERT INTO posts (user, content, type, time) VALUES (?, ?, ?, ?)",
                         (st.session_state.username, post_content, "text", 
                          datetime.now().strftime("%H:%M")))
                conn.commit()
                st.success("پست شما منتشر شد!")
                st.rerun()
        
        st.markdown("---")
        
        # نمایش پست‌ها
        c.execute("SELECT user, content, time FROM posts ORDER BY id DESC LIMIT 20")
        posts = c.fetchall()
        
        if posts:
            for user, content, time in posts:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"**👤 {user}** · `{time}`")
                st.markdown(f"> {content}")
                
                col_like, col_comment = st.columns(2)
                with col_like:
                    st.button("❤️ لایک", key=f"like_{user}_{time}")
                with col_comment:
                    st.button("💬 نظر", key=f"comment_{user}_{time}")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 هنوز پستی وجود ندارد. اولین پست رو شما بگذارید!")
    
    elif "💬 چت آنلاین" in page:
        st.markdown('<div class="main-header">💬 چت زنده</div>', unsafe_allow_html=True)
        
        # ارسال پیام
        with st.form("chat_form"):
            message = st.text_input("پیام شما:")
            if st.form_submit_button("📤 ارسال"):
                if message:
                    c.execute("INSERT INTO chat_messages (sender, content, time) VALUES (?, ?, ?)",
                             (st.session_state.username, message, datetime.now().strftime("%H:%M:%S")))
                    conn.commit()
                    st.rerun()
        
        # نمایش پیام‌ها
        chat_container = st.container(height=400)
        with chat_container:
            c.execute("SELECT sender, content, time FROM chat_messages ORDER BY id DESC LIMIT 50")
            messages = c.fetchall()[::-1]  # معکوس کنیم
        
            if messages:
                for sender, content, time in messages:
                    if sender == st.session_state.username:
                        st.markdown(f"""
                        <div style='text-align: left; margin: 10px;'>
                            <div style='background: #DCF8C6; padding: 10px; border-radius: 15px; 
                                      display: inline-block; max-width: 70%;'>
                                <strong>شما</strong> ({time}):<br>
                                {content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='text-align: right; margin: 10px;'>
                            <div style='background: white; padding: 10px; border-radius: 15px;
                                      display: inline-block; max-width: 70%; border: 1px solid #E0E0E0;'>
                                <strong>{sender}</strong> ({time}):<br>
                                {content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("💬 هنوز پیامی نیست. اولین نفر باشید!")
    
    elif "🎮 بازی‌ها" in page:
        st.markdown('<div class="main-header">🎮 بازی‌های آنلاین</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🎯 حدس عدد", "🧠 سوال هوش", "🏆 رده‌بندی"])
        
        with tab1:
            st.markdown("### بازی حدس عدد")
            st.markdown("عدد بین 1 تا 100 را حدس بزنید!")
            
            guess = st.slider("انتخاب عدد:", 1, 100, 50)
            
            if st.button("🎯 حدس بزن!"):
                secret = random.randint(1, 100)
                score = max(0, 100 - abs(secret - guess))
                
                c.execute("INSERT INTO games (user, game, score, time) VALUES (?, ?, ?, ?)",
                         (st.session_state.username, "حدس عدد", score, 
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                
                st.markdown(f"""
                <div class="card">
                <h3>🎯 نتیجه بازی</h3>
                <p>عدد مخفی: <strong>{secret}</strong></p>
                <p>حدس شما: <strong>{guess}</strong></p>
                <p>امتیاز: <strong>{score}/100</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                if score > 80:
                    st.balloons()
                    st.success("🎉 عالی!")
        
        with tab2:
            st.markdown("### سوالات اطلاعات عمومی")
            
            questions = [
                {"q": "پایتخت ایران؟", "a": "تهران"},
                {"q": "بزرگترین سیاره؟", "a": "مشتری"},
                {"q": "نویسنده شاهنامه؟", "a": "فردوسی"},
                {"q": "بلندترین کوه؟", "a": "اورست"}
            ]
            
            q = random.choice(questions)
            st.markdown(f"**سوال:** {q['q']}")
            
            answer = st.text_input("پاسخ شما:")
            
            if st.button("✅ ثبت پاسخ"):
                if answer.lower() == q['a'].lower():
                    score = 100
                    c.execute("INSERT INTO games (user, game, score, time) VALUES (?, ?, ?, ?)",
                             (st.session_state.username, "سوال هوش", score,
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success(f"🎉 درست! +100 امتیاز")
                    st.balloons()
                else:
                    st.error(f"❌ پاسخ صحیح: {q['a']}")
        
        with tab3:
            st.markdown("### جدول رده‌بندی")
            
            c.execute("""
                SELECT user, SUM(score) as total 
                FROM games 
                GROUP BY user 
                ORDER BY total DESC 
                LIMIT 10
            """)
            leaderboard = c.fetchall()
            
            if leaderboard:
                for i, (user, score) in enumerate(leaderboard, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    st.markdown(f"{medal} **{user}** - {score} امتیاز")
            else:
                st.info("🎮 هنوز کسی بازی نکرده!")
    
    elif "📝 پست جدید" in page:
        st.markdown('<div class="main-header">📝 ایجاد پست جدید</div>', unsafe_allow_html=True)
        
        with st.form("new_post_form", clear_on_submit=True):
            post_type = st.selectbox("نوع پست:", ["پست متنی", "شعر", "داستان", "نکته"])
            content = st.text_area("متن پست:", height=200)
            
            if st.form_submit_button("📤 انتشار پست"):
                if content:
                    c.execute("INSERT INTO posts (user, content, type, time) VALUES (?, ?, ?, ?)",
                             (st.session_state.username, content, post_type,
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.success("✅ پست شما منتشر شد!")
                    st.balloons()
    
    elif "👤 پروفایل" in page:
        st.markdown('<div class="main-header">👤 پروفایل شما</div>', unsafe_allow_html=True)
        
        user_info = get_user_info(st.session_state.username)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### اطلاعات حساب")
            if user_info:
                new_bio = st.text_area("بیوگرافی:", value=user_info[1] if user_info[1] else "")
                if st.button("💾 ذخیره تغییرات"):
                    c.execute("UPDATE users SET bio=? WHERE username=?", 
                             (new_bio, st.session_state.username))
                    conn.commit()
                    st.success("✅ به‌روز شد!")
                    st.rerun()
        
        with col2:
            st.markdown("### 📊 آمار شما")
            
            c.execute("SELECT COUNT(*) FROM posts WHERE user=?", (st.session_state.username,))
            posts = c.fetchone()[0]
            
            c.execute("SELECT SUM(score) FROM games WHERE user=?", (st.session_state.username,))
            score = c.fetchone()[0] or 0
            
            c.execute("SELECT COUNT(*) FROM chat_messages WHERE sender=?", (st.session_state.username,))
            messages = c.fetchone()[0]
            
            st.metric("📝 پست‌ها", posts)
            st.metric("🎮 امتیاز کل", score)
            st.metric("💬 پیام‌ها", messages)
    
    elif "⚙️ تنظیمات" in page:
        st.markdown('<div class="main-header">⚙️ تنظیمات</div>', unsafe_allow_html=True)
        
        st.markdown("### تغییر رمز عبور")
        
        current = st.text_input("رمز فعلی:", type="password")
        new = st.text_input("رمز جدید:", type="password")
        confirm = st.text_input("تکرار رمز جدید:", type="password")
        
        if st.button("🔄 تغییر رمز"):
            if authenticate_user(st.session_state.username, current):
                if new == confirm:
                    c.execute("UPDATE users SET password=? WHERE username=?", 
                             (hash_password(new), st.session_state.username))
                    conn.commit()
                    st.success("✅ رمز عبور تغییر کرد!")
                else:
                    st.error("❌ رمزهای جدید مطابقت ندارند")
            else:
                st.error("❌ رمز فعلی اشتباه است")

# === مسیریابی ===
if not st.session_state.logged_in:
    login_page()
else:
    home_page()

# === فوتر ===
st.markdown("---")
footer_col1, footer_col2 = st.columns(2)
with footer_col1:
    st.caption("🌐 مگا پلتفرم - نسخه 1.0")
with footer_col2:
    status = "🟢 آنلاین" if st.session_state.logged_in else "🔴 آفلاین"
    st.caption(f"{status} | {datetime.now().strftime('%H:%M')}")

# === اجرا ===
if __name__ == "__main__":
    pass
