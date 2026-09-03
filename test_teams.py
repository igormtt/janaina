import os

import requests

from dotenv import load_dotenv

load_dotenv()


POWER_AUTOMATE_URL = os.getenv("POWER_AUTOMATE_URL")


TEST_CASES = [
    {
        "recipient": "t-igor.geraldo@cni.com.br",
        "original_assignee": "Leandro Cesar De Aguiar Garcia",
        "message": (
            "Olá, Leandro! Tudo bem?\n\n"
            "Identificamos alguns chamados sob sua "
            "responsabilidade que estão há 3 dias ou mais "
            "sem atualização:\n\n"
            "• CNI-164883 — 27 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-164883\n\n"
            "• CNI-164936 — 27 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-164936\n\n"
            "Quando possível, poderia verificar os chamados "
            "e atualizar o andamento, por favor?\n\n"
            "Obrigado! 😊"
        ),
    },
    {
        "recipient": "t-janaina.lima@cni.com.br",
        "original_assignee": "Jessica Teles Da Costa",
        "message": (
            "Olá, Jessica! Tudo bem?\n\n"
            "Identificamos alguns chamados sob sua "
            "responsabilidade que estão há 3 dias ou mais "
            "sem atualização:\n\n"
            "• CNI-184005 — 3 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-184005\n\n"
            "Quando possível, poderia verificar o chamado "
            "e atualizar o andamento, por favor?\n\n"
            "Obrigado! 😊"
        ),
    },
    {
        "recipient": "t-danilo.rodrigues@cni.com.br",
        "original_assignee": "Greicy Kelly de Araujo Lima Damasceno",
        "message": (
            "Olá, Greicy! Tudo bem?\n\n"
            "Identificamos alguns chamados sob sua "
            "responsabilidade que estão há 3 dias ou mais "
            "sem atualização:\n\n"
            "• CNI-175924 — 107 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-175924\n\n"
            "• CNI-191990 — 10 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-191990\n\n"
            "• CNI-192235 — 7 dias sem atualização\n"
            "https://sistemacni.atlassian.net/browse/CNI-192235\n\n"
            "Quando possível, poderia verificar os chamados "
            "e atualizar o andamento, por favor?\n\n"
            "Obrigado! 😊"
        ),
    },
]


def send_test_message(
    recipient: str,
    original_assignee: str,
    message: str,
):

    payload = {
        "recipient": recipient,
        "original_assignee": original_assignee,
        "message": message,
    }

    response = requests.post(
        POWER_AUTOMATE_URL,
        json=payload,
        timeout=30,
    )

    print(f"{recipient} -> " f"Status {response.status_code}")

    if response.text:
        print(f"Resposta: {response.text}")

    response.raise_for_status()


def main():

    if not POWER_AUTOMATE_URL:
        raise RuntimeError("POWER_AUTOMATE_URL nao configurada no .env")

    print()
    print("=" * 60)
    print("TESTE DE ENVIO PARA O TEAMS")
    print("=" * 60)
    print()

    for test_case in TEST_CASES:

        recipient = test_case["recipient"]

        print(f"Enviando mensagem para " f"{recipient}...")

        try:
            send_test_message(
                recipient=recipient,
                original_assignee=test_case["original_assignee"],
                message=test_case["message"],
            )

            print("OK")
            print()

        except requests.RequestException as error:
            print(f"ERRO ao enviar para " f"{recipient}: {error}")
            print()

    print("=" * 60)
    print("TESTE FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
