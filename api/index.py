# -*- coding: utf-8 -*-
import os
from flask import Flask, redirect, url_for, session, request, render_template_string
from authlib.integrations.flask_client import OAuth

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

# --- PREMIUM CSS & ANIMATIONS ---
BASE_CSS = """
<style>
    :root { --bg: #050810; --bg-2: #0a0f1c; --card: rgba(15, 23, 42, 0.6); --gold: #fbbf24; --gold-glow: rgba(251, 191, 36, 0.4); --blue: #3b82f6; --blue-glow: rgba(59, 130, 246, 0.4); --text: #e2e8f0; --text-bright: #ffffff; --glass-border: rgba(255, 255, 255, 0.1); }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body { background-color: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', sans-serif; overflow-x: hidden; line-height: 1.6; position: relative; }
    body::before { content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px); background-size: 40px 40px; z-index: -2; pointer-events: none; animation: gridMove 20s linear infinite; }
    @keyframes gridMove { 0% { background-position: 0 0; } 100% { background-position: 40px 40px; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 60px, 0) scale(0.95); } to { opacity: 1; transform: none; } }
    @keyframes float { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-20px) rotate(5deg); } }
    @keyframes shimmer { 0% { background-position: -200% center; } 100% { background-position: 200% center; } }
    .animate-up { animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) both; }
    .d-1 { animation-delay: 0.2s; } .d-2 { animation-delay: 0.4s; } .d-3 { animation-delay: 0.6s; } .d-4 { animation-delay: 0.8s; }
    .nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 50px; background: rgba(5, 8, 16, 0.8); backdrop-filter: blur(16px); border-bottom: 1px solid var(--glass-border); position: fixed; width: 100%; top: 0; z-index: 1000; }
    .nav-logo { display: flex; align-items: center; gap: 10px; font-size: 1.3rem; font-weight: 800; color: var(--text-bright); text-decoration: none; letter-spacing: -0.5px; }
    .nav-logo span { color: var(--gold); }
    .btn { background: var(--blue); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; border: none; cursor: pointer; transition: 0.3s; display: inline-block; }
    .btn:hover { background: #2563eb; transform: translateY(-3px); box-shadow: 0 10px 25px var(--blue-glow); }
    .btn-gold { background: linear-gradient(135deg, var(--gold), #f59e0b); color: #050810; font-weight: 800; }
    .btn-gold:hover { box-shadow: 0 10px 25px var(--gold-glow); }
    .btn-ghost { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: #fff; }
    .btn-ghost:hover { background: rgba(255,255,255,0.1); box-shadow: none; }
    .hero { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; text-align: center; padding: 100px 20px 0 20px; overflow: hidden; }
    .orb { position: absolute; border-radius: 50%; filter: blur(100px); z-index: -1; }
    .orb-blue { width: 500px; height: 500px; background: rgba(59, 130, 246, 0.15); top: 10%; left: 10%; animation: float 8s ease-in-out infinite; }
    .orb-gold { width: 400px; height: 400px; background: rgba(251, 191, 36, 0.1); bottom: 10%; right: 10%; animation: float 10s ease-in-out infinite reverse; }
    .hero-content { max-width: 800px; }
    .hero-badge { display: inline-block; padding: 8px 16px; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.3); border-radius: 20px; font-size: 0.9rem; color: var(--gold); margin-bottom: 24px; }
    .hero h1 { font-size: 4.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 24px; letter-spacing: -3px; line-height: 1.1; }
    .gradient-text { background: linear-gradient(90deg, #ffffff, #3b82f6, #fbbf24, #ffffff); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 3s linear infinite; }
    .hero p { font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto 40px auto; }
    .hero-btns { display: flex; gap: 15px; justify-content: center; margin-bottom: 60px; }
    .shield-graphic { font-size: 6rem; margin-bottom: 40px; display: inline-block; animation: float 4s ease-in-out infinite; filter: drop-shadow(0 0 20px var(--blue-glow)); }
    .stats-bar { display: flex; justify-content: center; gap: 60px; padding: 40px 0; border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); background: rgba(0,0,0,0.3); backdrop-filter: blur(8px); }
    .stat-item h2 { font-size: 2.5rem; font-weight: 800; color: var(--text-bright); margin-bottom: 5px; }
    .stat-item h2 span { color: var(--gold); }
    .stat-item p { font-size: 0.9rem; color: #94a3b8; letter-spacing: 1px; text-transform: uppercase; }
    .features-section { padding: 100px 20px; max-width: 1200px; margin: 0 auto; }
    .section-title { text-align: center; font-size: 2.5rem; color: var(--text-bright); margin-bottom: 20px; font-weight: 800; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
    .glass-card { background: var(--card); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); padding: 32px; border-radius: 16px; transition: 0.3s; position: relative; overflow: hidden; }
    .glass-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--gold), transparent); opacity: 0; transition: 0.3s; }
    .glass-card:hover { transform: translateY(-8px); border-color: rgba(251, 191, 36, 0.3); }
    .glass-card:hover::before { opacity: 1; }
    .card-icon { width: 50px; height: 50px; background: rgba(59, 130, 246, 0.1); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 20px; border: 1px solid var(--glass-border); }
</style>
"""

HOME_HTML = BASE_CSS + """
<!DOCTYPE html>
<html>
<head><title>Zenith Guard - Ultimate Discord AI Protection</title></head>
<body>
    <nav class="nav">
        <a href="/" class="nav-logo">🛡️ Zenith <span>Guard</span></a>
        <div style="display: flex; gap: 15px; align-items: center;">
            <a href="/login" class="btn">Login</a>
            <a href="https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot" class="btn btn-gold">Invite Bot</a>
        </div>
    </nav>

    <div class="hero">
        <div class="orb orb-blue"></div>
        <div class="orb orb-gold"></div>
        
        <div class="hero-content">
            <div class="shield-graphic animate-up">🛡️</div>
            <div class="hero-badge animate-up d-1">✨ Powered by Quantum AI Technology</div>
            <h1 class="animate-up d-2"><span class="gradient-text">Zenith Guard</span><br>The Ultimate Shield</h1>
            <p class="animate-up d-3">Armed with <b>830+ commands</b> and next-generation AI, Zenith Guard predicts and eliminates threats before they even happen. The absolute pinnacle of Discord server security and management.</p>
            <div class="hero-btns animate-up d-4">
                <a href="https://discord.com/oauth2/authorize?client_id=YOUR_BOT_ID_HERE&permissions=8&scope=bot" class="btn btn-gold">Invite to Discord</a>
                <a href="/login" class="btn btn-ghost">Dashboard</a>
            </div>
        </div>
    </div>

    <div class="stats-bar animate-up d-4">
        <div class="stat-item">
            <h2><span>1K+</span></h2>
            <p>Users Protected</p>
        </div>
        <div class="stat-item">
            <h2><span>830+</span></h2>
            <p>Ultimate Commands</p>
        </div>
        <div class="stat-item">
            <h2><span>24/7</span></h2>
            <p>Uninterrupted</p>
        </div>
        <div class="stat-item">
            <h2><span>100%</span></h2>
            <p>Free Forever</p>
        </div>
    </div>

    <div class="features-section">
        <h2 class="section-title animate-up">Why choose <span style="color: var(--gold);">Zenith Guard</span>?</h2>
        <div class="grid-3" style="margin-top: 40px;">
            <div class="glass-card animate-up d-1">
                <div class="card-icon">🧠</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">Quantum AI Auto-Mod</h3>
                <p>Our hyper-advanced AI reads messages before they are sent, instantly neutralizing spam, toxicity, and raids with 99.9% accuracy.</p>
            </div>
            <div class="glass-card animate-up d-2">
                <div class="card-icon">⚡</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">Lightspeed Anti-Raid</h3>
                <p>Atomizes malicious bot raids in milliseconds. Automatic server lockdowns and threat elimination at lightspeed.</p>
            </div>
            <div class="glass-card animate-up d-3">
                <div class="card-icon">🎵</div>
                <h3 style="color: #fff; margin-bottom: 10px; font-size: 1.2rem;">Ultra-HD Music</h3>
                <p>Experience studio-quality, lossless audio playback with an advanced queue system and 50+ audio filters.</p>
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
    <div style="min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px;">
        <h1 style="color: #fff; font-size: 3rem; margin-bottom: 20px;" class="animate-up">Welcome, {{ user.username }}!</h1>
        <img src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png" width="120" height="120" style="border-radius: 50%; margin-bottom: 30px; border: 4px solid var(--gold);" class="animate-up d-1">
        <p style="color: #94a3b8; max-width: 500px; margin-bottom: 40px;" class="animate-up d-2">You are successfully logged in. The advanced control panel is currently undergoing a quantum upgrade.</p>
        <a href="/" class="btn btn-ghost animate-up d-3">Back to Home</a>
        <a href="/logout" class="btn animate-up d-3" style="margin-left: 15px;">Logout</a>
    </div>
</body>
</html>
"""

# --- ROUTES ---
@app.route("/")
def home():
    user = session.get('user')
    return render_template_string(HOME_HTML, user=user)

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
    return render_template_string(DASH_HTML, user=user)
