from playwright.sync_api import Page, TimeoutError, Error
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LoginManager:
    def __init__(self, page: Page):
        self.page = page

    def login_atlas(self, email: str, password: str):
        try:
            self.page.goto("https://atlasedu.com.br", timeout=60000)
            time.sleep(1)
            self.page.wait_for_load_state("networkidle", timeout=60000)
            logging.info(f"Página inicial carregada: {self.page.url}")

            # Acessar
            self.page.get_by_role("link", name="Acessar", exact=True).click(timeout=60000)
            time.sleep(1)
            logging.info(f"URL após Acessar: {self.page.url}")

            # Aluno
            self.page.get_by_text("Aluno").first.click(timeout=60000)
            time.sleep(3)
            logging.info(f"URL após Aluno: {self.page.url}")

            # Botão Google no iframe
            google_btn = self.page.frame_locator('iframe[src*="accounts.google.com"]').locator(
                'xpath=//span[contains(text(),"Fazer Login com o Google")]').first
            logging.info(f"Matches Google button: {google_btn.count()}")
            google_btn.wait_for(state="visible", timeout=45000)
            google_btn.click(timeout=45000)
            logging.info("Clicado em 'Fazer Login com o Google'")

            # Form Google
            self.page.wait_for_selector("input[type=email]", timeout=60000)
            logging.info("Form Google carregado")

            # Usar outra conta
            try:
                self.page.get_by_text("Usar outra conta").click(timeout=10000)
            except TimeoutError:
                logging.info("Não apareceu 'Usar outra conta'")

            # Email
            self.page.fill("input[type=email]", email)
            self.page.get_by_role("button", name="Avançar").click(timeout=45000)  # Padronizado para "Próximo"
            time.sleep(3)  # Delay extra para transição

            # Senha
            self.page.wait_for_selector("input[type=password]", timeout=60000)
            self.page.fill("input[type=password]", password)
            self.page.get_by_role("button", name="Avançar").click(timeout=45000)
            logging.info("Clicado em 'Próximo' após senha")

            # Espera redirecionamento completo (sync robusto)
            self.page.wait_for_url("**atlasedu.com.br**", timeout=90000)  # Espera URL conter "atlasedu.com.br", 90s
            self.page.wait_for_load_state("networkidle", timeout=60000)
            logging.info(f"URL final após login: {self.page.url}")

            if "atlasedu.com.br" not in self.page.url.lower():
                raise ValueError(f"Login falhou - URL final: {self.page.url}")

            logging.info(f"Login bem-sucedido para {email}")
        except Exception as e:
            logging.error(f"Erro no login para {email}: {str(e)}")
            # Depurador seguro: Tente capturar antes de close
            try:
                self.page.screenshot(path="login_error_screenshot.png")
                with open("login_error_html.html", "w", encoding="utf-8") as f:
                    f.write(self.page.content())
            except Exception as depug_err:
                logging.warning(f"Falha ao capturar depurador: {str(depug_err)}")
            raise RuntimeError(f"Erro no login: {str(e)}")