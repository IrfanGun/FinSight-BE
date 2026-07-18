UPDATE_TRANSACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "update_transaction",
        "description": (
            "Mengubah transaksi yang sudah tercatat ketika pengguna ingin "
            "mengganti nominal, akun, kategori, atau tanggal transaksi. "
            "Gunakan juga untuk koreksi lanjutan seperti 'ternyata harganya 10rb' "
            "yang merujuk ke transaksi terakhir."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": ["integer", "null"],
                    "description": (
                        "ID transaksi jika disebutkan pengguna. Isi null untuk "
                        "koreksi transaksi terakhir tanpa ID."
                    ),
                },
                "reference_amount": {
                    "type": ["number", "null"],
                    "description": "Nominal transaksi lama untuk membantu pencarian target.",
                },
                "reference_account_name": {
                    "type": ["string", "null"],
                    "description": "Nama akun transaksi lama.",
                },
                "reference_category_name": {
                    "type": ["string", "null"],
                    "description": "Nama kategori transaksi lama.",
                },
                "reference_transaction_date": {
                    "type": ["string", "null"],
                    "description": "Tanggal transaksi lama dalam format YYYY-MM-DD.",
                },
                "amount": {
                    "type": ["number", "null"],
                    "description": "Nominal baru transaksi.",
                },
                "account_name": {
                    "type": ["string", "null"],
                    "description": "Nama akun baru transaksi.",
                },
                "category_name": {
                    "type": ["string", "null"],
                    "description": "Nama kategori baru transaksi.",
                },
                "transaction_date": {
                    "type": ["string", "null"],
                    "description": "Tanggal baru transaksi dalam format YYYY-MM-DD.",
                },
            },
            "required": [
                "transaction_id",
                "reference_amount",
                "reference_account_name",
                "reference_category_name",
                "reference_transaction_date",
                "amount",
                "account_name",
                "category_name",
                "transaction_date",
            ],
            "additionalProperties": False,
        },
    },
}
