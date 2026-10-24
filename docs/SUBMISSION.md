# Təqdimetmə vəziyyəti və qalan addımlar

| Tələb | Hazır olan material | Vəziyyət |
|---|---|---|
| İşlək mənbə kodu | app/, run.py, seed.py, requirements.txt | Lokal API/integration testləri keçib |
| DB strukturu və əlaqələr | schema.sql, DATABASE.md | Hazır |
| Əsas səhifələrin ekran görüntüləri | Aşağıdakı çəkmə siyahısı | Hələ çəkilməyib |
| Git repo və commit tarixçəsi | university-events.bundle | Lokal tarixçə hazır; remote URL yoxdur |
| Test ssenariləri və nəticələr | TESTS.md, test-results.txt, tests/ | 14 avtomatik test keçib; əl testləri gözləyir |
| AI istifadə jurnalı | AI_LOG.md | AI işi qeyd olunub; tələbə öz hissəsini doldurmalıdır |
| Arxitektura və seçimlər | TECHNICAL.md | Hazır |
| Fərdi əlavə funksiya | CSV ixracı nümunəsi | Müəllimin konkret tapşırığı ilə təsdiqlənməlidir |

## Tələbənin tamamlayacağı addımlar

1. README üzrə tətbiqi işə sal, admin yarat, tələbə hesabını saytdan aç.
2. TESTS.md-dəki əl yoxlamalarını apar və real nəticələri əlavə et.
3. Windows Snipping Tool ilə aşağıdakı real ekran görüntülərini çək, `docs/screenshots/` qovluğunda saxla:
   - `01-catalog.png`: kataloq, filtr və tədbir kartları;
   - `02-registration.png`: hesabla qeydiyyat və “Qeydiyyatlarım”;
   - `03-editor.png`: adminin tədbir forması;
   - `04-dashboard.png`: statistika paneli;
   - `05-validation.png`: dolmuş limit və ya yanlış məlumat mesajı;
   - `06-csv.png`: şəxsi məlumatlar olmayan demo CSV-nin açılması.
4. Müəllimdən təyin olunmuş əlavə funksiyanı dəqiqləşdir. CSV uyğun deyilsə konkret tapşırığı inteqrasiya et.
5. Bundle-dan Git repozitoriyasını bərpa et, öz real dəyişikliklərini ayrıca commit et, remote repozitoriyaya push et və onun ünvanını təqdim et.
6. AI jurnalında şəxsi sorğularını, düzəlişlərini və başa düşdüyün anlayışları yaz.
7. DEFENSE.md üzrə məşq et; başa düşmədiyin kodu təqdim etmə.

Uzaq brauzer lokal serverə qoşula bilmədiyinə görə saxta ekran görüntüləri daxil edilməyib. Nümayiş məqsədli şəxsi e-poçt/şifrə və runtime baza faylları paketə əlavə edilmir.
