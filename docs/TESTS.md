# Test ssenariləri və nəticələr

İcra tarixi: 24.10.2026. Mühit: Linux, Python 3.12, Flask 3.1.2, Python unittest + Flask test client + müvəqqəti SQLite. Bu nəticələr Windows və bütün brauzerlərin ayrıca yoxlandığını göstərmir.

Komanda: `python -m unittest discover -s tests -v`. Faktiki çıxış ayrıca `test-results.txt` faylındadır. Hər test öz bazasını qurur və sonra silir. Bütün testlərdə başlanğıc admin, iki tələbə və bir gələcək tədbir var.

| № | Avtomatlaşdırılmış test | Addımlar və gözlənilən nəticə | Faktiki nəticə |
|---|---|---|---|
| 1 | test_crud | Admin tədbirin adını dəyişir, siyahıda yeni ad görünür, silmə ilə siyahı boşalır | Keçdi |
| 2 | test_filters | Ad, kateqoriya/məkan, tarix aralığı uyğun nəticə verir; olmayan ad və SQL mətninə oxşar giriş boş nəticə verir | Keçdi |
| 3 | test_invalid_fields | Boş/null ad, sıfır/kəsr limit, keçmiş/yanlış tarix və olmayan kateqoriya → 400 | Keçdi |
| 4 | test_auth_csrf | Yanlış şifrə → 401; tələbənin admin əməliyyatı → 403; CSRF-siz POST → 403; qonağın qeydiyyatı → 401 | Keçdi |
| 5 | test_registration_duplicate_cancel | İlk qeydiyyat → 201; təkrar → 409; şəxsi siyahı yenilənir; ləğvdən sonra boşalır | Keçdi |
| 6 | test_capacity_and_update | Tutum 1 olduqda ikinci istifadəçi rədd edilir; iki qeydiyyat varkən tutum 1 edilə bilmir → 409 | Keçdi |
| 7 | test_concurrent_last_place | Son yerə iki ayrı client paralel sorğu göndərir → dəqiq bir 201 və bir 409; say 1 qalır | Keçdi |
| 8 | test_past_event | Keçmiş tədbir bayrağı göstərilir; yeni qeydiyyat → 409 | Keçdi |
| 9 | test_stats_export_cascade | Tələbə ixrac edə bilmir; admin statistikada 1/1 görür; CSV e-poçtu doğrudur; tədbir silindikdə qeydiyyat da silinir | Keçdi |
| 10 | test_signup | Yeni hesab → 201; eyni e-poçtun böyük hərf variantı → 409; yanlış e-poçt → 400; hash və student rolu saxlanır | Keçdi |
| 11 | test_database_constraints | Birbaşa DB insert-də duplicate cüt və mövcud olmayan istifadəçi FK-sı → IntegrityError | Keçdi |
| 12 | test_csv_formula_escape | Ad =1+1 olarsa CSV hüceyrəsi apostrofla başlayır | Keçdi |
| 13 | test_missing_and_invalid_json | Olmayan tədbirin redaktəsi, qeydiyyatı və silinməsi → 404; JSON massiv → 400 | Keçdi |
| 14 | test_frontend_headers | Baş səhifə və JS → 200; UniEvent mətni və X-Frame-Options başlığı mövcuddur | Keçdi |

## Hələ aparılmalı əl testləri

Bu sətirlər avtomatik nəticə deyil; tələbənin kompüterində tamamlanmalıdır.

| Ssenari | Nə yoxlanmalıdır | Status |
|---|---|---|
| Desktop kataloq | Kartların yerləşməsi, AZ mətnlər, filtr düymələri | Gözləyir |
| Mobil görünüş | 390 px ətrafı en, üfüqi daşma, formalar, menyu | Gözləyir |
| Login və hesab yaratma | Dialoqlar, klaviatura, yanlış şifrə mesajı | Gözləyir |
| CRUD UI | Admin forması, uğur və xəta mesajları, silmə təsdiqi | Gözləyir |
| Qeydiyyat UI | Qeydiyyat/ləğv düyməsi və doluluq indikatoru yenilənir | Gözləyir |
| Statistika UI | Saylar və bar göstəriciləri DB ilə eynidir | Gözləyir |
| CSV / Excel | Fayl açılır, Azərbaycan hərfləri düzgün görünür | Gözləyir |

Brauzer yoxlaması üçün uzaq brauzer `127.0.0.1:5000` ünvanına qoşula bilmədi (`ERR_CONNECTION_REFUSED`). Bu, API testlərinin nəticəsi deyil, brauzer ilə serverin ayrı mühitdə olmasının məhdudiyyətidir. Real ekran görüntüləri hazırlanmış kimi təqdim edilmir.
