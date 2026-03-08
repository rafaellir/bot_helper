import time
import logging

class BrowserActions:

    def __init__(self, page):
        self.page = page


    def handle_leitura(self):

        logging.info("📖 Leitura: clicando em 'Leia o item'")

        try:

            self.page.click("text=Leia o item", timeout=30000)

            time.sleep(30)

            logging.info("✅ Leitura completa")

        except Exception as e:

            logging.error(f"Erro na leitura: {e}")


    def handle_objetiva(self, option_text: str):

        logging.info(f"🎯 Objetiva: procurando alternativa '{option_text}'")

        index = ord(option_text.upper()) - ord('A')

        try:

            option = self.page.locator("[data-test-id='option']").nth(index)

            option.wait_for(state="visible", timeout=5000)

            option.scroll_into_view_if_needed()

            # clique direto via JS (mais confiável)
            self.page.evaluate("(el) => el.click()", option)

            time.sleep(0.4)

            logging.info(f"✅ Alternativa '{option_text}' marcada")

            return True

        except Exception as e:

            logging.error(f"❌ Erro ao marcar alternativa: {e}")

            return False


    def handle_discursiva(self, text: str):

        logging.info("✍️ Discursiva: preenchendo resposta")

        try:

            self.page.fill(
                "textarea, [placeholder*='resposta'], .resposta-texto",
                text or ""
            )

            time.sleep(1)

            # botão enviar resposta
            self.page.click("text=Enviar resposta", timeout=30000)

            logging.info("📤 Clicado em 'Enviar resposta'")

            time.sleep(1)

            # botão confirmar (versão que funciona com React)
            confirmar = self.page.locator(
                "button:has(p:has-text('Confirmar'))"
            )

            confirmar.wait_for(state="visible", timeout=10000)

            self.page.evaluate("(el) => el.click()", confirmar)

            logging.info("✅ Clicado em 'Confirmar'")

            time.sleep(1)

        except Exception as e:

            logging.error(f"❌ Erro na discursiva: {e}")