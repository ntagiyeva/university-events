# Müdafiəyə hazırlıq

## 7–10 dəqiqəlik nümayiş planı

1. Məqsəd (30 san): “Universitet tədbirlərini vahid kataloqda göstərən, tələbələrin yer ayırmasını və adminin tədbirləri idarə etməsini təmin edən web tətbiqidir.”
2. Kataloq (1 dəq): baş səhifəni göstər, ada görə axtar, kateqoriya/məkan/tarix filtrini tətbiq et, boş nəticəni nümayiş etdir.
3. İstifadəçi (1 dəq): hesab yarat, daxil ol, tədbirə qeydiyyatdan keç, şəxsi siyahını aç və ləğv et.
4. Admin (1–2 dəq): yeni tədbir yarat, tutumu 1 et, iki müxtəlif istifadəçi ilə dolmuş limiti göstər, redaktə və silmə təsdiqini aç.
5. Statistika və əlavə funksiya (1 dəq): sayları, populyar tədbirləri, kateqoriyaları və CSV ixracını göstər. CSV-nin müəllimin fərdi funksiyası olduğu yalnız təsdiqdən sonra deyilməlidir.
6. Kod və DB (2 dəq): `schema.sql`, `services.py` və API marşrutlarını aç. DevTools Network bölməsində qeydiyyat zamanı POST sorğusu və JSON cavabını göstər.
7. Test və AI (1 dəq): unittest komandasını işə sal; paralel son yer testini izah et; AI jurnalında faktiki istifadəni və öz dəyişikliklərini göstər.

## Gözlənilən suallar

**Frontend, backend və database nə edir?** Frontend məlumatı göstərir və istifadəçi əməlini sorğuya çevirir. Backend icazəni və biznes qaydalarını yoxlayır. Baza əlaqəli məlumatı və bütövlük məhdudiyyətlərini saxlayır. Frontend-in form yoxlamasına tək güvənmirik.

**Niyə Flask?** Kiçik tətbiq üçün az başlanğıc quruluşu və oxunaqlı marşrutlar. App factory testlərə ayrıca konfiqurasiya verir. Seçim “ən yaxşı framework” iddiası deyil, layihənin həcminə görədir.

**Niyə SQLite?** Lokal müdafiədə ayrıca DB serveri lazım deyil, amma real cədvəllər və tranzaksiyalar var. Çox böyük paralel yazı yükündə PostgreSQL daha uyğun ola bilər.

**Çoxdan-çoxa əlaqə haradadır?** Bir istifadəçi bir neçə tədbirə, bir tədbir bir neçə istifadəçiyə bağlıdır. Aralıq `registrations` cədvəli bunu saxlayır.

**Təkrar qeydiyyat necə bloklanır?** Service əvvəl yoxlayır; bazadakı `UNIQUE(user_id,event_id)` son təminatdır. Yalnız frontend düyməsini söndürmək kifayət deyil.

**Son yeri iki nəfər eyni anda tutsa?** Qeydiyyat `BEGIN IMMEDIATE` tranzaksiyasında işləyir. Bazanın capacity trigger-i əlavə qoruma verir. Test iki ayrı client ilə eyni anda göndərilən sorğuların yalnız birinin qəbulunu yoxlayır.

**Tutum 20-dən 10-a dəyişsə və 15 nəfər qeydiyyatlı olsa?** `capacity_floor` trigger-i UPDATE-i rədd edir. İstifadəçi 409 və aydın mesaj alır. 15 və ya daha çox tutuma dəyişmək olar.

**Şifrə açıq saxlanır?** Xeyr, Werkzeug hash-i saxlanır. Girişdə hash yoxlanır. Sessiyada şifrə saxlanmır; istifadəçi ID-si cookie sessiyası ilə imzalanır. İmzalanmış cookie şifrələnmiş məxfi yaddaş deyil.

**Authentication və authorization fərqi?** Birincisi kimliyi, ikincisi hansı əməliyyatlara icazə olduğunu yoxlayır. Admin düyməsinin gizlənməsi icazə nəzarəti sayılmır; server də rolu yoxlayır.

**SQL injection necə önlənir?** İstifadəçi dəyərləri SQL mətninə birləşdirilmir, `?` parametrləri ilə verilir. Axtarışın sütun/operator seçimi yalnız sabit kod siyahısından gəlir.

**CSRF nədir?** Başqa saytdan istifadəçinin sessiyası ilə dəyişdirən sorğunun göndərilməsi riskidir. Sessiyaya bağlı token frontend-dən ayrıca başlıqda qaytarılır; server müqayisə edir.

**SOLID-in hamısı tətbiq edilib?** Xeyr. SRP və təkrarın azaldılması məqsədli tətbiq edilib. Repository abstraction və tam dependency inversion yoxdur; kiçik kurs layihəsi üçün bu kompromis sənədləşdirilib.

**AI nə edib və sən nə etmisən?** AI bu ilkin kodu, testləri və sənəd qaralamasını hazırlayıb. Öz etdiyin dəyişiklikləri və yoxlamaları faktiki jurnaldan göstər. “Hamısını özüm yazmışam” demə; kodun işləmə prinsipini izah etməyə hazır ol.

## Müəllimin kiçik dəyişiklik tapşırığına məşq

Nümunə: maksimum tutumu 100000-dən 5000-ə salmaq.

1. `EventService.validate` daxilində biznes limitini və xəta mətnini dəyiş.
2. HTML `capacity` input-un `max` atributunu dəyiş.
3. Testə 5000 qəbul və 5001 rədd halını əlavə et.
4. Testləri işə sal, səbəbi və nəticəni Git commit-də yaz.

Bu məşq hələ yerinə yetirilmiş sayılmır; mövcud maksimum 100000-dir. Eyni qaydanı yalnız frontend-də dəyişmək backend-i qorumasız saxlayar.

## Özünü yoxla

- `RegistrationService.register` metodunu sətir-sətir izah edə bilirəm?
- COMMIT, ROLLBACK, UNIQUE və FOREIGN KEY nə edir?
- JSON səhvdirsə və ya istifadəçi admin deyilsə hansı status gəlir?
- Brauzer sorğusunun backend-ə getdiyini Network paneldə göstərə bilirəm?
- Test bazasının normal bazadan fərqini bilirəm?
- Müəllimin konkret fərdi funksiyasını dəqiqləşdirmişəm?
