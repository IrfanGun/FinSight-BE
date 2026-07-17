# Architecture

## Overview

Project ini disusun sebagai backend Python dengan pendekatan modular dan gaya layered architecture. Dari struktur folder yang ada, desainnya memisahkan aplikasi ke dalam beberapa module bisnis dan beberapa komponen shared.

Saat ini, struktur arsitekturnya sudah mulai dibentuk, tetapi implementasi kode di hampir semua file masih kosong. Artinya, dokumen ini menjelaskan arsitektur yang dimaksud oleh struktur proyek, bukan implementasi runtime yang sudah aktif.

## Directory Structure

```text
app/
  main.py
  shared/
    config.py
    database.py
    security.py
  modules/
    users/
      domain/
        entities.py
      service_layer/
        auth_service.py
        user_service.py
      adapters/
        orm.py
        repository.py
      entrypoints/
        api.py
    transactions/
      service_layer/
        transaction_service.py
      adapters/
        orm.py
        repository.py
      entrypoints/
        api.py
    ai/
      service_layer/
        rag_service.py
        evaluation_service.py
```

## Architectural Style

Arsitektur ini paling dekat dengan kombinasi berikut:

- Modular monolith
- Layered architecture
- Ports and adapters / clean architecture ringan

Setiap domain dipisahkan ke dalam module sendiri, misalnya `users`, `transactions`, dan `ai`. Di dalam masing-masing module, tanggung jawab dibagi lagi menjadi beberapa layer.

## Layer Responsibilities

### 1. Entrypoints

Folder: `app/modules/*/entrypoints/`

Tanggung jawab:

- menerima HTTP request
- validasi input request
- memanggil service layer
- membentuk HTTP response

File yang diharapkan:

- `users/entrypoints/api.py`
- `transactions/entrypoints/api.py`

Dalam implementasi yang lengkap, file ini biasanya berisi router seperti `FastAPI APIRouter` atau endpoint handler lain.

### 2. Service Layer

Folder: `app/modules/*/service_layer/`

Tanggung jawab:

- menyimpan business use case
- mengatur alur proses aplikasi
- memanggil repository atau komponen eksternal
- mengisolasi logika bisnis dari detail HTTP dan database

Contoh:

- `auth_service.py` untuk autentikasi
- `user_service.py` untuk use case user
- `transaction_service.py` untuk transaksi
- `rag_service.py` dan `evaluation_service.py` untuk fitur AI

### 3. Domain

Folder: `app/modules/*/domain/`

Tanggung jawab:

- mendefinisikan entitas inti bisnis
- menyimpan aturan domain yang tidak bergantung pada framework

Contoh:

- `users/domain/entities.py`

Saat ini hanya module `users` yang sudah disiapkan memiliki folder domain.

### 4. Adapters

Folder: `app/modules/*/adapters/`

Tanggung jawab:

- menghubungkan service layer ke penyimpanan data
- memetakan model database
- menyediakan implementasi repository

Contoh:

- `orm.py` untuk model ORM
- `repository.py` untuk akses data

Layer ini adalah detail infrastruktur yang sebaiknya tidak langsung dipanggil dari endpoint.

### 5. Shared

Folder: `app/shared/`

Tanggung jawab:

- konfigurasi global aplikasi
- koneksi database
- utilitas keamanan

Contoh:

- `config.py` untuk environment/configuration
- `database.py` untuk engine/session database
- `security.py` untuk hashing, JWT, auth helper, atau middleware security

## Expected Request Flow

Berikut alur request yang diharapkan dari struktur ini:

1. Client mengirim HTTP request ke endpoint.
2. `entrypoints/api.py` menerima request dan melakukan parsing/validasi.
3. Endpoint memanggil fungsi di `service_layer`.
4. Service menjalankan business logic.
5. Jika perlu data persistence, service memanggil `adapters/repository.py`.
6. Repository menggunakan `adapters/orm.py` dan `shared/database.py`.
7. Hasil dikembalikan ke service.
8. Service mengembalikan output ke entrypoint.
9. Entrypoint membentuk HTTP response ke client.

## Current Implementation Status

Berdasarkan isi file saat ini:

- struktur folder sudah ada
- pemisahan layer sudah dirancang
- belum ada implementasi kode aktif
- belum ada endpoint HTTP yang terdaftar
- belum ada bootstrap aplikasi di `app/main.py`
- belum ada service, repository, ORM, atau config yang terisi

Dengan kata lain, arsitektur konseptualnya sudah terlihat, tetapi aplikasinya belum berjalan.

## Suggested Runtime Composition

Jika proyek ini akan memakai FastAPI, komposisi minimal yang disarankan:

- `app/main.py`
  - inisialisasi `FastAPI`
  - registrasi router dari module `users` dan `transactions`
- `entrypoints/api.py`
  - definisi `APIRouter`
  - endpoint per use case
- `service_layer/*.py`
  - fungsi atau class use case
- `adapters/repository.py`
  - class repository per aggregate/domain
- `shared/database.py`
  - session factory / database dependency
- `shared/config.py`
  - settings berbasis environment

## Recommended Next Steps

1. Isi `app/main.py` dengan bootstrap aplikasi.
2. Implementasikan endpoint dasar di `users` dan `transactions`.
3. Tambahkan schema request/response jika memakai FastAPI dan Pydantic.
4. Hubungkan service ke repository.
5. Implementasikan database session dan konfigurasi environment.
6. Tambahkan authentication flow di module `users`.

## Summary

Struktur proyek ini menunjukkan niat menggunakan arsitektur backend modular dengan pemisahan layer yang cukup baik: entrypoints, service layer, domain, adapters, dan shared infrastructure. Namun saat ini baru sebatas skeleton struktur folder dan file, sehingga endpoint dan alur aplikasi belum benar-benar diimplementasikan.
