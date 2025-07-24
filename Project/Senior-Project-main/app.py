# from flask import Flask, render_template, request
# from transformers import AutoTokenizer, AutoModelForCausalLM 
# import torch 


# app = Flask(__name__)

# from transformers import AutoTokenizer, AutoModelForCausalLM
# import torch

# model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

# tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=True)
# model = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     device_map="auto",  # Or {"": 0} if single-GPU
#     torch_dtype=torch.float16,
#     load_in_4bit=True  # Optional: reduce VRAM using bitsandbytes
# )
# model.eval()


# @app.route('/dashboard', methods=['GET', 'POST'])
# def dashboard():
#     if request.method == 'POST':
#         origin = request.form['origin']
#         destination = request.form['destination']
#         departure_date = request.form['departureDate']
#         return_date = request.form['returnDate']

#         # Create a prompt for GPT-2
#         prompt = (
#             f"Create a detailed daily itinerary for a trip from {origin} to {destination} "
#             f"starting on {departure_date} and returning on {return_date}."
#         )

#         # Tokenize and generate text
#         inputs = tokenizer(prompt, return_tensors="pt").to(device)
#         outputs = model.generate(
#             **inputs,
#             max_length=200,
#             num_return_sequences=1,
#             no_repeat_ngram_size=2,
#             do_sample=True,
#             top_p=0.9,
#             temperature=0.8,
#         )

#         generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#         # Convert generated text into list items for display
#         itinerary = [line.strip() for line in generated_text.split('.') if line.strip()]

#         return render_template('home.html', itinerary=itinerary)

#     return render_template('dashboard.html')

# @app.route('/')
# def home():
#     return render_template('home.html', itinerary=None)

# if __name__ == "__main__":
#     app.run(debug=True)
