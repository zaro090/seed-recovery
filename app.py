from flask import Flask, request, jsonify, render_template_string
from mnemonic import Mnemonic
import os

app = Flask(__name__)
mnemo = Mnemonic("english")
wordlist = mnemo.wordlist

HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>بازیابی کلمه BIP39</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Tahoma, sans-serif; background: #0f0f0f; color: #f0f0f0; min-height: 100vh; padding: 16px; line-height: 1.6; }
.container { max-width: 600px; margin: 0 auto; background: #1a1a1a; border-radius: 16px; padding: 20px; border: 1px solid #3a3a3a; }
h1 { color: #f5c542; font-size: 1.4rem; margin-bottom: 8px; text-align: center; }
.subtitle { text-align: center; color: #b0b0b0; font-size: 0.85rem; margin-bottom: 20px; }
label { display: block; font-weight: 600; font-size: 0.9rem; color: #f5c542; margin-bottom: 6px; margin-top: 16px; }
textarea { width: 100%; min-height: 120px; padding: 12px; border-radius: 10px; border: 1px solid #3a3a3a; background: #222; color: #f0f0f0; font-size: 0.95rem; font-family: monospace; direction: ltr; text-align: left; outline: none; }
textarea:focus { border-color: #f5c542; }
.options { display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap; }
.options button { flex: 1; min-width: 80px; padding: 10px; border: 1px solid #3a3a3a; border-radius: 10px; background: #333; color: #f0f0f0; cursor: pointer; font-size: 0.9rem; }
.options button.active { background: #f5c542; color: #121212; border-color: #f5c542; font-weight: 700; }
.search-btn { width: 100%; padding: 14px; border: none; border-radius: 50px; background: #f5c542; color: #121212; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 16px; }
.search-btn:disabled { background: #555; color: #999; }
.result { margin-top: 20px; padding: 16px; border-radius: 12px; background: #262626; border: 1px solid #3a3a3a; display: none; }
.result.show { display: block; }
.result h3 { color: #f5c542; font-size: 1rem; margin-bottom: 10px; }
.result-item { padding: 12px; margin: 8px 0; border-radius: 8px; background: #333; font-size: 0.85rem; word-break: break-word; font-family: monospace; direction: ltr; text-align: left; cursor: pointer; line-height: 1.8; }
.result-item:hover { background: #3a3a3a; }
.result-item.success { background: rgba(46,204,113,0.15); border: 1px solid #2ecc71; color: #2ecc71; }
.result-item.error { background: rgba(231,76,60,0.15); border: 1px solid #e74c3c; color: #e74c3c; }
.result-item.warning { background: rgba(243,156,18,0.15); border: 1px solid #f39c12; color: #f39c12; }
.result-item .found-word { color: #f5c542; font-weight: 700; text-decoration: underline; }
.stats { font-size: 0.8rem; color: #b0b0b0; margin-top: 10px; text-align: center; }
.loading { text-align: center; padding: 20px; color: #f5c542; display: none; }
.loading.show { display: block; }
.spinner { display: inline-block; width: 30px; height: 30px; border: 3px solid #333; border-top: 3px solid #f5c542; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.hint { font-size: 0.75rem; color: #888; margin-top: 6px; }
</style>
</head>
<body>
<div class="container">
<h1>بازیابی کلمه BIP39</h1>
<div class="subtitle">کلمه گم‌شده رو پیدا کن</div>
<label>تعداد کل کلمات سید:</label>
<div class="options">
<button id="btn12" class="active" onclick="setTotal(12)">12 کلمه</button>
<button id="btn24" onclick="setTotal(24)">24 کلمه</button>
</div>
<label>تعداد کلمات گم‌شده:</label>
<div class="options">
<button id="m1" class="active" onclick="setMissing(1)">1 گم‌شده</button>
<button id="m2" onclick="setMissing(2)">2 گم‌شده</button>
</div>
<label>عبارت ناقص:</label>
<textarea id="seedInput" placeholder="کلمات را با فاصله جدا کنید..."></textarea>
<div class="hint" id="hintText">باید 11 کلمه وارد کنی</div>
<button id="searchBtn" class="search-btn" onclick="startSearch()">شروع جستجو</button>
<div class="loading" id="loading">
<div class="spinner"></div>
<p style="margin-top:10px;">در حال جستجو...</p>
</div>
<div class="result" id="resultBox">
<h3>نتیجه:</h3>
<div id="resultContent"></div>
<div class="stats" id="statsBox"></div>
</div>
</div>
<script>
var totalWords = 12;
var missingCount = 1;
function setTotal(n) { totalWords = n; document.getElementById('btn12').classList.toggle('active', n === 12); document.getElementById('btn24').classList.toggle('active', n === 24); updateHint(); }
function setMissing(n) { missingCount = n; document.getElementById('m1').classList.toggle('active', n === 1); document.getElementById('m2').classList.toggle('active', n === 2); updateHint(); }
function updateHint() { var needed = totalWords - missingCount; document.getElementById('hintText').textContent = 'باید ' + needed + ' کلمه وارد کنی'; }
async function startSearch() {
  var input = document.getElementById('seedInput').value.trim();
  var words = input.split(/\\s+/).filter(function(w) { return w.length > 0; });
  var needed = totalWords - missingCount;
  if (words.length !== needed) { alert('باید دقیقاً ' + needed + ' کلمه وارد کنی. الان ' + words.length + ' کلمه دادی.'); return; }
  document.getElementById('searchBtn').disabled = true;
  document.getElementById('loading').classList.add('show');
  document.getElementById('resultBox').classList.remove('show');
  try {
    var res = await fetch('/search', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({words: words, total: totalWords, missing: missingCount}) });
    var data = await res.json();
    document.getElementById('loading').classList.remove('show');
    document.getElementById('searchBtn').disabled = false;
    var box = document.getElementById('resultBox');
    var content = document.getElementById('resultContent');
    box.classList.add('show');
    content.innerHTML = '';
    if (data.error) { content.innerHTML = '<div class="result-item error">' + data.error + '</div>'; }
    else if (data.found.length === 0) { content.innerHTML = '<div class="result-item error">هیچ ترکیبی پیدا نشد.</div>'; }
    else {
      if (data.found.length === 1) { content.innerHTML = '<div class="result-item success">عبارت کامل پیدا شد (کلمه گم‌شده با رنگ زرد مشخص شده):</div>'; }
      else { content.innerHTML = '<div class="result-item warning">' + data.found.length + ' عبارت پیدا شد (کلمه گم‌شده با رنگ زرد):</div>'; }
      for (var i = 0; i < data.found.length; i++) { content.innerHTML += '<div class="result-item success">' + data.found[i] + '</div>'; }
    }
    document.getElementById('statsBox').textContent = 'تعداد کل نتایج: ' + data.found.length;
  } catch (e) {
    document.getElementById('loading').classList.remove('show');
    document.getElementById('searchBtn').disabled = false;
    alert('خطا: ' + e.message);
  }
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    words = data.get('words', [])
    total = data.get('total', 24)
    missing = data.get('missing', 1)
    if len(words) + missing != total:
        return jsonify({'error': 'تعداد کلمات اشتباهه', 'found': []})
    for w in words:
        if w not in wordlist:
            return jsonify({'error': 'کلمه ' + w + ' توی لیست BIP39 نیست', 'found': []})
    found = []
    if missing == 1:
        for word in wordlist:
            candidate = words + [word]
            if mnemo.check(" ".join(candidate)):
                highlighted = []
                for w in candidate:
                    if w == word:
                        highlighted.append('<span class="found-word">' + w + '</span>')
                    else:
                        highlighted.append(w)
                found.append(" ".join(highlighted))
    elif missing == 2:
        for w1 in wordlist:
            for w2 in wordlist:
                candidate = words + [w1, w2]
                if mnemo.check(" ".join(candidate)):
                    highlighted = []
                    for w in candidate:
                        if w == w1 or w == w2:
                            highlighted.append('<span class="found-word">' + w + '</span>')
                        else:
                            highlighted.append(w)
                    found.append(" ".join(highlighted))
    else:
        return jsonify({'error': 'فقط 1 یا 2 کلمه گم‌شده پشتیبانی می‌شه', 'found': []})
    return jsonify({'found': found, 'error': None})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
