# UniEvent — Universitet tədbirlərinin idarə edilməsi və qeydiyyat sistemi

**Fənn:** Proqramlaşdırma texnologiyaları · **Tapşırıq:** SDF fərdi layihə

HTML/CSS/JavaScript frontend, Flask backend və SQLite bazası ilə işləyən lokal tədris tətbiqi. İnternetdə yerləşdirilmiş sayt deyil. Tələbə müəllif kimi təqdim etməzdən əvvəl kodu öyrənməli, öz dəyişikliklərini etməli və nəticələri özü yoxlamalıdır.

## Windows-da işə salmaq

Python 3.11 və ya daha yeni versiya quraşdırın. ZIP-i çıxarın, `university-events` qovluğunda Terminal / PowerShell açın:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe run.py
```

`seed.py` administrator e-poçtu və şifrəsini terminalda soruşur. Şifrə ekranda görünmür. Bir dəfə icra edin; eyni e-poçtla ikinci icra unikal məhdudiyyət xətası verəcək. Admin hesabı və dörd nümunə tədbir yaradılır. Hazır və hamıya məlum admin şifrəsi yoxdur. Nümunə tarixlər skriptin işə salındığı günə görə hesablanır. Bir tədbir qəsdən keçmiş tarixlidir.

Brauzerdə `http://127.0.0.1:5000` açın. Admin məlumatları ilə daxil olun. Tələbə hesabını saytda “Hesabın yoxdur? Qeydiyyatdan keç” düyməsindən yaradın. Ayrıca terminalda serveri saxlamadan testləri işə salmaq olar.

## Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/python run.py
```

## Testlər

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Linux: `.venv/bin/python -m unittest discover -s tests -v`

Hazırlanma mühitində 14 avtomatlaşdırılmış test keçib. Testlər ayrıca müvəqqəti bazada işləyir; normal tətbiq bazasını dəyişmir. Faktiki çıxış: `docs/test-results.txt`. Brauzer yoxlaması ayrı şəbəkə mühitindən lokal serverə qoşula bilmədiyi üçün tamamlanmayıb. Vizual görünüş və bütün düymələr tələbənin kompüterində də yoxlanmalıdır.

## Mövcud funksiyalar

- Admin üçün tədbirin yaradılması, redaktəsi və əlaqəli qeydiyyatlarla birlikdə silinməsi.
- Ad, kateqoriya, məkan və tarix aralığı ilə axtarış; nəticə olmadıqda mesaj.
- Hesab yaratma, giriş, çıxış; tələbə və administrator səlahiyyətləri.
- Qeydiyyat, təkrar qeydiyyatın bloklanması, limit nəzarəti, ləğv, “Qeydiyyatlarım”.
- Keçmiş və gələcək tədbirlər; keçmiş tədbirə yeni qeydiyyat bağlıdır.
- Admin panelində ümumi saylar, populyar tədbirlər və kateqoriya diaqramları.
- Nümunə əlavə funksiya: admin üçün iştirakçıların UTF-8 CSV ixracı.
- Tutum azaldılarkən mövcud qeydiyyat sayı yenidən yoxlanır.

**Fərdi əlavə tapşırıq:** müəllimin konkret funksiyası hələ verilməyib. CSV ixracı nümunə kimi hazırlanıb; onun müəllimin tapşırığını əvəz etdiyi iddia edilmir.

## Fayllar

| Fayl | Məqsəd |
|---|---|
| `run.py` | Lokal serverin başlanması |
| `seed.py` | Admin və nümayiş məlumatlarının hazırlanması |
| `app/__init__.py` | Tətbiq fabriki, HTTP API, giriş və səlahiyyət yoxlamaları |
| `app/services.py` | Tədbir və qeydiyyat biznes qaydaları |
| `app/db.py` | Sorğu üzrə DB bağlantısı və sxemin hazırlanması |
| `app/schema.sql` | Cədvəllər, açarlar, indekslər və trigger-lər |
| `app/templates/index.html` | Səhifə və dialoq formaları |
| `app/static/` | Dizayn və API ilə işləyən JavaScript |
| `tests/test_app.py` | 14 inteqrasiya testi |
| `docs/TECHNICAL.md` | Arxitektura və seçimlərin əsaslandırılması |
| `docs/DATABASE.md` | DB modeli və bütövlük qaydaları |
| `docs/TESTS.md` | Test ssenariləri və əl ilə yoxlama |
| `docs/AI_LOG.md` | Faktiki AI dəstəyi və tələbə üçün jurnal sahələri |
| `docs/DEFENSE.md` | Müdafiə planı, kod izahları və dəyişiklik nümunəsi |
| `docs/SUBMISSION.md` | Təqdimetmə və qalan addımlar |

## Git tarixçəsi

ZIP-dəki `university-events.bundle` real lokal Git commit-lərini saxlayır. Təmiz repozitoriyanı belə bərpa edin:

```bash
git clone university-events.bundle university-events-repo
cd university-events-repo
git log --oneline
```

ZIP-dən birbaşa çıxarılan mənbə qovluğunda `.git` yoxdur; commit tarixçəsi bundle-dan bərpa edilir. GitHub-da boş repozitoriya yaradıb bərpa olunmuş qovluqda:

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/university-events.git
git push -u origin main
```

Remote GitHub repozitoriyası bu işdə yaradılmayıb; `YOUR_USERNAME` öz hesabınızla əvəz edilməlidir. Mövcud commit-lər AI köməkçisi tərəfindən bu sessiyada yaradılıb, tələbənin əvvəlki işi kimi təqdim edilməməlidir.

## Lokal məlumatlar və sərhədlər

İlk başlanğıcda `instance/events.sqlite3` və sessiya imzası üçün `instance/session.key` yaradılır. Bunları Git-ə əlavə etməyin. Dəyişən sessiya açarı mövcud girişləri etibarsız edir. Nüsxə çıxararkən serveri dayandırın, SQLite faylını təhlükəsiz saxlayın. Vaxtlar Bakı vaxtı (UTC+4), qeydiyyat audit vaxtı isə SQLite UTC formatındadır.

Bu versiya lokal kurs layihəsidir. Geniş istifadə üçün ayrıca WSGI server, HTTPS, `COOKIE_SECURE=1`, giriş cəhdlərinə limit, parol bərpası, e-poçt təsdiqi, audit və migrasiya mexanizmləri əlavə edilməlidir. SQLite kiçik layihə üçündür; böyük paralel yük üçün PostgreSQL keçidi ayrıca işdir. Axtarışda SQLite `LIKE` istifadə olunur; Unicode hərflərin böyük/kiçik variantları üzrə tam dilə uyğun axtarış təmin edilmir.
