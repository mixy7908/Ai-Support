import json
import re
from openai import OpenAI
from wsgiref.simple_server import make_server

# ----------------------------
#   CONFIG
# ----------------------------
client = OpenAI(api_key="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")

BLOCK_WORDS = ["smm", "panel", "s.m.m", "pannel", "panal"]

def clean_text(text):
    t = text.lower()
    for w in BLOCK_WORDS:
        t = re.sub(rf"\b{w}\b", "Mixy Grow", t)
    return t


def bot_reply(user_msg):
    msg = clean_text(user_msg)

    # Fixed replies
    if any(x in msg for x in ["order", "complete nahi", "not complete"]):
        return "Sir 2-3 Ghante Wait Karo Aapka Order Complete Ho Jaye Ga 🙏"

    if "payment" in msg or "pay" in msg or "paisa" in msg:
        return "Payment Related Help Ke Liye Is Username Pe Message Kare: @ZoZyOx"

    # AI Response
    prompt = f"""
    Tum MixyGrow.Shop ke support agent ho.
    Tum kabhi bhi 'SMM Panel' ya smm related naam nahi loge.
    Agar user bole to tum usko 'Mixy Grow' likh kar reply doge.

    User Message: {msg}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# ---------------------------------------------------------
#   RENDER.com WSGI Server (auto works on Render deployment)
# ---------------------------------------------------------
def application(environ, start_response):
    if environ["REQUEST_METHOD"] == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
            body = environ["wsgi.input"].read(size)
            data = json.loads(body.decode("utf-8"))
            user_msg = data.get("message", "")

            reply = bot_reply(user_msg)

            res = json.dumps({"reply": reply}).encode("utf-8")
            start_response("200 OK", [("Content-Type", "application/json")])
            return [res]

        except Exception as e:
            start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
            return [str(e).encode("utf-8")]

    start_response("200 OK", [("Content-Type", "application/json")])
    return [b'{"status": "running"}']


# ---------------------------------------------------------
#   LOCAL RUN (for testing)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Bot Running on http://localhost:8000")
    with make_server("", 8000, application) as httpd:
        httpd.serve_forever()
