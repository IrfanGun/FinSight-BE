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
from app.modules.ai.tools.delete_transaction.definition import (
    DELETE_TRANSACTION_TOOL,
)
from app.modules.ai.tools.delete_transaction.handler import (
    execute_delete_transaction,
)
from app.modules.ai.tools.update_transaction.definition import (
    UPDATE_TRANSACTION_TOOL,
)
from app.modules.ai.tools.update_transaction.handler import (
    execute_update_transaction,
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
            UPDATE_TRANSACTION_TOOL,
            DELETE_TRANSACTION_TOOL,
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

        if tool_name == "create_transaction":
            result = execute_create_transaction(
                arguments=arguments,
                user_id=user_id,
                transaction_service=self.transaction_service,
                account_service=self.account_service,
                category_service=self.category_service,
            )
        elif tool_name == "update_transaction":
            result = execute_update_transaction(
                arguments=arguments,
                user_id=user_id,
                transaction_service=self.transaction_service,
                account_service=self.account_service,
                category_service=self.category_service,
            )
        elif tool_name == "delete_transaction":
            result = execute_delete_transaction(
                arguments=arguments,
                user_id=user_id,
                transaction_service=self.transaction_service,
                account_service=self.account_service,
                category_service=self.category_service,
            )
        else:
            return {
                "success": False,
                "route": "blocked",
                "message": f"Tool '{tool_name}' tidak diizinkan.",
                "tool_name": tool_name,
                "data": None,
            }

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
2. Gunakan create_transaction jika pengguna ingin mencatat transaksi baru.
3. Gunakan update_transaction jika pengguna ingin mengubah transaksi yang sudah ada.
4. Gunakan delete_transaction jika pengguna ingin menghapus, membatalkan, atau undo transaksi.
5. Jangan mengatakan transaksi berhasil sebelum tool selesai dijalankan.
6. Jangan mengarang nama akun.

Aturan:
- "30 ribu" berarti 30000.
- "50 rb" berarti 50000.
- "1,5 juta" berarti 1500000.
- "bensin" masuk kategori Transportasi.
- "makan" masuk kategori Makanan.
- Jika nominal tidak disebutkan, tanyakan nominal.
- Jika akun tidak disebutkan, tanyakan nama akun.
- Untuk update/delete, pakai transaction_id jika diberikan pengguna.
- Jika tidak ada transaction_id, pakai kombinasi nominal, akun, kategori, dan tanggal untuk mencari transaksi target.
- Jika pengguna memakai koreksi lanjutan seperti "ternyata harganya 10rb", "salah, harusnya 10rb", atau "ubah jadi 10rb" tanpa menyebut target, gunakan update_transaction untuk transaksi terakhir.
- Jika target transaksi tidak unik, minta klarifikasi.
- Jangan memanggil tool untuk pertanyaan, simulasi, atau contoh.
""".strip()
