# AI istifadə jurnalı

Bu sənəd AI köməkçisinin bu sessiyada gördüyü işi qeydə alır. Aşağıdakı texniki alt tapşırıqlar ilkin istifadəçi sorğusundan çıxarılıb; istifadəçinin hər birini ayrıca yazdığı iddia edilmir. Tələbə tərəfindən şəxsi yoxlama və öyrənmə bölməsi hələ doldurulmayıb.

## Faktiki ilkin sorğu

“Layihə tapşırığını icra etməyə kömək elə” — Universitet tədbirlərinin idarə edilməsi və qeydiyyat sistemi üzrə tam SDF tələbləri təqdim edilib: frontend, backend, DB, Git, test, AI jurnalı, müdafiə və fərdi əlavə funksiya.

| Mərhələ / alt tapşırıq | AI təklifi və icrası | Yoxlama / düzəliş | Öyrəniləcək anlayış |
|---|---|---|---|
| Tələbləri işlək sistemə çevirmək | Flask + SQLite + build tələb etməyən JS seçildi | Rəsmi Flask və SQLite sənədləri yoxlandı; seçimlərin kompromisləri yazıldı | Client/server, HTTP, JSON |
| DB əlaqələrini qurmaq | users, categories, events, registrations; UNIQUE və FK | İnteqrasiya testində duplicate və yanlış FK yoxlandı | Many-to-many, açar, referensial bütövlük |
| Son yerin eyni anda tutulmasının qarşısını almaq | BEGIN IMMEDIATE və DB trigger | Paralel iki client ilə 201/409 nəticəsi yoxlandı | Tranzaksiya, yarış vəziyyəti |
| Hesab və səlahiyyətləri ayırmaq | Hash, cookie sessiyası, CSRF, admin dekoratoru | Yanlış giriş, tələbənin admin endpoint çağırması və tokensiz sorğu yoxlandı | Authentication və authorization fərqi |
| Əlavə funksiya nümunəsi | CSV ixracı, UTF-8 BOM, formula escape | CSV sətirləri və təhlükəli formula başlanğıcı yoxlandı | CSV və injection |
| Kod keyfiyyəti | Service sinifləri, DomainError, ortak API funksiyası | 14 test keçdi; tam SOLID iddiası edilmədi | SRP və məsuliyyət bölgüsü |
| Vizual yoxlama | Lokal server və uzaq brauzerdə açma cəhdi | Brauzer localhost-a çata bilmədi; ekran görüntüləri tamamlanmadı | Mühit və şəbəkə sərhədi |

## Prosesdə edilmiş düzəlişlər

Test faylının ilk yazılmasında iş qovluğuna görə yol səhv seçilmişdi; fayl düzgün `tests/test_app.py` yoluna yazıldı və testlər yenidən işə salındı. Testdə açılan statik fayl cavabının bağlanması əlavə edildi. Kod tələbənin əl yoxlamasından keçməyib; AI testlərinin nəticəsi şəxsi təsdiqi əvəz etmir.

## Tələbənin özü dolduracağı hissə

| Tarix | Mənim real AI sorğum | AI təklifi | Öz yoxlamam və dəyişdirdiyim kod | Öz sözlərimlə öyrəndiyim anlayış |
|---|---|---|---|---|
| Doldurulmalıdır | Doldurulmalıdır | Doldurulmalıdır | Doldurulmalıdır | Doldurulmalıdır |

Müdafiədən əvvəl: `RegistrationService.register`, `EventService.validate`, session/CSRF axını və SQL açarlarının hər birini öz sözlərinizlə izah edin. Bilmədiyiniz kod hissəsini izah ala-alə öyrənin, sonra kiçik dəyişiklik edib testlə yoxlayın. Şəxsi jurnal sətirlərinə faktiki etmədiyiniz fəaliyyətləri yazmayın.
