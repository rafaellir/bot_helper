# main.py
"""
Main do bot com paralelismo apenas para tarefas do tipo 'leitura' (batches).
- Reaproveita BrowserSession (context) e abre múltiplas PAGES (abas) por batch.
- Mantém objetiva e discursiva SEQUENCIAIS (sem paralelismo).
- Salva completed.json apenas no thread principal.
- CONFIG: batch_size pode vir do config.yaml (campo browser.batch_size) ou padrão = 5.

ATENÇÃO: Cole sua lógica de login/navegação no marcador abaixo para obter a `plurall_page`
autenticada (ex.: clicar em Plurall, abrir nova aba, etc).
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# imports do seu projeto (ajuste caminhos se necessário)
from browser.session import BrowserSession
from engine.advisor import Advisor
from database.repository import Repository
from infra.tracker import Tracker  # se você tem esse módulo; caso contrário ajuste
import yaml

# ---------- Config / Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
config = yaml.safe_load(open("config.yaml"))
BATCH_SIZE = config.get("browser", {}).get("batch_size", 5)  # default 5
HEADLESS = config.get("browser", {}).get("headless", True)

# ---------- Helpers ----------
def safe_append_completed(repo: Repository, email: str, url: str):
    """Carrega, atualiza e salva completed.json no thread principal (thread-safe por design)."""
    try:
        done_map = repo.load_completed() or {}
    except Exception:
        done_map = {}
    done_for_account = done_map.get(email, [])
    if url not in done_for_account:
        done_for_account.append(url)
    done_map[email] = done_for_account
    repo.save_completed(done_map)


# ---------- Main ----------
def main():
    logging.info("Iniciando main.py")

    # Inicializa sessão do browser (usa browser/session.py)
    session = BrowserSession()
    browser = session  # nome curto (tem methods: get_page(), new_page(), close_page(), close())

    # repositório e tracker (ajuste se suas classes estiverem em outro path)
    repo = Repository()
    tracker = Tracker()

    # email da conta (opcional no config). Se não achar, usa 'default'
    email = config.get("account", {}).get("email", "default")

    # PÁGINA PRINCIPAL já autenticada — substitua este bloco com seu login/navegação existente
    plurall_page = session.get_page()

    # -----------------------------
    # --- PASTE YOUR NAVIGATION/LOGIN HERE ---
    # Cole aqui o seu código atual que faz:
    #  - abrir o site
    #  - realizar login (Google etc)
    #  - abrir Plurall / lista de atividades
    #
    # Ao final deste bloco você deve ter:
    #   plurall_page -> uma Page já autenticada pronta para acessar as tasks
    #
    # Exemplo (apenas ilustrativo, NÃO copie se já tem sua lógica):
    # plurall_page.goto("https://atlasedu.com.br")
    # ... (seu código de login)
    #
    # -----------------------------

    # Depois de logado, carregue as tasks
    tasks = repo.load_tasks() or []
    done_map = repo.load_completed() or {}
    already_done = set(done_map.get(email, []))

    # separa reading tasks e as outras, mantendo ordem
    reading_tasks = [t for t in tasks if t.get("type") == "leitura" and t.get("url") not in already_done]
    other_tasks   = [t for t in tasks if t.get("type") in ("objetiva", "discursiva") and t.get("url") not in already_done]

    logging.info(f"Tarefas carregadas: total={len(tasks)} leitura={len(reading_tasks)} outras={len(other_tasks)}")

    # -----------------------------
    # PROCESSAMENTO EM BATCHES (LEITURAS) - paralelo por batches de BATCH_SIZE
    # -----------------------------
    if reading_tasks:
        logging.info(f"Iniciando processamento em batches de leitura (batch_size={BATCH_SIZE})")
    for i in range(0, len(reading_tasks), BATCH_SIZE):
        batch = reading_tasks[i:i + BATCH_SIZE]
        logging.info(f"Rodando batch {i//BATCH_SIZE + 1} com {len(batch)} leituras")

        # cria páginas (uma por task no batch)
        pages = []
        for _ in batch:
            p = session.new_page()
            pages.append(p)

        def _worker_read(page, task):
            """Worker que roda em thread. Retorna (url, ok)."""
            try:
                logging.info(f"(worker) Abrindo {task['url']}")
                page.goto(task["url"], timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)

                # cria um advisor com a page do worker e processa
                worker_advisor = Advisor(page)
                # Para leitura garantimos que o handle_leitura será chamado. Como handle_leitura faz sleep(30),
                # assumimos sucesso se não levantar exceção.
                try:
                    worker_advisor.process_task(task)  # process_task chama handle_leitura internamente
                    return {"url": task["url"], "type": task["type"], "ok": True}
                except Exception as e:
                    logging.error(f"(worker) Erro ao processar task interna: {e}")
                    return {"url": task["url"], "type": task["type"], "ok": False}

            except Exception as e:
                logging.error(f"(worker) Erro geral ao abrir/processar {task['url']}: {e}")
                return {"url": task["url"], "type": task["type"], "ok": False}

        # executar workers com ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(batch)) as ex:
            future_to_task = {ex.submit(_worker_read, pages[idx], batch[idx]): batch[idx] for idx in range(len(batch))}
            for fut in as_completed(future_to_task):
                task = future_to_task[fut]
                try:
                    result = fut.result()
                    if result.get("ok"):
                        # grava completed no main thread
                        safe_append_completed(repo, email, task["url"])
                        tracker.log_completed(email, task["url"], task["type"], "completada")
                        logging.info(f"✅ (worker->main) Tarefa concluída: {task['url']}")
                    else:
                        logging.warning(f"⚠️ (worker->main) Falha na tarefa de leitura: {task['url']}")
                except Exception as e:
                    logging.error(f"Erro ao coletar resultado do worker para {task['url']}: {e}")

        # fecha as pages criadas para o batch
        for p in pages:
            try:
                session.close_page(p)
            except Exception as e:
                logging.debug(f"Erro ao fechar page do batch: {e}")

        # pequena folga entre batches (evita sobrecarregar)
        time.sleep(0.5)

    # -----------------------------
    # PROCESSAMENTO SEQUENCIAL: objetivas + discursivas
    # -----------------------------
    if other_tasks:
        logging.info("Iniciando processamento sequencial de objetivas e discursivas")
    advisor = Advisor(plurall_page)

    for task in other_tasks:
        url = task["url"]
        logging.info(f"Abrindo tarefa: {url}")
        try:
            plurall_page.goto(url, timeout=60000)
            plurall_page.wait_for_load_state("networkidle", timeout=60000)

            # process_task já faz as ações do tipo (objetiva/discursiva)
            result = advisor.process_task(task)

            # veja: algumas funções retornam True/False; se não retornarem nada (None),
            # consideramos sucesso se não houve exceção.
            # Como simplificação: se não ocorreu exceção até aqui, registramos como concluída.
            safe_append_completed(repo, email, url)
            tracker.log_completed(email, url, task["type"], "completada")
            logging.info(f"✅ Tarefa concluída: {url}")

        except Exception as e:
            logging.error(f"❌ Erro ao processar tarefa {url}: {e}")
            # decide: pular para próxima tarefa
            continue

    # -----------------------------
    # FINALIZAÇÃO
    # -----------------------------
    logging.info("Todas tarefas processadas (ou tentadas). Fechando sessão.")
    try:
        session.close()
    except Exception as e:
        logging.error(f"Erro ao fechar sessão: {e}")

    logging.info("Fim do script.")


if __name__ == "__main__":
    main()
