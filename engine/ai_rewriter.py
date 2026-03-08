from groq import Groq
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

PROMPT_TEMPLATE = """
Parafraseie a resposta abaixo mudando algumas palavras e a estrutura da frase,
mas mantendo exatamente o mesmo significado e as mesmas informações.

Resposta:
{texto}
"""

class AIRewriter:

    def __init__(self):
        self.client = Groq(
            api_key=""
        )

    def rewrite(self, texto: str) -> str:

        try:

            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "user",
                        "content": PROMPT_TEMPLATE.format(texto=texto)
                    }
                ],
                temperature=0.7,
                max_tokens=512,
                top_p=1
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:

            logging.error(f"Erro na IA: {e}")

            # fallback se a IA falhar
            return texto