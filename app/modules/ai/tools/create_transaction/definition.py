# app/modules/ai/tools/create_transaction/definition.py

CREATE_TRANSACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "create_transaction",
        "description": (
            "Mencatat transaksi pengeluaran ketika pengguna mengatakan "
            "telah membeli, membayar, atau mengeluarkan uang."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": (
                        "Nominal transaksi dalam angka penuh. "
                        "Contoh 30 ribu menjadi 30000."
                    ),
                },
                "account_name": {
                    "type": "string",
                    "description": (
                        "Nama akun pembayaran, misalnya Cash, BCA, "
                        "Mandiri, GoPay, atau ShopeePay."
                    ),
                },
                "category_name": {
                    "type": "string",
                    "description": (
                        "Nama kategori transaksi, misalnya Makanan, "
                        "Transportasi, Tagihan, Kesehatan, atau Belanja."
                    ),
                },
                "transaction_date": {
                    "type": ["string", "null"],
                    "description": (
                        "Tanggal transaksi dalam format YYYY-MM-DD. "
                        "Gunakan null jika tanggal tidak diketahui."
                    ),
                },
            },
            "required": [
                "amount",
                "account_name",
                "category_name",
                "transaction_date",
            ],
            "additionalProperties": False,
        },
    },
}