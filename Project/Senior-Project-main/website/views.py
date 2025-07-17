from flask import Blueprint as bl, render_template, session, redirect, url_for, request, flash
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

views = bl('views', __name__)

@views.route('/')
def home():
    user = session.get('user')
    if not user:
        flash("Please log in first.", category="error")
        return redirect(url_for('auth.login'))

    itinerary = session.get('itinerary')
    return render_template('home.html', user=user, itinerary=itinerary)

# device = torch.device("cpu")

base_model_id = "unsloth/llama-3-8b-Instruct"
adapter_model_id = "VacationGenieSeniorProject2025/VacationGenie"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    device_map="auto",
    torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
)

model = PeftModel.from_pretrained(base_model, adapter_model_id)
model.eval()

@views.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    data = request.get_json()
    user_input = data.get("prompt", "").strip()

    if not user_input:
        return {"error": "Prompt is required."}, 400

    try:
        inputs = tokenizer(user_input, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
            )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Optionally save itinerary to session
        session['itinerary'] = generated_text

        return {"response": generated_text}

    except Exception as e:
        return {"error": f"Model generation failed: {str(e)}"}, 500
