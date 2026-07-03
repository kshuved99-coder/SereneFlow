import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Explicitly look for and load a local .env file if it exists
load_dotenv()

# Configures Flask to look upward precisely into the Vercel architecture layer
app = Flask(__name__, template_folder='../templates')

# Safety Trigger Words for Mode 3 (Smart Resource Router) 
CRISIS_KEYWORDS = ["suicide", "harm", "kill", "die", "hurt myself", "end my life", "panic attack", "cannot breathe"]

def get_groq_client():
    """Initializes the Groq Client safely."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

@app.route('/')
def home():
    """Serves the primary unified sanctuary application interface workspace."""
    return render_template(
        'index.html',
        supabase_url=os.environ.get("SUPABASE_URL", ""),
        supabase_anon_key=os.environ.get("SUPABASE_ANON_KEY", "")
    )

@app.route('/api/chat', methods=['POST'])
def chat_companion():
    """Mode 1: Best Friend & Deep Listening Companion (Supports History & Vitals)"""
    data = request.json or {}
    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    heart_rate = data.get("heart_rate", "")
    sleep_hours = data.get("sleep_hours", "")
    stress_scale = data.get("stress_scale", "")
    
    if not user_message and not history:
        return jsonify({"reply": "I'm right here listening. Tell me what's on your mind."}), 400

    safety_triggered = any(keyword in user_message.lower() for keyword in CRISIS_KEYWORDS)

    client = get_groq_client()
    if not client:
        return jsonify({
            "reply": "Groq API Configuration missing. Please verify your Environment Variables.",
            "safety_triggered": safety_triggered
        })

    try:
        vitals_context = ""
        if heart_rate or sleep_hours or stress_scale:
            vitals_context = f" (For your context only, their wearable metrics show: Heart Rate: {heart_rate} BPM, Sleep: {sleep_hours}h, Stress: {stress_scale}/10. Keep this in mind but don't be robotic about it.)"

        system_prompt = (
            "You are Elowen, the user's deeply supportive, validating, and empathetic companion "
            "Your primary role is to just listen, validate their feelings warmly, "
            "Give thoughtful feedback, but dont seem pushy "
            f"and avoid sounding like an AI assistant or a textbook corporate coach. or being pushy "
            f"{vitals_context} "
            "CRITICAL: Never provide clinical/medical diagnoses or medical advice. "
            "Keep answers natural, comforting, conversational, and concise (under 3 sentences) so it feels like a real chat.don't keep conversations long too long ask them do you want to keep chatting."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.get("role"), "content": msg.get("content")})
        
        if not history or history[-1].get("content") != user_message:
            messages.append({"role": "user", "content": user_message})
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.8,
            max_tokens=250
        )
        ai_reply = completion.choices[0].message.content
        return jsonify({"reply": ai_reply, "safety_triggered": safety_triggered})
        
    except Exception as e:
        return jsonify({"reply": f"Engine error handled: {str(e)}", "safety_triggered": safety_triggered}), 500

@app.route('/api/stress-plan', methods=['POST'])
def stress_planner():
    """Mode 2: Stress Metric & Action Planner"""
    data = request.json or {}
    stress_scale = data.get("stress_scale", 5)
    sleep_hours = data.get("sleep_hours", 7)
    heart_rate = data.get("heart_rate", "")

    client = get_groq_client()
    if not client:
        return jsonify({"plan": "Groq config token is unavailable."})

    vitals_context = f", and a resting heart rate of {heart_rate} bpm" if heart_rate else ""
    
    prompt = (
        f"Generate an immediate, comforting, 3-step markdown cooldown action plan for an individual experiencing "
        f"a Level {stress_scale}/10 stress state, who slept only {sleep_hours} hours last night{vitals_context}. "
        f"Include one actionable sensory grounding guide. Keep it short."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a calming wellness coach specialized in immediate stress reduction."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=500
        )
        return jsonify({"plan": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"plan": f"Could not construct tactical guide: {str(e)}"}), 500

@app.route('/api/sleep-analysis', methods=['POST'])
def sleep_analyser():
    """Mode 3: Advanced Sleep Pattern Analytics Architecture"""
    data = request.json or {}
    hours = data.get("hours", 7)
    quality = data.get("quality", 70)
    consistency = data.get("consistency", "variable")

    client = get_groq_client()
    if not client:
        return jsonify({"analysis": "Groq API environment link unavailable. Check config."}), 500

    prompt = (
        f"You are a specialized sleep coach analyzing wearable health data profile graphs ensuring better sleep and overall health.\n"
        f"User Metrics Profile:\n"
        f"- Total Rest Duration: {hours} hours\n"
        f"- Deep/REM Quality Index: {quality}%\n"
        f"- Circadian Bedtime Schedule Consistency: {consistency}\n\n"
        f"Provide a 3-sentence maximum breakdown pinpointing exactly how their sleep architecture impacts daytime stress levels. "
        f"Provide one clear, practical adjustment suggestion to optimize recovery."
    )

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a brief, encouraging health tech coach focusing on circadian clock mechanics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        return jsonify({"analysis": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"analysis": f"Sleep metrics analytics processing error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)