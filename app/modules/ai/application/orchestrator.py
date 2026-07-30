# app/modules/ai/application/orchestrator.py

import json
import re
from datetime import datetime
from decimal import Decimal
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
from app.modules.ai.adapters.repository import AIConversationRepository



class FinanceOrchestrator:
    def __init__(
        self,
        *,
        transaction_service: TransactionService,
        account_service: FinancialAccountService,
        category_service: TransactionCategoryService,
        conversation_repository: AIConversationRepository,
    ) -> None:
        self.llm = GroqProvider()

        self.transaction_service = transaction_service
        self.account_service = account_service
        self.category_service = category_service
        self.conversation_repository = conversation_repository

    def process(
        self,
        *,
        user_id: int,
        conversation_id: int | None,
        message: str,
    ) -> dict[str, Any]:
        conversation = self.conversation_repository.get_or_create(
            user_id=user_id, conversation_id=conversation_id
        )
        self.conversation_repository.add_message(
            conversation_id=conversation.id, user_id=user_id,
            role="user", message=message,
        )

        history = self.conversation_repository.get_recent_messages(
            conversation_id=conversation.id,
            user_id=user_id,
        )
        correction = self._parse_correction(message, history)
        if correction is not None:
            result = execute_update_transaction(
                arguments=correction,
                user_id=user_id,
                transaction_service=self.transaction_service,
                account_service=self.account_service,
                category_service=self.category_service,
            )
            return self._save_response(conversation.id, user_id, {
                "conversation_id": conversation.id,
                "route": "tool",
                "tool_name": "update_transaction",
                **result,
            })

        llm_messages = [{
            "role": "system",
            "content": self._build_system_prompt(),
        }]
        for item in history:
            content = item.message
            if item.metadata_json and item.metadata_json.get("data"):
                content += "\nKonteks terstruktur: " + json.dumps(
                    item.metadata_json["data"], ensure_ascii=False, default=str
                )
            llm_messages.append({"role": item.role, "content": content})

        response = self.llm.generate(
        messages=llm_messages,
        tools=[
            CREATE_TRANSACTION_TOOL,
            UPDATE_TRANSACTION_TOOL,
            DELETE_TRANSACTION_TOOL,
        ],
    )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []

        if not tool_calls:
            return self._save_response(conversation.id, user_id, {
                "success": True,
                "conversation_id": conversation.id,
                "route": "chat",
                "message": (
                    assistant_message.content
                    or "Saya belum menemukan transaksi untuk dicatat."
                ),
                "tool_name": None,
                "data": None,
            })

        tool_call = tool_calls[0]
        tool_name = tool_call.function.name

        try:
            arguments = json.loads(
                tool_call.function.arguments
            )
        except json.JSONDecodeError:
            return self._save_response(conversation.id, user_id, {
                "success": False,
                "conversation_id": conversation.id,
                "route": "error",
                "message": (
                    "Groq menghasilkan parameter tool "
                    "yang tidak valid."
                ),
                "tool_name": tool_name,
                "data": None,
            })

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
            return self._save_response(conversation.id, user_id, {
                "success": False,
                "conversation_id": conversation.id,
                "route": "blocked",
                "message": f"Tool '{tool_name}' tidak diizinkan.",
                "tool_name": tool_name,
                "data": None,
            })

        return self._save_response(conversation.id, user_id, {
            "conversation_id": conversation.id,
            "route": "tool",
            "tool_name": tool_name,
            **result,
        })

    def _save_response(self, conversation_id: int, user_id: int,
                       response: dict[str, Any]) -> dict[str, Any]:
        self.conversation_repository.add_message(
            conversation_id=conversation_id, user_id=user_id,
            role="assistant", message=response["message"],
            intent=response.get("tool_name"),
            metadata={"route": response.get("route"),
                      "data": response.get("data")},
        )
        self.conversation_repository.commit()
        return response

    @staticmethod
    def _parse_correction(message: str, history) -> dict[str, Any] | None:
        text = message.lower().strip()
        if not re.search(r"\b(maksudnya|ternyata|salah|harusnya)\b", text):
            return None
        transaction_id = None
        for item in reversed(history):
            data = (item.metadata_json or {}).get("data")
            if isinstance(data, dict) and data.get("id") is not None:
                transaction_id = data["id"]
                break
        if transaction_id is None:
            return None
        match = re.search(r"(?:rp\s*)?([\d.,]+)\s*(rb|ribu|jt|juta)?\b", text)
        if not match:
            return None
        amount = Decimal(match.group(1).replace(".", "").replace(",", "."))
        if match.group(2) in ("rb", "ribu"):
            amount *= 1000
        elif match.group(2) in ("jt", "juta"):
            amount *= 1000000
        return {"transaction_id": transaction_id, "amount": amount}

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
7. Untuk transfer atau rekening bank, gunakan account_name "Bank".
8. Untuk pembayaran tunai, gunakan account_name "Cash".
9. Untuk dana investasi, gunakan account_name "Investment".

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
