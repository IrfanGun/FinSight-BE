# app/modules/ai/application/orchestrator.py

import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.modules.ai.providers.groq_provider import GroqProvider
from app.modules.ai.tools.create_transaction.definition import (
    CREATE_TRANSACTION_TOOL,
)
from app.modules.ai.tools.create_transaction.handler import (
    execute_create_transaction,
)
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionService,
    TransactionCategoryService,
)



class FinanceOrchestrator:
    def __init__(
        self,
        *,
        transaction_service: TransactionService,
        account_service: FinancialAccountService,
        category_service: TransactionCategoryService,
    ) -> None:
        self.llm = GroqProvider()

        self.transaction_service = transaction_service
        self.account_service = account_service
        self.category_service = category_service

    def process(
        self,
        *,
        user_id: int,
        message: str,
    ) -> dict[str, Any]:
        response = self.llm.generate(
        messages=[
            {
                "role": "system",
                "content": self._build_system_prompt(),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        tools=[
            CREATE_TRANSACTION_TOOL,
        ],
    )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []

        if not tool_calls:
            return {
                "success": True,
                "route": "chat",
                "message": (
                    assistant_message.content
                    or "Saya belum menemukan transaksi untuk dicatat."
                ),
                "tool_name": None,
                "data": None,
            }

        tool_call = tool_calls[0]
        tool_name = tool_call.function.name

        if tool_name != "create_transaction":
            return {
                "success": False,
                "route": "blocked",
                "message": f"Tool '{tool_name}' tidak diizinkan.",
                "tool_name": tool_name,
                "data": None,
            }

        try:
            arguments = json.loads(
                tool_call.function.arguments
            )
        except json.JSONDecodeError:
            return {
                "success": False,
                "route": "error",
                "message": (
                    "Groq menghasilkan parameter tool "
                    "yang tidak valid."
                ),
                "tool_name": tool_name,
                "data": None,
            }

        result = execute_create_transaction(
            arguments=arguments,
            user_id=user_id,
            transaction_service=self.transaction_service,
            account_service=self.account_service,
            category_service=self.category_service,
        )

        return {
            "route": "tool",
            "tool_name": tool_name,
            **result,
        }

    @staticmethod
    def _build_system_prompt() -> str:
        today = datetime.now(
            ZoneInfo("Asia/Jakarta")
        ).date().isoformat()

        return f"""
Anda adalah orchestrator aplikasi keuangan pribadi.

Tanggal hari ini: {today}.
Zona waktu pengguna: Asia/Jakarta.

Tugas:
1. Pahami pesan pengguna.
2. Gunakan create_transaction jika pengguna telah melakukan pengeluaran.
3. Jangan mengatakan transaksi berhasil sebelum tool selesai dijalankan.
4. Jangan mengarang nama akun.

Aturan:
- "30 ribu" berarti 30000.
- "50 rb" berarti 50000.
- "1,5 juta" berarti 1500000.
- "bensin" masuk kategori Transportasi.
- "makan" masuk kategori Makanan.
- Jika nominal tidak disebutkan, tanyakan nominal.
- Jika akun tidak disebutkan, tanyakan nama akun.
- Jangan memanggil tool untuk pertanyaan, simulasi, atau contoh.
""".strip()
