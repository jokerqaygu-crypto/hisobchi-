# To'lovli kategoriya bot (Click/Payme + qo'lda tasdiqlash)

## Qanday ishlaydi

1. Foydalanuvchi `/start` bosadi — kategoriyalar (masalan: Anime, Romantik) ro'yxati chiqadi
2. Kategoriyani tanlaydi — narx va to'lov havolasi (Click/Payme) ko'rinadi
3. Foydalanuvchi to'lov qiladi, so'ng **chek skrinshotini** botga yuboradi
4. Bot skrinshotni **barcha adminlarga** yuboradi, ✅ Tasdiqlash / ❌ Rad etish tugmalari bilan
5. Admin tasdiqlasa — foydalanuvchiga **kanal linki** avtomatik yuboriladi
6. Admin rad etsa — foydalanuvchiga xabar boradi

## O'rnatish

```bash
pip install -r requirements.txt
```

`config.py`da:
```python
BOT_TOKEN = "SIZNING_TOKENINGIZ"
ADMIN_IDS = [SIZNING_ID_RAQAMINGIZ]
```

## Ishga tushirish

```bash
python main.py
```

## Kategoriya qo'shish (admin)

1. Botga `/admin` yozing
2. **➕ Kategoriya qo'shish**
3. Ketma-ket so'raladi: nomi → narxi → to'lov havolasi (Click/Payme) → kanal havolasi
4. Tayyor — endi foydalanuvchilar shu kategoriyani ko'ra oladi

## GitHub'da doimiy ishlatish

Avvalgi "Majburiy obuna" bot bilan bir xil tartibda:
1. Repo yarating, barcha fayllarni (papka tuzilmasi bilan!) yuklang
2. `.github/workflows/bot.yml` to'g'ri joyda ekanligini tekshiring
3. Repo'ni public qiling (yoki Secrets orqali BOT_TOKEN bering)
4. Actions bo'limidan "Run Payment Bot" workflow'ini ishga tushiring

Kategoriya qo'shilganda/o'chirilganda, bot avtomatik ravishda `database.db`ni
GitHub'ga qaytarib saqlaydi (`git_sync.py` orqali) — shuning uchun 5 soatlik
qayta ishga tushishlarda ma'lumotlar yo'qolmaydi.

## Loyiha tuzilmasi

```
payment_bot/
├── main.py
├── config.py
├── database.py
├── keyboards.py
├── git_sync.py
├── requirements.txt
├── .github/workflows/bot.yml
└── handlers/
    ├── __init__.py
    ├── user.py
    └── admin.py
```

## Muhim eslatma

Bu bot to'lovni **avtomatik tekshirmaydi** — faqat chek skrinshotini adminga
ko'rsatadi, admin qo'lda tasdiqlaydi/rad etadi. To'liq avtomatik tekshirish
(Click/Payme API orqali) uchun rasmiy merchant hisobi va doimiy ishlaydigan
server (VPS) kerak bo'ladi.
