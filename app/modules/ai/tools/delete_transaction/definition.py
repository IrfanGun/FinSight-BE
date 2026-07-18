DELETE_TRANSACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "delete_transaction",
        "description": (
            "Menghapus transaksi yang sudah tercatat ketika pengguna ingin "
            "membatalkan, menghapus, atau undo transaksi."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": ["integer", "null"],
                    "description": "ID transaksi jika disebutkan pengguna.",
                },
                "amount": {
                    "type": ["number", "null"],
                    "description": "Nominal transaksi yang ingin dihapus.",
                },
                "account_name": {
                    "type": ["string", "null"],
                    "description": "Nama akun transaksi yang ingin dihapus.",
                },
                "category_name": {
                    "type": ["string", "null"],
                    "description": "Nama kategori transaksi yang ingin dihapus.",
                },
                "transaction_date": {
                    "type": ["string", "null"],
                    "description": "Tanggal transaksi dalam format YYYY-MM-DD.",
                },
            },
            "required": [
                "transaction_id",
                "amount",
                "account_name",
                "category_name",
                "transaction_date",
            ],
            "additionalProperties": False,
        },
    },
}
