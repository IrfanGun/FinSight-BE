# FinSight API Endpoints

## Ringkasan

Base URL lokal saat development:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Cara Menjalankan

### 1. Siapkan environment

Pastikan Python 3.11+ tersedia.

Buat virtual environment:

```powershell
python -m venv .venv
```

Aktifkan virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependency:

```powershell
pip install -r requirements.txt
```

### 2. Siapkan `.env`

Project ini membaca konfigurasi dari file `.env`.

Contoh minimum:

```env
APP_NAME=FinSight API
DATABASE_URL=postgresql+psycopg://postgres:4@127.0.0.1:5142/finsight_ai
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SECRET_KEY=your-secret-key
```

Catatan:

- Pastikan database PostgreSQL `finsight_ai` sudah dibuat.
- Sesuaikan nama database jika Anda tidak memakai `finsight_ai`.
- Struktur tabel dibuat lewat Alembic migration dan mengacu ke schema di `finsight.db`.

### 3. Jalankan migration

```powershell
alembic upgrade head
```

### 4. Jalankan seeder

```powershell
python scripts\seed.py
```

### 5. Jalankan server

```powershell
uvicorn app.main:app --reload
```

Jika berhasil, API bisa diakses di:

```text
http://127.0.0.1:8000
```

## Endpoint Umum

### `GET /`

Healthcheck sederhana.

Contoh response:

```json
{
  "message": "FinSight API is running"
}
```

## Users

### `GET /users/`

Ambil semua user.

### `GET /users/{user_id}`

Ambil detail user berdasarkan ID.

### `POST /users/`

Buat user baru.

Contoh body:

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

### `PUT /users/{user_id}`

Update data user.

Contoh body:

```json
{
  "full_name": "John Updated",
  "status": "active"
}
```

### `DELETE /users/{user_id}`

Soft delete user.

## Transaction Categories

### `GET /transaction-categories`

Ambil semua kategori transaksi.

### `GET /transaction-categories/{category_id}`

Ambil detail kategori transaksi berdasarkan ID.

### `POST /transaction-categories`

Buat kategori transaksi baru.

Contoh body:

```json
{
  "user_id": null,
  "name": "Food",
  "type": "expense",
  "icon": "utensils",
  "color": "orange",
  "is_default": true,
  "is_active": true
}
```

Nilai `type` yang valid:

- `income`
- `expense`

### `PUT /transaction-categories/{category_id}`

Update kategori transaksi.

Contoh body:

```json
{
  "user_id": null,
  "name": "Groceries",
  "icon": "basket",
  "color": "green"
}
```

### `DELETE /transaction-categories/{category_id}`

Hapus kategori transaksi.

## Financial Accounts

### `GET /finance-accounts`

Ambil semua akun finansial.

### `GET /finance-accounts/{account_id}`

Ambil detail akun finansial berdasarkan ID.

### `POST /finance-accounts`

Buat akun finansial baru.

Contoh body:

```json
{
  "user_id": 1,
  "name": "BCA Main",
  "type": "bank",
  "subtype": "checking",
  "currency": "IDR",
  "balance": 1500000.00,
  "unit": null,
  "quantity": null,
  "is_active": true
}
```

### `PUT /finance-accounts/{account_id}`

Update akun finansial.

Contoh body:

```json
{
  "user_id": 1,
  "type": "bank",
  "subtype": "savings",
  "balance": 1750000.00,
  "currency": "IDR"
}
```

### `DELETE /finance-accounts/{account_id}`

Hapus akun finansial.

## Status Code Umum

- `200` berhasil ambil/update/delete data
- `201` berhasil create data
- `400` request tidak valid atau nama/email sudah dipakai
- `404` data tidak ditemukan

## Catatan Implementasi

- User memakai soft delete melalui field `deleted_at`.
- `transaction category` mengikuti schema `finsight.db`: `user_id`, `type`, `icon`, `color`, `is_default`.
- `finance account` mengikuti schema `finsight.db`: `user_id`, `type`, `subtype`, `unit`, `quantity`.
- Email user harus unik.
