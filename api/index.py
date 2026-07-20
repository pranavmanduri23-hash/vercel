import os
from flask import Flask, redirect, url_for, session, request, render_template_string
from authlib.integrations.flask_client import OAuth
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "super-secret-random-string")

# Setup Discord OAuth2
oauth = OAuth(app)
discord = oauth.register(
    name='discord',
    client_id=os.getenv('DISCORD_CLIENT_ID'),
    client_secret=os.getenv('DISCORD_CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    api_base_url='https://discord.com/api/',
    client_kwargs={'scope': 'identify guilds'}
)

# Connect to MongoDB
def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client.zenith_guard

# --- PREMIUM CSS & ANIMATIONS ---
BASE_CSS = """
<style>
    :root { --bg: #06070a; --card: rgba(20, 22, 27, 0.6); --accent: #5865F2; --accent-glow: rgba(88, 101, 242, 0.4); --text: #dcddde; --text-bright: #ffffff; --glass-border: rgba(255, 255, 255, 0.08); }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', sans-serif; overflow-x: hidden; line-height: 1.6; }
    
    /* Keyframes */
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 60px, 0); } to { opacity: 1; transform: none; } }
    @keyframes float { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-20px) rotate(5deg); } }
    @keyframes pulseGlow { 0%, 100% { box-shadow: 0 0 30px var(--accent-glow); } 50% { box-shadow: 0 0 60px var(--accent-glow); } }
    @keyframes textGradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    @keyframes spinSlow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    
    .animate-up { animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .d-1 { animation-delay: 0.2s; } .d-2 { animation-delay: 0.4s; } .d-3 { animation-delay: 0.6s; } .d-4 { animation-delay: 0.8s; }

    /* Navbar */
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(6, 7, 10, 0.7); backdrop-filter: blur(16px); border-bottom: 1px solid var(--glass-border); position: fixed; width: 100%; top: 0; z-index: 1000; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.3rem; font-weight: 800; color: var(--text-bright); text-decoration: none; letter-spacing: -0.5px; }
    .btn { background: var(--accent); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.3s; display: inline-block; }
    .btn:hover { background: #4752c4; transform: translateY(-3px); box-shadow: 0 10px 25px var(--accent-glow); }
    .btn-ghost { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: #fff; }
    .btn-ghost:hover { background: rgba(255,255,255,0.1); box-shadow: none; }

    /* Hero Section */
    .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; text-align: center; padding: 100px 20px 0 20px; overflow: hidden; }
    .hero-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; background: radial-gradient(circle at 50% 0%, #1a1c25 0%, var(--bg) 60%); }
    .orb { position: absolute; border-radius: 50%; filter: blur(80px); z-index: -1; }
    .orb-1 { width: 400px; height: 400px; background: rgba(88, 101, 242, 0.15); top: 10%; left: 10%; animation: float 8s ease-in-out infinite; }
    .orb-2 { width: 300px; height: 300px; background: rgba(88, 101, 242, 0.1); bottom: 10%; right: 10%; animation: float 10s ease-in-out infinite reverse; }
    
    .hero-content { max-width: 800px; }
    .hero-badge { display: inline-block; padding: 8px 16px; background: rgba(88, 101, 242, 0.1); border: 1px solid rgba(88, 101, 242, 0.3); border-radius: 20px; font-size: 0.9rem; color: #a3acff; margin-bottom: 24px; }
    .hero h1 { font-size: 4.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 24px; letter-spacing: -3px; line-height: 1.1; }
    .gradient-text { background: linear-gradient(90deg, #ffffff, #5865F2, #8a93ff, #ffffff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: textGradient 4s linear infinite; }
    .hero p { font-size: 1.25rem; color: #8e9297; max-width: 600px; margin: 0 auto 40px auto; }
    .hero-btns { display: flex; gap: 15px; justify-content: center; margin-bottom: 60px; }
    
    /* Decorative Graphic */
    .shield-graphic { font-size: 8rem; margin-bottom: 40px; display: inline-block; animation: float 4s ease-in-out infinite; filter: drop-shadow(0 0 20px var(--accent-glow)); }

    /* Live Stats Bar */
    .stats-bar { display: flex; justify-content: center; gap: 60px; padding: 40px 0; border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); background: rgba(0,0,0,0.2); }
    .stat-item h2 { font-size: 2.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 5px; }
    .stat-item p { font-size: 0.9rem; color: #8e9297; letter-spacing: 1px; text-transform: uppercase; }

    /* Features */
    .features-section { padding: 100px 20px; max-width: 1200px; margin: 0 auto; }
    .section-title { text-align: center; font-size: 2.5rem; color: var(--text-bright); margin-bottom: 20px; font-weight: 800; }
    .section-subtitle { text-align: center; color: #8e9297; margin-bottom: 60px; font-size: 1.1rem; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .glass-card { background: var(--card); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); padding: 32px; border-radius: 16px; transition: 0.3s; position: relative; overflow: hidden; }
    .glass-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: 0; transition: 0.3s; }
    .glass-card:hover { transform: translateY(-8px); border-color: rgba(88, 101, 242, 0.3); background: rgba(20, 22, 27, 0.8); }
    .glass-card:hover::before { opacity: 1; }
    .card-icon { width: 50px; height: 50px; background: rgba(88, 101, 242, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 20px; }
    
    /* Dashboard Layout */
    .dash-container { display: flex; min-height: 100vh; }
    .sidebar { width: 260px; background: #0a0b0e; padding: 30px 0; border-right: 1px solid var(--glass-border); position: fixed; height: 100vh; }
    .sidebar-item { display: block; padding: 15px 30px; color: #8e9297; text-decoration: none; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
    .sidebar-item:hover, .sidebar-item.active { background: rgba(255,255,255,0.03); color: #fff; border-left-color: var(--accent); }
    .dash-content { margin-left: 260px; padding: 40px; width: calc(100% - 260px); }
    .dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid var(--glass-border); }
    .settings-card { background: var(--card); backdrop-filter: blur(16px); padding: 30px; border-radius: 12px; border: 1px solid var(--glass-border); margin-bottom: 30px; }
    .form-group { margin-bottom: 25px; }
    .form-group label { display: block; margin-bottom: 8px; color: var(--text-bright); font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input[type="text"] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #303136; background: #0a0b0e; color: var(--text); font-size: 1rem; transition: 0.2s; }
    .form-group input[type="text"]:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
    .switch { position: relative; display: inline-block; width: 50px; height: 28px; float: right; }
    .switch input { opacity: 0; width: 0; height: 0; }
    .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #303136; transition: .4s; border-radius: 28px; }
    .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
    input:checked + .slider { background-color: var(--accent); }
    input:checked + .slider:before { transform: translateX(22px); }
    .stat-card { background: var(--card); backdrop-filter: blur(16px); padding: 24px; border-radius: 12px; border: 1px solid var(--glass-border); text-align: center; }
    .alert { background: rgba(88, 101, 242, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(88, 101, 242, 0.4); margin-bottom: 20px; color: #fff; }
</style>
"""

# --- HTML TEMPLATES ---
HOME_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Zenith Guard - Ultimate Discord Protection</title></head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">🛡️ Zenith Guard</a>
        <div style="display: flex; gap: 15px; align-items: center;">
            {% if user %}
                <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="32" height="32" style="border-radius: 50%;">
                <a href="/dashboard" class="btn">Dashboard</a>
            {% else %}
                <a href="/login" class="btn">Login with Discord</a>
            {% endif %}
        </div>
    </nav>

    <div class="hero">
        <div class="hero-bg"></div>
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        
        <div class="hero-content">
            <div class="shield-graphic animate-up">🛡️</div>
            <div class="hero-badge animate-up d-1">✨ Next-Gen Discord Security</div>
            <h1 class="animate-up d-2"><span class="gradient-text">Protection that feels</span><br>impenetrable.</h1>
            <p class="animate-up d-3">Empower your community with advanced AI moderation, instant anti-raid defense, and seamless server management. Zenith Guard keeps your server safe 24/7.</p>
            <div class="hero-btns animate-up d-4">
                <a href="https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot" class="btn">Invite to Discord</a>
                {% if user %}
                <a href="/dashboard" class="btn btn-ghost">Go to Dashboard</a>
                {% else %}
                <a href="/login" class="btn btn-ghost">Learn More</a>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="stats-bar animate-up d-4">
        <div class="stat-item">
            <h2 id="stat-servers">{{ stats.servers }}+</h2>
            <p>Active Servers</p>
        </div>
        <div class="stat-item">
            <h2>{{ stats.users }}+</h2>
            <p>Users Protected</p>
        </div>
        <div class="stat-item">
            <h2>24/7</h2>
            <p>Uninterrupted</p>
        </div>
        <div class="stat-item">
            <h2>100%</h2>
            <p>Free Forever</p>
        </div>
    </div>

    <div class="features-section">
        <h2 class="section-title animate-up">Why choose Zenith Guard?</h2>
        <p class="section-subtitle animate-up d-1">A complete all-in-one solution for your Discord server.</p>
        
        <div class="grid-3">
            <div class="glass-card animate-up d-1">
                <div class="card-icon">🚨</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">AI Auto-Moderation</h3>
                <p>Our advanced AI filters spam, links, and toxic messages in real-time before they hit your server.</p>
            </div>
            <div class="glass-card animate-up d-2">
                <div class="card-icon">🛡️</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">Instant Anti-Raid</h3>
                <p>Detect and stop malicious raids instantly. Auto-lockdown protects your members and server integrity.</p>
            </div>
            <div class="glass-card animate-up d-3">
                <div class="card-icon">🎵</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">High-Quality Music</h3>
                <p>Seamless music playback from multiple sources with an advanced queue and audio filters system.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

DASH_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Dashboard - Zenith Guard</title></head>
<body>
    <div class="dash-container">
        <div class="sidebar">
            <a href="/dashboard" class="sidebar-item active">📊 Overview</a>
            <a href="/dashboard" class="sidebar-item">⚙️ General</a>
            <a href="/dashboard" class="sidebar-item">🛡️ Moderation</a>
            <a href="/dashboard" class="sidebar-item">🎵 Music</a>
            <a href="/" class="sidebar-item" style="position: absolute; bottom: 20px; width: 100%;">🏠 Back to Home</a>
        </div>
        <div class="dash-content">
            <div class="dash-header">
                <div>
                    <h1 style="color: #fff;">Server Overview</h1>
                    <p style="color: #8e9297;">Real-time data directly from your bot</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="40" height="40" style="border-radius: 50%;">
                    <a href="/logout" style="color: #8e9297; text-decoration: none;">Logout</a>
                </div>
            </div>

            {% if saved %}<div class="alert animate-up">✅ Settings saved successfully to the database!</div>{% endif %}

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div class="stat-card animate-up d-1">
                    <h2 style="color: var(--accent); margin-bottom: 5px;">{{ stats.servers }}</h2>
                    <p style="color: #8e9297; font-size: 0.9rem; text-transform: uppercase;">Live Servers</p>
                </div>
                <div class="stat-card animate-up d-2">
                    <h2 style="color: var(--accent); margin-bottom: 5px;">{{ stats.users }}</h2>
                    <p style="color: #8e9297; font-size: 0.9rem; text-transform: uppercase;">Live Users</p>
                </div>
            </div>

            <form action="/save_settings" method="POST">
                <div class="settings-card animate-up d-1">
                    <h3 style="color: #fff; margin-bottom: 20px;">⚙️ General Configuration</h3>
                    <div class="form-group">
                        <label>Command Prefix</label>
                        <input type="text" name="prefix" value="{{ settings.prefix }}" maxlength="3" required>
                    </div>
                    <div class="form-group">
                        <label>Welcome Message (Use {user} for new members)</label>
                        <input type="text" name="welcome_message" value="{{ settings.welcome_message }}" required>
                    </div>
                </div>
                <div class="settings-card animate-up d-2">
                    <h3 style="color: #fff; margin-bottom: 20px;">🛡️ Modules</h3>
                    <div class="form-group">
                        <label>Anti-Raid System <span class="switch"><input type="checkbox" name="anti_raid" {% if settings.anti_raid %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                    <div class="form-group">
                        <label>Music Player <span class="switch"><input type="checkbox" name="music" {% if settings.music %}checked{% endif %}><span class="slider"></span></span></label>
                    </div>
                </div>
                <button type="submit" class="btn animate-up d-3" style="width: 100%; padding: 15px; font-size: 1.1rem;">Save All Changes</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# --- ROUTES ---
@app.route("/")
def home():
    user = session.get('user')
    db = get_db()
    
    # Fetch LIVE Bot Stats for Homepage
    stats_doc = db.bot_stats.find_one({"_id": "live_stats"})
    if stats_doc:
        stats = {"servers": stats_doc.get("servers", 0), "users": stats_doc.get("users", 0)}
    else:
        stats = {"servers": "10K", "users": "50K"} # Fallback before bot connects to DB

    return render_template_string(HOME_HTML, user=user, stats=stats)

@app.route("/login")
def login():
    redirect_uri = url_for('callback', _external=True)
    return discord.authorize_redirect(redirect_uri)

@app.route("/callback")
def callback():
    token = discord.authorize_access_token()
    resp = discord.get('users/@me', token=token)
    session['user'] = resp.json()
    return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/')

@app.route("/dashboard")
def dashboard():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    db = get_db()
    
    # 1. Fetch LIVE Bot Stats
    stats_doc = db.bot_stats.find_one({"_id": "live_stats"})
    if stats_doc:
        stats = {"servers": stats_doc.get("servers", 0), "users": stats_doc.get("users", 0)}
    else:
        stats = {"servers": 0, "users": 0}

    # 2. Fetch Real User Settings from DB
    settings_doc = db.user_settings.find_one({"user_id": user['id']})
    if not settings_doc:
        settings = {"prefix": "!", "welcome_message": "Welcome {user}!", "anti_raid": False, "music": True}
    else:
        settings = {
            "prefix": settings_doc.get("prefix", "!"),
            "welcome_message": settings_doc.get("welcome_message", "Welcome!"),
            "anti_raid": settings_doc.get("anti_raid", False),
            "music": settings_doc.get("music", True)
        }
    
    saved = request.args.get('saved', False)
    return render_template_string(DASH_HTML, user=user, settings=settings, stats=stats, saved=saved)

@app.route("/save_settings", methods=['POST'])
def save_settings():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    db = get_db()
    
    # Save REAL settings to the database
    new_settings = {
        "user_id": user['id'],
        "prefix": request.form.get('prefix', '!'),
        "welcome_message": request.form.get('welcome_message', 'Welcome!'),
        "anti_raid": 'anti_raid' in request.form,
        "music": 'music' in request.form
    }
    
    db.user_settings.update_one({"user_id": user['id']}, {"$set": new_settings}, upsert=True)
    
    return redirect('/dashboard?saved=true')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
