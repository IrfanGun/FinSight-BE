import json
import re
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo


class PromptBuilder:
    @staticmethod
    def build(history) -> list[dict[str, str]]:
        messages = [{"role": "system", "content": PromptBuilder.system_prompt()}]
        for item in history:
            content = item.message
            if item.metadata_json and item.metadata_json.get("data"):
                content += "\nKonteks terstruktur: " + json.dumps(
                    item.metadata_json["data"], ensure_ascii=False, default=str
                )
            messages.append({"role": item.role, "content": content})
        return messages

    @staticmethod
    def correction(message: str, history) -> dict | None:
        text = message.lower().strip()
        if not re.search(r"\b(maksudnya|ternyata|salah|harusnya)\b", text):
            return None
        transaction_id = next(
            (data["id"] for item in reversed(history)
             for data in [(item.metadata_json or {}).get("data")]
             if isinstance(data, dict) and data.get("id") is not None), None
        )
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
    def system_prompt() -> str:
        today = datetime.now(ZoneInfo("Asia/Jakarta")).date().isoformat()
        return f"""Anda adalah orchestrator aplikasi keuangan pribadi.

Tanggal hari ini: {today}.
Zona waktu pengguna: Asia/Jakarta.

Gunakan create_transaction untuk transaksi baru, update_transaction untuk perubahan,
dan delete_transaction untuk penghapusan. Jangan mengatakan transaksi berhasil sebelum
tool selesai dijalankan. Jangan mengarang nama akun. Gunakan Bank untuk transfer/rekening,
Cash untuk tunai, dan Investment untuk dana investasi.

Aturan: 30 ribu berarti 30000; 50 rb berarti 50000; 1,5 juta berarti 1500000.
Bensin adalah Transportasi, makan adalah Makanan. Jika nominal atau akun tidak disebut,
tanyakan. Untuk update/delete gunakan transaction_id atau kombinasi atribut transaksi.
Koreksi lanjutan tanpa target berarti transaksi terakhir. Jika target tidak unik, minta
klarifikasi. Jangan memanggil tool untuk pertanyaan, simulasi, atau contoh.""".strip()
