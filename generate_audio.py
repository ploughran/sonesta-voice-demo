"""
Pre-generate ElevenLabs TTS audio for each line in the TrueNorth conversation.

Usage:
    ELEVENLABS_API_KEY=sk_xxx python3 generate_audio.py

Outputs:
    ./audio/line-0.mp3 ... ./audio/line-N.mp3  (always overwritten)

Notes:
- Always regenerates every file — existing mp3s are overwritten.
- Uses Sarah for the agent and Brian for the customer by default.
"""

import os
import sys
import json
import urllib.request
import urllib.error

API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    sys.exit("ELEVENLABS_API_KEY env var is required.")

# Voices
SARAH = "EXAVITQu4vr4xnSDxMaL"   # agent
BRIAN = "nPczCjzI2devNBz1zQrb"   # customer
MODEL = "eleven_turbo_v2_5"

LINES = [
    (SARAH, "Hi, you've reached TrueNorth Services. I'm your virtual assistant. Could I have your name to get started?"),
    (BRIAN, "Hi, this is Marcus Landry."),
    (SARAH, "Thanks, Marcus — one moment while I pull up your account."),
    (SARAH, "Got it, I have your account here."),
    (SARAH, "Thank you for calling. For your security, can you please confirm the last 4 digits of the billing card on file?"),
    (BRIAN, "Sure, it's 4892."),
    (SARAH, "Absolutely, Marcus. Are you calling about your most recent order?"),
    (SARAH, "Hi Marcus, I see you contacted us recently about a billing question and we applied a credit. Are you calling about something related to that, or a new issue?"),
    (BRIAN, "Actually, yes. I appreciate the credit, but I want to talk about that quarterly upcharge. I want it permanently removed from my contract going forward.."),
    (SARAH, "I understand completely. Let me review your contract terms and the specific add-on in question…"),
    (SARAH, "I can see this is the seasonal treatment add-on included in your renewed contract. You're asking for a permanent removal, which would require a contract modification."),
    (SARAH, "Given your 3-year tenure with us and that you've contacted us twice about billing in the past few months, I'm going to connect you directly with our customer retention team. They have the authority to modify your contract and can work out the best solution for you."),
    (BRIAN, "Oh that sounds great, thanks!"),
    (SARAH, "One moment please."),
]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(OUT_DIR, exist_ok=True)


def synthesize(voice_id: str, text: str, out_path: str) -> None:
    payload = {
        "text": text,
        "model_id": MODEL,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
    }
    req = urllib.request.Request(
        url=f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        sys.exit(f"ElevenLabs HTTP {e.code} for {os.path.basename(out_path)}: {body}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error: {e}")

    with open(out_path, "wb") as f:
        f.write(audio)


def main() -> None:
    for i, (voice, text) in enumerate(LINES):
        out = os.path.join(OUT_DIR, f"line-{i}.mp3")
        speaker = "Sarah (agent)" if voice == SARAH else "Brian (customer)"
        snippet = text[:70].replace("\n", " ") + ("…" if len(text) > 70 else "")
        print(f"  [tts ] line-{i}.mp3  {speaker:18s}  {snippet}")
        synthesize(voice, text, out)
    print(f"\nDone. {len(LINES)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
