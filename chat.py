# manualchat/chat.py
import requests

def generate_answer(question, context):
    prompt = f"""
Du er en teknisk ekspert. **Besvar udelukkende på dansk** Brug udelukkende information fra konteksten nedenfor til at besvare spørgsmålet.

Start altid med at tjekke tabeller og vedligeholdelsesafsnit, da de typisk indeholder præcise instruktioner og intervaller.

Svar kort og præcist. Hvis svaret ikke kan findes direkte i teksten, så sig: "Det fremgår ikke af manualen, men kig i nedenstående PDFer."

Kontekst:
{context}

Spørgsmål:
{question}

Svar:
""".strip()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "gemma:7b", "prompt": prompt, "stream": False}
    )

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "[FEJL] Kunne ikke hente svar fra Gemma."
