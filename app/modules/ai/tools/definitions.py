# app/ai/tools/definitions.py

CREATE_EXPENSE_TOOL = {
    "type": "function",
    "name": "create_expense",
    "description": (
        "Mencatat pengeluaran ketika pengguna mengatakan telah membeli, "
        "membayar, atau mengeluarkan uang."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": (
                    "Nominal penuh dalam angka. "
                    "Contoh 30 ribu menjadi 30000."
                ),
            },
            "account_name": {
                "type": "string",
                "description": "Nama akun pembayaran.",
            },
            "category_name": {
                "type": "string",
                "description": "Kategori pengeluaran.",
            },
            "description": {
                "type": "string",
                "description": "Keterangan transaksi.",
            },
            "transaction_date": {
                "type": "string",
                "format": "date",
                "description": "Tanggal transaksi YYYY-MM-DD.",
            },
        },
        "required": [
            "amount",
            "account_name",
            "category_name",
            "description",
            "transaction_date",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}