# Routing List

Dokumen ini berisi daftar route HTTP yang aktif di aplikasi saat ini.

Base URL lokal umum:

```text
http://localhost:8000
```

Dokumentasi otomatis FastAPI:

```text
GET /docs
GET /redoc
```

## Healthcheck

| Method | Path | Fungsi |
| --- | --- | --- |
| GET | `/` | Mengecek aplikasi berjalan. |

## Users

Prefix: `/users`

| Method | Path | Fungsi |
| --- | --- | --- |
| GET | `/users/` | Ambil semua user yang belum soft deleted. |
| GET | `/users/{user_id}` | Ambil detail user berdasarkan ID. |
| POST | `/users/` | Buat user baru. |
| PUT | `/users/{user_id}` | Update data user. |
| DELETE | `/users/{user_id}` | Soft delete user. |

Catatan:

- Password disimpan sebagai `password_hash`.
- Belum ada route login/token.
- Route user saat ini belum diproteksi auth.

## Transaction Categories

| Method | Path | Fungsi |
| --- | --- | --- |
| GET | `/transaction-categories` | Ambil semua kategori transaksi. |
| GET | `/transaction-categories/{category_id}` | Ambil detail kategori transaksi. |
| POST | `/transaction-categories` | Buat kategori transaksi baru. |
| PUT | `/transaction-categories/{category_id}` | Update kategori transaksi. |
| DELETE | `/transaction-categories/{category_id}` | Hapus kategori transaksi. |

## Finance Accounts

| Method | Path | Fungsi |
| --- | --- | --- |
| GET | `/finance-accounts` | Ambil semua akun finansial. |
| GET | `/finance-accounts/{account_id}` | Ambil detail akun finansial. |
| POST | `/finance-accounts` | Buat akun finansial baru. |
| PUT | `/finance-accounts/{account_id}` | Update akun finansial. |
| DELETE | `/finance-accounts/{account_id}` | Hapus akun finansial. |

## Transactions

| Method | Path | Fungsi |
| --- | --- | --- |
| POST | `/transactions` | Buat transaksi baru. |

Catatan:

- Service transaksi sudah memiliki fungsi get, find, update, dan delete.
- Route HTTP untuk list/get/update/delete transaksi belum tersedia di `transactions/entrypoints/api.py`.
- Saat transaksi dibuat, data juga diubah menjadi dokumen embedding dan disimpan ke ChromaDB.

## AI

Prefix: `/ai`

| Method | Path | Fungsi |
| --- | --- | --- |
| POST | `/ai/chat` | Mengirim pesan natural language ke AI orchestrator. |

Flow `/ai/chat`:

```text
User message
  -> FinanceOrchestrator
  -> GroqProvider
  -> tool call:
      create_transaction
      update_transaction
      delete_transaction
```

Catatan:

- Endpoint AI saat ini memakai `current_user_id = 1`.
- Belum memakai auth user aktual.
- Belum ada route `/ai/ask`; route aktif adalah `/ai/chat`.
- RAG indexing sudah ada melalui `EmbeddingService` dan `VectorStore`, tetapi flow tanya-jawab RAG belum menjadi route khusus.

## Route Yang Belum Ada

Route berikut belum aktif di kode saat ini, tetapi service layer sudah mengarah ke kebutuhan tersebut:

| Method | Path | Kebutuhan |
| --- | --- | --- |
| POST | `/auth/login` | Login user dan generate token. |
| GET | `/transactions` | List transaksi. |
| GET | `/transactions/{transaction_id}` | Detail transaksi. |
| PUT | `/transactions/{transaction_id}` | Update transaksi via REST. |
| DELETE | `/transactions/{transaction_id}` | Delete transaksi via REST. |
| POST | `/ai/ask` | Tanya jawab berbasis data/RAG jika ingin dipisah dari `/ai/chat`. |
