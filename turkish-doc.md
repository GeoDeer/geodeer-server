# GeoDeer Sunucu Dokümantasyonu (Detaylı Açıklama)

#Önemli Notlar

Farklı bir kütüphane indirip yaptıysanız eğer bir işlemleri pip list --format=freeze > requirements.txt komutunu yazın terminale yoksa site deploy edilirken hata alırsınız.

Models dosyasını değiştirmeyin. Eğer değiştirmek zorunda kalırsanız (tavsiye etmiyorum) Beni arasanız iyi olur öncesinde.
Değişiklik yaptıktan sonra migrate etmeyi unutmayın. Önce python manage.py makemigrations sonra python manage.py migrate.

Views dosyalarıdna da mümkün olduğu kadar az değişiklik yapın. Kullanıcı girişi için falan yapabilirsiniz onun dışında diğer fonksiyonları değiştirmeyin.

Bu doküman, GeoDeer projesinin sunucu tarafı (backend) ve web arayüzü (frontend) bileşenlerini, programlama veya Django konusunda çok az bilgisi olan kişilerin bile anlayabileceği şekilde detaylı olarak açıklamaktadır.

Bazı dosyalarda #for demo diye etiket attım. bu yerleri sunumdan önce inceleyip kapalı olması gerekn yerler varsa eğer kapatabilirsiniz veya açabilirsiniz.

## Projeye Genel Bakış

**Kullanılan Teknolojiler:**

*   **Backend (Sunucu Tarafı):**
    *   **Python:** Ana programlama dili.
    *   **Django:** Python ile yazılmış, web uygulamaları geliştirmeyi kolaylaştıran güçlü bir framework (çatı). Veritabanı işlemleri, kullanıcı yönetimi, URL yönlendirmeleri gibi birçok temel işlevi sağlar.
    *   **Django REST Framework (DRF):** Django üzerine kurulu, mobil uygulamalar gibi diğer istemcilerle iletişim kurmak için API'ler (Uygulama Programlama Arayüzleri) oluşturmayı kolaylaştıran bir kütüphane.
    *   **GeoDjango:** Django'nun coğrafi verilerle (konumlar, haritalar vb.) çalışmayı sağlayan eklentisi.
    *   **PostgreSQL (PostGIS ile):** Verilerin (kullanıcılar, oyunlar, konumlar) saklandığı veritabanı sistemi. PostGIS eklentisi coğrafi sorguları ve işlemleri mümkün kılar.
    *   **pytz:** Zaman dilimi yönetimi için kullanılan bir Python kütüphanesi.
*   **Frontend (Web Arayüzü):**
    *   **HTML:** Web sayfalarının temel yapısını ve içeriğini oluşturan dil.
    *   **CSS:** (Bu dokümanda detayına girilmeyecek) Web sayfalarının görünümünü (renkler, yazı tipleri, düzen) şekillendiren dil.
    *   **JavaScript:** Web sayfalarını interaktif hale getiren (harita etkileşimleri, dinamik güncellemeler, form işlemleri) programlama dili.
    *   **Leaflet:** Haritaları göstermek ve üzerinde işlemler yapmak için kullanılan popüler bir JavaScript kütüphanesi.
    *   **ECharts:** Verileri görselleştirmek (grafikler oluşturmak) için kullanılan bir JavaScript kütüphanesi.
    *   **Django Template Language (DTL):** HTML içinde Python benzeri kodlar yazarak dinamik içerik (örneğin, veritabanından gelen oyun listesi) göstermeyi sağlayan Django'ya özgü sistem.

---

## 1. Backend Mimarisi (Sunucu Tarafı Kodu)

Sunucu tarafı, oyunun beynidir. Verileri saklar, kuralları uygular, mobil uygulama ve web arayüzünden gelen istekleri işler.

### 1.1. Modeller (`game/models.py`)

Modeller, veritabanında saklanacak verilerin yapısını tanımlar. Django'da her model sınıfı, veritabanındaki bir tabloya karşılık gelir. Sınıf içindeki her değişken (alan) ise tablodaki bir sütunu temsil eder.

*   **`User` Modeli (Kullanıcı Tablosu):**
    *   **Amacı:** Oyuncuların ve oyun yaratıcılarının temel bilgilerini saklar.
    *   **Alanları:**
        *   `user_id`: Her kullanıcı için benzersiz, otomatik artan kimlik numarası (Primary Key - Birincil Anahtar).
        *   `username`: Kullanıcının oyundaki benzersiz adı (en fazla 12 karakter).
        *   `email`: Kullanıcının e-posta adresi.
        *   `password`: Kullanıcının (güvenlik için şifrelenmiş) parolası.
    *   **`__str__(self)` metodu:** Django yönetim arayüzü gibi yerlerde kullanıcı nesnesinin nasıl görüneceğini belirler (kullanıcı adını gösterir).

*   **`Game` Modeli (Oyun Tablosu):**
    *   **Amacı:** Oluşturulan her oyunun genel bilgilerini tutar.
    *   **Alanları:**
        *   `game_id`: Her oyun için benzersiz, otomatik artan kimlik numarası.
        *   `game_name`: Oyunun adı (örneğin, "Ankara Kalesi Macerası").
        *   `start_date_time`: Oyunun başlayacağı tarih ve saat bilgisi. Zaman dilimi bilgisi içerir.
        *   `number_of_players`: Oyuna katılabilecek maksimum oyuncu sayısı (ondalıklı sayı olabilir, FloatField).
        *   `time`: Oyunun toplam süresi (saniye cinsinden, FloatField).
        *   `invite_id`: Oyuncuların oyuna katılmak için kullanacağı, otomatik üretilen özel davet kodu (örneğin, `#01151234`). `blank=True` olması boş olabileceği anlamına gelir (başlangıçta boştur).
        *   `game_creator`: Oyunu kimin oluşturduğunu belirtir. `User` modeline bir referanstır (ForeignKey). `on_delete=models.CASCADE` demek, eğer bu kullanıcı silinirse, oluşturduğu oyunların da otomatik olarak silinmesi demektir. `related_name='created_games'` ise bir kullanıcı nesnesi üzerinden onun oluşturduğu oyunlara kolayca erişmeyi sağlar (örneğin, `user.created_games.all()`).
    *   **`__str__(self)` metodu:** Oyun nesnesinin oyun adıyla temsil edilmesini sağlar.
    *   **`format_two_digits(self, value)` metodu:** Verilen bir sayıyı alır, string'e çevirir ve başına '0' ekleyerek iki haneli olmasını sağlar (örneğin, 5 -> "05", 12 -> "12"). `invite_id` üretiminde kullanılır.
    *   **`generate_invite_id(self)` metodu:** Oyun için benzersiz bir davet kodu üretir. Oyunun ID'sinin son iki hanesi, başlangıç gününün iki hanesi ve rastgele 4 haneli bir sayıyı birleştirir (örneğin, `#01151234`).
    *   **`save(self, *args, **kwargs)` metodu:** Bir `Game` nesnesi veritabanına kaydedildiğinde (veya güncellendiğinde) otomatik olarak çalışır.
        *   `super().save(*args, **kwargs)`: Önce Django'nun normal kaydetme işlemini yapar.
        *   `if not self.invite_id:`: Eğer oyun yeni oluşturulmuşsa ve `invite_id` henüz atanmamışsa:
            *   `self.invite_id = self.generate_invite_id()`: `generate_invite_id` metodu çağrılarak bir davet kodu üretilir ve atanır.
            *   `super().save(update_fields=['invite_id'])`: Sadece `invite_id` alanını güncellemek için tekrar kaydetme işlemi yapılır. Bu, gereksiz yere tüm alanları tekrar yazmayı önler.

*   **`Waypoint` Modeli (Hedef Noktası Tablosu):**
    *   **Amacı:** Oyundaki her bir hedef noktası (uğranacak yer) ile ilgili bilgileri saklar.
    *   **Alanları:**
        *   `waypoint_id`: Her hedef noktası için benzersiz, otomatik artan kimlik numarası.
        *   `game`: Bu hedef noktasının hangi oyuna ait olduğunu belirtir (`Game` modeline ForeignKey). `related_name='waypoints'` ile bir oyun üzerinden onun hedef noktalarına erişilebilir (`game.waypoints.all()`).
        *   `waypoint_name`: Hedef noktasının adı (örneğin, "Kale Girişi", "Gizli Çeşme").
        *   `is_last`: Bu noktanın oyundaki son hedef olup olmadığını belirten bir bayrak (`True` veya `False`). `default=False` başlangıçta `False` olacağını belirtir.
        *   `lat`, `lon`: Noktanın enlem ve boylam koordinatları (ondalıklı sayılar).
        *   `height`: Noktanın deniz seviyesinden yüksekliği (isteğe bağlı, `null=True` boş olabilir, `blank=True` formlarda boş bırakılabilir).
        *   `hint`: Oyunculara bu noktayı bulmaları için verilecek ipucu metni.
        *   `question`: Oyuncuların bu noktaya ulaştığında cevaplaması gereken soru metni.
        *   `answer`: Sorunun doğru cevabı.
        *   `ques_dif_level`: Sorunun zorluk seviyesi (1-10 arası gibi, ondalıklı sayı).
        *   `waypoint_geom`: Noktanın coğrafi konumunu GeoDjango formatında saklayan alan (`PointField`). Harita işlemleri için kullanılır. `srid=4326` Dünya üzerindeki standart enlem/boylam koordinat sistemini (WGS84) kullandığını belirtir. `null=True, blank=True` olması, başlangıçta veya bazı durumlarda boş olabileceğini gösterir.
        *   `waypoint_buffer`: Noktanın etrafında belirli bir yarıçapta (örneğin 5 metre) oluşturulan tampon bölgeyi saklayan alan (`PolygonField`). Oyuncunun hedefe yeterince yaklaşıp yaklaşmadığını kontrol etmek için kullanılır. SRID'si `waypoint_geom` ile aynıdır.
        *   `order`: Waypoint'lerin oyun içindeki sırasını belirlemek için kullanılan pozitif tam sayı. `Meta` sınıfındaki `ordering` ile birlikte kullanılır.
    *   **`__str__(self)` metodu:** Hedef noktasını adıyla temsil eder.
    *   **`create_buffer(self, buffer_distance=20)` metodu:**
        *   Verilen `buffer_distance` (varsayılan 20 metre) kadar bir tampon bölge oluşturur.
        *   `geom = self.waypoint_geom`: Noktanın geometrisini alır.
        *   `geom_proj = GEOSGeometry(geom.wkt, geom.srid)`: Geometriyi GeoDjango'nun işleyebileceği bir nesneye dönüştürür.
        *   `geom_proj.transform(3857)`: Metre cinsinden hesaplama yapabilmek için koordinat sistemini Web Mercator'a (SRID 3857) dönüştürür.
        *   `buff = geom_proj.buffer(buffer_distance, quadsegs=8)`: Belirtilen mesafede tampon bölgeyi (poligon) oluşturur. `quadsegs=8` tamponun kenarlarının ne kadar pürüzsüz olacağını belirler.
        *   `buff.transform(4326)`: Tampon bölgenin koordinat sistemini tekrar standart WGS84'e (SRID 4326) dönüştürür.
        *   `return buff`: Oluşturulan tampon poligonunu döndürür.
    *   **`save(self, *args, **kwargs)` metodu:** Bir `Waypoint` kaydedildiğinde çalışır.
        *   `if not self.waypoint_geom:`: Eğer `waypoint_geom` alanı boşsa (genellikle ilk kayıtta):
            *   `self.waypoint_geom = GEOSGeometry(...)`: `lat` ve `lon` değerlerini kullanarak bir `Point` geometrisi oluşturur ve `waypoint_geom` alanına atar.
        *   `self.waypoint_buffer = self.create_buffer(buffer_distance=5)`: 5 metrelik bir tampon bölge oluşturup `waypoint_buffer` alanına atar.
        *   `super().save(*args, **kwargs)`: Değişiklikleri veritabanına kaydeder.
        *   `self.update_is_last_flag()`: Bu waypoint kaydedildikten sonra, oyun içindeki son waypoint'in `is_last` bayrağını güncelleyen metodu çağırır.
        *   `self.create_question()`: Bu waypoint için (eğer henüz yoksa) otomatik olarak boş bir `Question` nesnesi oluşturan metodu çağırır.
    *   **`update_is_last_flag(self)` metodu:**
        *   Aynı oyuna ait tüm waypoint'leri veritabanından çeker (`Waypoint.objects.filter(game=self.game)`).
        *   Bunları `waypoint_id`'ye göre tersten sıralayıp ilkini (yani ID'si en büyük olanı) `last_waypoint` olarak bulur.
        *   Tüm waypoint'leri tek tek kontrol eder:
            *   Eğer bir waypoint'in ID'si `last_waypoint`'in ID'si ile aynıysa, onun `is_last` değerini `True` yapar.
            *   Diğerlerinin `is_last` değerini `False` yapar.
            *   Eğer bir waypoint'in `is_last` değeri değiştiyse, `super(Waypoint, wp).save(update_fields=['is_last'])` ile sadece o alanı veritabanında günceller.
    *   **`create_question(self)` metodu:**
        *   `Question.objects.filter(waypoint=self).exists()`: Bu waypoint ile ilişkili bir `Question` nesnesi veritabanında var mı diye kontrol eder.
        *   `if not ...`: Eğer yoksa:
            *   `Question.objects.create(...)`: Yeni bir `Question` nesnesi oluşturur. Bu soru başlangıçta oyunun yaratıcısına atanır (`user=self.game.game_creator`), cevap süresi 0'dır ve doğru cevaplanmamıştır (`is_correct=False`). Zorluk seviyesi waypoint'ten alınır. Bu, her waypoint için bir soru kaydının olmasını garantiler (mobil uygulama daha sonra bu kaydı güncelleyebilir).
    *   **`Meta` Sınıfı:**
        *   `ordering = ['order']`: Bu model sorgulandığında (örneğin `game.waypoints.all()`), sonuçların otomatik olarak `order` alanına göre sıralanmasını sağlar.

*   **`UserLocation` Modeli (Kullanıcı Konum Tablosu):**
    *   **Amacı:** Oyuncuların oyun sırasındaki konum güncellemelerini ve ilgili bilgileri (zaman, mesafe, hız) kaydeder.
    *   **Alanları:**
        *   `user`, `game`: Bu konum kaydının hangi kullanıcıya ve hangi oyuna ait olduğunu belirtir (ForeignKey ilişkileri).
        *   `lat`, `lon`: Konumun enlem ve boylamı.
        *   `location_geom`: Konumun GeoDjango `PointField` geometrisi. `save` metodunda `lat` ve `lon`'dan otomatik oluşturulur.
        *   `time_stamp`: Konumun kaydedildiği anın zaman damgası (`default=timezone.now` ile otomatik olarak o anki zaman atanır).
        *   `time_diff`: Bu konum kaydı ile aynı kullanıcının bir önceki konumu arasındaki geçen süre (saat cinsinden, `save` metodunda hesaplanır).
        *   `distance`: Bu konum ile bir önceki konum arasındaki mesafe (metre cinsinden, `save` metodunda GeoDjango ile hesaplanır).
        *   `speed`: Hesaplanan anlık hız (km/saat, `save` metodunda `distance / time_diff` ile hesaplanır).
    *   **`save(self, *args, **kwargs)` metodu:** Bir `UserLocation` kaydedileceği zaman çalışır.
        *   **Oyun Bitiş Kontrolü:**
            *   Oyunun bitiş zamanını (`end_time`) hesaplar (`game.start_date_time + game.time`).
            *   Eğer şu anki zaman (`now`) oyunun bitiş zamanından sonraysa, konumu kaydetmez ve bir bilgi mesajı yazdırır (`print`). Bu, oyun bittikten sonra konum gönderilmesini engeller.
            *   `try...except`: Eğer `game.time` geçerli bir sayı değilse veya oyun bilgisi eksikse hata oluşabilir, bu durumda hata mesajı yazdırır ama kaydetmeye devam eder (`pass`).
        *   **Geometri Oluşturma:** `if not self.location_geom...`: Eğer `location_geom` boşsa, `lat` ve `lon`'dan bir `Point` oluşturur.
        *   **Hesaplamalar (Yeni Konumsa):** `is_new = self.pk is None`: Kaydın yeni mi (daha önce veritabanında yok muydu) olduğunu kontrol eder.
            *   `if is_new:`: Eğer yeni bir konum kaydıysa:
                *   `previous = UserLocation.objects.filter(...).order_by('-time_stamp').first()`: Aynı kullanıcı ve oyuna ait, zaman damgasına göre en son kaydedilmiş (bir önceki) konumu bulur.
                *   `if previous:`: Eğer bir önceki konum varsa:
                    *   `delta = self.time_stamp - previous.time_stamp`: İki zaman damgası arasındaki farkı (`timedelta`) hesaplar.
                    *   `self.time_diff = delta.total_seconds() / 3600.0`: Farkı saniyeye çevirip 3600'e bölerek saat cinsinden `time_diff`'i bulur.
                    *   `prev_geom.transform(3857)`, `curr_geom.transform(3857)`: Mesafe hesaplaması için her iki konumun geometrisini de metre bazlı koordinat sistemine (3857) dönüştürür. `.clone()` orijinal geometrilerin değişmemesini sağlar.
                    *   `self.distance = prev_geom.distance(curr_geom)`: İki nokta arasındaki mesafeyi metre cinsinden hesaplar.
                    *   `if self.time_diff and self.time_diff > 0:`: Eğer zaman farkı hesaplanabildiyse ve sıfırdan büyükse:
                        *   `self.speed = (self.distance / 1000) / self.time_diff`: Hızı km/saat olarak hesaplar (mesafeyi km'ye çevirip zamana böler).
                *   `else:`: Eğer bu, kullanıcının oyundaki ilk konum kaydıysa (önceki yoksa):
                    *   `transaction.on_commit(...)`: Veritabanı işlemi başarıyla tamamlandığında çalışacak bir fonksiyon tanımlar.
                    *   `UserScore.objects.get_or_create(...)`: `UserScore` tablosunda bu kullanıcı ve oyun için bir kayıt olup olmadığını kontrol eder. Yoksa, varsayılan skor değerleri (0.0) ile yeni bir kayıt oluşturur. Bu, her oyuncu için bir skor kaydının olmasını garantiler.
        *   `super().save(*args, **kwargs)`: Hesaplanan veya güncellenen tüm alanlarla birlikte konumu veritabanına kaydeder.
    *   **`__str__(self)` metodu:** Konum kaydını "Kullanıcı X için Y zamanındaki konum" şeklinde temsil eder.

*   **`UserScore` Modeli (Kullanıcı Skoru Tablosu):**
    *   **Amacı:** Her oyuncunun bir oyundaki skorlarını ve durumunu (diskalifiye olup olmadığı, bitirme zamanı) tutar.
    *   **Alanları:**
        *   `user`, `game`: Skorun hangi kullanıcıya ve oyuna ait olduğunu belirtir (ForeignKey).
        *   `location_score`, `time_score`, `ques_score`: Farklı kategorilerdeki skorlar (konum başarısı, zamanlama, soru cevaplama). `default=0.0` başlangıçta 0 olmalarını sağlar.
        *   `total_score`: Tüm skorların toplamı.
        *   `is_disqualified`: Oyuncunun diskalifiye edilip edilmediğini belirten bayrak (`default=False`).
        *   `end_date_time`: Oyuncunun oyunu bitirdiği zaman damgası (`null=True, blank=True` olması boş olabileceğini gösterir, yani oyuncu henüz bitirmemiş olabilir).
    *   **`save(self, *args, **kwargs)` metodu:** Bir `UserScore` kaydedildiğinde çalışır.
        *   `old_end = None`: Eski bitiş zamanını tutmak için değişken tanımlar.
        *   `if self.pk:`: Eğer bu kayıt veritabanında zaten varsa (güncelleme durumu):
            *   `old_end = UserScore.objects.filter(pk=self.pk)...first()`: Kaydetmeden *önceki* `end_date_time` değerini veritabanından alır.
        *   `super().save(*args, **kwargs)`: Normal kaydetme/güncelleme işlemini yapar.
        *   `if self.end_date_time and old_end != self.end_date_time:`: Eğer `end_date_time` alanı artık doluysa (yani oyuncu oyunu bitirdiyse) VE bu değer bir önceki değerden farklıysa (yani yeni güncellendiyse):
            *   `calculate_scores_for_game(self.game)`: `game/services/score_calculator.py` dosyasındaki skor hesaplama fonksiyonunu çağırarak, bu oyun için *tüm* oyuncuların skorlarını yeniden hesaplatır. Bu, bir oyuncu bitirdiğinde sıralamaların ve skorların güncellenmesini sağlar.
    *   **`__str__(self)` metodu:** Skoru "Oyun X içindeki Kullanıcı Y için skor" şeklinde temsil eder.

*   **`Question` Modeli (Soru Tablosu):**
    *   **Amacı:** Bir oyuncunun belirli bir waypoint'teki soruyla etkileşimini kaydeder (cevapladı mı, ne zaman, doğru mu?).
    *   **Alanları:**
        *   `game`, `user`, `waypoint`: Sorunun hangi oyuna, hangi kullanıcıya (cevaplayan) ve hangi hedef noktasına ait olduğunu belirtir (ForeignKey).
        *   `ques_dif_level`: Sorunun zorluk seviyesi. `save` içinde `waypoint`'ten otomatik doldurulabilir.
        *   `answer_time`: Oyuncunun soruyu cevaplamak için harcadığı süre (saniye vb.). `default=0`.
        *   `is_correct`: Oyuncunun cevabının doğru olup olmadığını belirten bayrak (`default=False`).
    *   **`save(self, *args, **kwargs)` metodu:** Bir `Question` nesnesi kaydedildiğinde çalışır. Otomatik alan doldurma yapar:
        *   `if not self.ques_dif_level and self.waypoint:`: Eğer zorluk seviyesi belirtilmemişse ve `waypoint` ilişkisi varsa, zorluğu `waypoint`'in zorluk seviyesinden alır.
        *   `if not self.game:`: Eğer `game` belirtilmemişse, `waypoint`'in ait olduğu oyunu atar.
        *   `if not self.user:`: Eğer `user` belirtilmemişse, başlangıçta `waypoint`'in ait olduğu oyunun yaratıcısını atar (bu, `Waypoint`'in `create_question` metodunda oluşturulan ilk kayıt içindir, mobil uygulama daha sonra gerçek cevaplayan kullanıcı ile günceller).
        *   `super().save(*args, **kwargs)`: Doldurulan alanlarla birlikte kaydeder.
    *   **`__str__(self)` metodu:** Soruyu "Hedef Noktası X'teki Kullanıcı Y için soru" şeklinde temsil eder.

### 1.2. API Views (`mobile/views.py`)

Bu dosya, mobil uygulamanın sunucu ile konuşmasını sağlayan API (Uygulama Programlama Arayüzü) endpoint'lerini (uç noktalarını) tanımlar. Mobil uygulama bu endpoint'lere istekler (örneğin, yeni bir konumu kaydetme isteği) gönderir ve sunucu da bu isteklere cevaplar (örneğin, "konum kaydedildi" veya "hata oluştu") verir. Django REST Framework (DRF) kullanılır.

*   **Genel Yapı:** Genellikle her model (`User`, `Game`, `Waypoint` vb.) için temel CRUD (Create, Read, Update, Delete - Oluştur, Oku, Güncelle, Sil) işlemleri için view fonksiyonları bulunur.
    *   `get_*` (örneğin `get_user`): Belirli bir modelin tüm kayıtlarını listelemek için (HTTP GET isteği).
    *   `create_*` (örneğin `create_user`): Yeni bir kayıt oluşturmak için (HTTP POST isteği).
    *   `*_detail` (örneğin `user_detail`): Belirli bir kaydı okumak (GET), güncellemek (PUT) veya silmek (DELETE) için. Genellikle kaydın `pk` (primary key) veya başka bir benzersiz kimliğini URL'den alır.
*   **Decorator'lar:** `@api_view(['GET', 'POST', ...])`
    *   Bu "decorator" (bezemek gibi düşünebiliriz), bir fonksiyonun DRF tarafından bir API view'ı olarak tanınmasını sağlar.
    *   İçindeki liste (`['GET', 'POST']`), bu view fonksiyonunun hangi HTTP metotlarına (istek türlerine) cevap vereceğini belirtir. Örneğin, `get_user` sadece `GET` isteklerine cevap verirken, `user_detail` hem `GET`, hem `PUT`, hem de `DELETE` isteklerine cevap verebilir.
*   **Serializer'lar (`UserSerializer`, `GameSerializer`, vb. - `mobile/serializer.py` dosyasında tanımlıdırlar, burada sadece kullanılıyor):**
    *   **Amacı:** Python nesnelerini (örneğin, veritabanından gelen `User` model nesnesini) mobil uygulamanın anlayabileceği bir formata (genellikle JSON) dönüştürmek ve tam tersini yapmak (mobil uygulamadan gelen JSON verisini Python nesnesine çevirmek). Ayrıca veri doğrulama (validation) işlevi de görürler.
    *   **Kullanım:**
        *   `serializer = UserSerializer(users, many=True)`: Birden fazla `User` nesnesini JSON'a çevirmek için. `many=True` bir liste olduğunu belirtir.
        *   `serializer = UserSerializer(data=request.data)`: Mobil uygulamadan gelen JSON verisi (`request.data`) ile yeni bir `User` nesnesi oluşturmak veya var olanı güncellemek için.
        *   `serializer.is_valid()`: Gelen verinin `UserSerializer` içinde tanımlanan kurallara (örneğin, `username` boş olamaz, `email` geçerli formatta olmalı vb.) uygun olup olmadığını kontrol eder.
        *   `serializer.save()`: Eğer veri geçerliyse (`is_valid()` True döndürdüyse), veriyi veritabanına kaydeder (yeni nesne oluşturur veya var olanı günceller).
        *   `serializer.data`: Serializer'ın Python nesnesini çevirdiği JSON verisi.
        *   `serializer.errors`: Eğer `is_valid()` False döndürdüyse, doğrulama hatalarını içeren bir sözlük (dictionary).
*   **Yanıtlar (`Response`)**
    *   `Response(serializer.data, status=status.HTTP_200_OK)`: API'den başarılı bir cevap döndürmek için kullanılır. İlk parametre gönderilecek veri (genellikle serializer'dan gelen JSON), ikincisi ise HTTP durum kodudur.
    *   **Durum Kodları:**
        *   `status.HTTP_200_OK`: İstek başarılı (genellikle GET için).
        *   `status.HTTP_201_CREATED`: Yeni bir kaynak başarıyla oluşturuldu (genellikle POST için).
        *   `status.HTTP_204_NO_CONTENT`: İstek başarılı ama geri gönderilecek içerik yok (genellikle DELETE için).
        *   `status.HTTP_400_BAD_REQUEST`: İstek geçersiz veya eksik veri içeriyor (genellikle `serializer.is_valid()` False döndüğünde).
        *   `status.HTTP_404_NOT_FOUND`: İstenen kaynak (örneğin, belirli ID'ye sahip kullanıcı) bulunamadı.
*   **Detay View'ları (`*_detail`)**
    *   `try...except Model.DoesNotExist`: URL'den gelen `pk` (primary key) ile veritabanında ilgili nesneyi bulmaya çalışır (`Model.objects.get(pk=pk)`). Bulamazsa `DoesNotExist` hatası oluşur ve `404 NOT FOUND` yanıtı döndürülür.
    *   HTTP Metoduna Göre İşlem: `if request.method == 'GET': ... elif request.method == 'PUT': ...` gibi yapılarla gelen isteğin türüne göre farklı işlemler yapılır (nesneyi oku, güncelle veya sil).
    *   `partial=True` (`question_detail` PUT içinde): Bu parametre, `PUT` isteği ile sadece bazı alanların güncellenmesine izin verir (HTTP PATCH davranışına benzer). Normalde `PUT` tüm alanların gönderilmesini bekler.

### 1.3. Web Views (`game/views.py`)

Bu dosya, web tarayıcısından gelen istekleri işleyen ve kullanıcıya HTML sayfaları gösteren view fonksiyonlarını içerir. Oyun yöneticisinin kullandığı arayüzün mantığı buradadır.

*   **`main_menu(request, creator_id)` Fonksiyonu (Ana Menü Sayfası):**
    *   **Amacı:** Belirli bir oyun yaratıcısının (`creator_id` ile belirtilen) ana menüsünü yönetir.
    *   **Parametreler:**
        *   `request`: Tarayıcıdan gelen isteği temsil eden Django nesnesi. İstek türü (GET, POST), gönderilen veriler vb. bilgileri içerir.
        *   `creator_id`: Hangi kullanıcının ana menüsünün görüntüleneceğini belirten ID (URL'den gelir).
    *   **İşleyiş:**
        *   `if request.method == 'POST':`: Eğer istek bir form gönderimi (POST) ise:
            *   `if 'delete_game' in request.POST:`: Eğer gönderilen form verisi içinde `delete_game` anahtarı varsa (yani "Delete" butonuna basıldıysa):
                *   `game_id = request.POST.get('delete_game')`: Silinecek oyunun ID'sini formdan alır.
                *   `Game.objects.filter(...).delete()`: İlgili oyunu (ID'si ve yaratıcısı eşleşen) veritabanından siler.
                *   `return redirect('main_menu', creator_id=creator_id)`: Kullanıcıyı tekrar ana menü sayfasına yönlendirir (sayfanın yenilenmesini sağlar).
            *   `else:` (Yani "Create Game" butonuna basıldıysa):
                *   `new_game = Game.objects.create(...)`: Yeni bir `Game` nesnesi oluşturur. Yaratıcısı (`creator_id`), varsayılan bir oyun adı, o anki zaman, varsayılan oyuncu sayısı ve süre ile oluşturulur.
                *   `return redirect('create_manage', ...)`: Kullanıcıyı, yeni oluşturulan oyunun düzenleme sayfasına (`create_manage` view'ına) yönlendirir.
        *   `else:` (Yani istek GET ise - sayfa ilk açıldığında veya yenilendiğinde):
            *   `games = Game.objects.filter(...).order_by('-start_date_time')`: İlgili yaratıcıya ait tüm oyunları veritabanından çeker ve başlangıç zamanına göre en yeniden eskiye doğru sıralar.
            *   `return render(request, 'game/main_menu.html', {...})`: `game/main_menu.html` adlı HTML şablonunu (template) kullanarak bir web sayfası oluşturur. `{...}` içindeki sözlük (`context`), şablona gönderilecek verileri içerir (`games` listesi ve `creator_id`).

*   **`create_manage(request, creator_id, game_id)` Fonksiyonu (Oyun Oluşturma/Yönetme Sayfası):**
    *   **Amacı:** Yeni bir oyun oluşturma veya var olan bir oyunu düzenleme arayüzünü yönetir.
    *   **Parametreler:**
        *   `request`, `creator_id`: `main_menu` ile aynı.
        *   `game_id`: Düzenlenecek oyunun ID'si (URL'den gelir). Yeni oyun oluşturuluyorsa bu ID genellikle `main_menu` tarafından atanır.
    *   **İşleyiş:**
        *   `game = Game.objects.filter(...).first()`: Verilen `game_id` ve `creator_id` ile eşleşen oyunu veritabanından bulmaya çalışır. `.first()` eşleşme olmazsa hata vermek yerine `None` döndürür.
        *   `if request.method == 'POST':`: Eğer "Save Game" butonu ile form gönderildiyse:
            *   Formdan oyun bilgilerini (`game_name`, `start_date`, `start_time`, `number_of_players`, `time`, `user_timezone`) alır (`request.POST.get`). `.strip()` ile baştaki/sondaki boşlukları temizler.
            *   **Tarih/Saat İşleme:**
                *   `start_date_str` ve `start_time_str` birleştirilerek `datetime.datetime.strptime` ile Python'un `datetime` nesnesine dönüştürülmeye çalışılır. Format `"%Y/%m/%d %H:%M:%S"` olarak beklenir.
                *   Kullanıcının tarayıcısından gönderilen zaman dilimi adı (`user_timezone`) `pytz.timezone` ile bir zaman dilimi nesnesine çevrilir. Hata olursa varsayılan zaman dilimi kullanılır.
                *   `user_tz.localize(naive)`: Oluşturulan "saf" (naive - zaman dilimi bilgisi olmayan) `datetime` nesnesine kullanıcının yerel zaman dilimi bilgisi eklenir ("aware" hale getirilir). Django veritabanında zamanları genellikle UTC olarak saklar ama bu dönüşüm önemlidir.
                *   `try...except ValueError`: Eğer tarih/saat formatı yanlışsa hata yakalanır ve kullanıcıya mesaj gösterilir (`messages.error`).
            *   **Sayısal Değerleri İşleme:** `number_of_players` ve `time` değerleri `float()` ile ondalıklı sayıya çevrilir. Hata olursa varsayılan değer (0) atanır.
            *   **Oyun Nesnesini Güncelle/Oluştur:**
                *   `if game:`: Eğer oyun zaten varsa (düzenleme modu): Alanları formdan gelen yeni değerlerle günceller ve `game.save()` ile kaydeder.
                *   `else:`: Eğer oyun yoksa (yeni oyun durumu): `Game.objects.create(...)` ile yeni bir oyun nesnesi oluşturur. Eksik bilgi varsa varsayılan değerler kullanılır.
            *   **Waypoint İşleme:**
                *   `raw = request.POST.get('waypoints_data', '[]')`: Formdaki gizli `waypoints_data` alanından JSON formatındaki waypoint listesini alır. Bu JSON, sayfadaki JavaScript tarafından oluşturulur.
                *   `wps = json.loads(raw)`: JSON string'ini Python listesine çevirir. Hata olursa boş liste (`[]`) kullanılır.
                *   **Silinen Waypoint'ler:** (Bu kısım kodda yok ama olmalıydı) Eğer JavaScript silinen waypoint ID'lerini ayrı bir alanda gönderiyorsa, burada `Waypoint.objects.filter(game=game, waypoint_id__in=deleted_ids).delete()` ile silinmeleri gerekir.
                *   `kept_ids = set()`: İşlenen (veya güncellenen) waypoint ID'lerini takip etmek için bir küme (set).
                *   `for idx, wp_data in enumerate(wps):`: JavaScript'ten gelen her waypoint verisi için döngü çalışır:
                    *   `wp_id = wp_data.get('id')`: Waypoint'in ID'sini alır (eğer varsa, yani eski bir waypoint ise).
                    *   `if wp_id: wp = Waypoint.objects.filter(...)`: ID varsa, veritabanından o waypoint'i bulur.
                    *   `else: wp = Waypoint(game=game)`: ID yoksa, yeni bir `Waypoint` nesnesi oluşturur.
                    *   Waypoint'in alanlarını (`waypoint_name`, `lat`, `lon`, `hint`, `question`, `answer`, `ques_dif_level`) JSON'dan gelen verilerle doldurur. `.get('key', default)` ile anahtar yoksa varsayılan değer kullanılır.
                    *   `wp.order = idx`: Waypoint'in sırasını döngüdeki indeksi olarak ayarlar.
                    *   `wp.save()`: Waypoint'i veritabanına kaydeder (yeni ise oluşturur, eski ise günceller). `save` metodu içindeki `create_buffer`, `update_is_last_flag` gibi işlemler de burada tetiklenir.
                    *   `kept_ids.add(wp.pk)`: Kaydedilen waypoint'in ID'sini `kept_ids` kümesine ekler.
                *   `game.waypoints.exclude(pk__in=kept_ids).delete()`: Oyuna ait ama JavaScript'ten gelen listede olmayan (yani kullanıcı tarafından silinmiş ama yukarıda explicit silme kodu yoksa diye) waypoint'leri veritabanından siler.
            *   `return redirect(...)`: Kullanıcıyı tekrar aynı create/manage sayfasına yönlendirir (yapılan değişikliklerin görünmesi için).
        *   `else:` (Yani istek GET ise):
            *   `waypoints = game.waypoints.all().order_by('order')`: Oyuna ait waypoint'leri sırasına göre çeker.
            *   `context = {...}`: Şablona gönderilecek verileri hazırlar (oyun bilgisi, waypoint listesi, yaratıcı ID'si vb.).
            *   `return render(request, 'game/create_manage.html', context)`: `create_manage.html` şablonunu bu verilerle render eder.

*   **`monitor(request, pk, creator_id)` Fonksiyonu (Oyun İzleme Sayfası):**
    *   **Amacı:** Devam eden bir oyunun canlı olarak harita üzerinde takip edilmesini sağlar. Oyuncu konumları, skorları, kalan süre gibi bilgileri gösterir.
    *   **Parametreler:**
        *   `request`, `creator_id`: Diğerleriyle aynı.
        *   `pk`: İzlenecek oyunun ID'si (`game_id` yerine `pk` ismi kullanılmış, Django'da yaygındır).
    *   **İşleyiş:**
        *   `game = get_object_or_404(Game, pk=pk, ...)`: İlgili oyunu bulur. Bulamazsa otomatik olarak 404 "Bulunamadı" hatası verir.
        *   `now = timezone.now()`: Şu anki zamanı alır.
        *   **Oyun Durumu ve Kalan Süre Hesaplama:**
            *   Oyunun bitiş zamanını (`end_time`) hesaplar.
            *   `now` ile `game.start_date_time` ve `end_time` karşılaştırılarak `game_state` belirlenir ("not_started", "running", "finished", "unknown").
            *   Oyun "running" ise, `remaining_seconds_until_end` hesaplanır.
            *   `try...except`: `game.time` geçersizse hata yakalanır, uyarı yazdırılır.
        *   **AJAX POST İsteği (Diskalifiye):**
            *   `if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':`: Eğer istek POST ise VE bir AJAX isteğiyse (JavaScript tarafından gönderilmişse):
                *   `player_id = request.POST.get('player_id')`: Diskalifiye edilecek oyuncunun ID'sini alır.
                *   `user = get_object_or_404(User, user_id=player_id)`: İlgili kullanıcıyı bulur.
                *   `score = get_object_or_404(UserScore, game=game, user=user)`: Kullanıcının bu oyundaki skor kaydını bulur.
                *   `score.is_disqualified = True`: Diskalifiye bayrağını `True` yapar.
                *   `score.save()`: Değişikliği kaydeder.
                *   `return JsonResponse({"status": "success"})`: JavaScript'e işlemin başarılı olduğuna dair JSON yanıtı gönderir.
        *   **Oyuncu Verilerini Hazırlama (Hem İlk Yükleme Hem AJAX İçin):**
            *   `user_scores = UserScore.objects.filter(game=game).select_related('user')`: Oyuna katılan tüm oyuncuların skor kayıtlarını çeker. `select_related('user')` ile her skor kaydı çekilirken ilişkili `User` nesnesinin de tek bir veritabanı sorgusuyla çekilmesi sağlanır (performans iyileştirmesi).
            *   `players = []`: Oyuncu verilerini tutacak boş bir liste oluşturur.
            *   `for score in user_scores:`: Her oyuncu için döngü:
                *   `user_locs = list(UserLocation.objects.filter(...).order_by('-pk')[:100])`: Oyuncunun son 100 konum kaydını çeker. `.reverse()` ile en eskiden en yeniye sıralar.
                *   `latest = user_locs[-1] if user_locs else None`: En son konumu alır (varsa).
                *   `path = [{'lat': loc.lat, 'lon': loc.lon} for loc in user_locs]`: Konumların enlem/boylamlarından oluşan bir liste (yol çizimi için) oluşturur (list comprehension).
                *   `players.append({...})`: Oyuncunun ID'si, adı, skoru, son konumu, yolu, diskalifiye durumu ve son hızı gibi bilgileri içeren bir sözlüğü `players` listesine ekler.
            *   **Renk Atama ve Sıralama:**
                *   `sorted_players = sorted(players, key=lambda p: p['id'])`: Oyuncuları ID'lerine göre sıralar (renk atamasının tutarlı olması için). `lambda` ile sıralama kriteri belirtilir.
                *   `available_colors = [...]`: Kullanılabilir ikon renklerinin listesi.
                *   `for i, player in enumerate(sorted_players):`: Sıralı oyuncu listesi üzerinde dönerken hem indeksi (`i`) hem de oyuncuyu (`player`) alır.
                *   `player['icon'] = available_colors[i % len(available_colors)]`: Oyuncuya sırayla (modulo operatörü `%` ile) listeden bir renk atar.
        *   **Waypoint Verilerini Hazırlama (Hem İlk Yükleme Hem AJAX İçin):**
            *   `waypoints_qs = game.waypoints.all().order_by('order')`: Waypoint'leri sırasına göre çeker.
            *   `waypoints = []`: Waypoint verilerini tutacak liste.
            *   `for idx, wp in enumerate(waypoints_qs):`: Her waypoint için:
                *   Sırasına göre (`idx`) etiket (`label` - "Start Location", "1st Waypoint", "Last Waypoint") ve marker rengi (`marker_color`) belirlenir. `ordinal` fonksiyonu sıra sayılarını "1st", "2nd" gibi yapar.
                *   `waypoints.append({...})`: Waypoint ID, ad, konum, etiket ve renk bilgilerini içeren sözlüğü listeye ekler.
        *   **AJAX GET İsteği Yanıtı:**
            *   `if request.headers.get('x-requested-with') == 'XMLHttpRequest':`: Eğer istek GET ve AJAX ise (yani JavaScript periyodik olarak veri güncellemesi istiyorsa):
                *   O anki `game_state` ve `remaining_seconds_ajax` tekrar hesaplanır (zaman geçmiş olabilir).
                *   `return JsonResponse({...})`: Hazırlanan oyuncu listesi (`sorted_players`), waypoint listesi (`waypoints`), oyun durumu ve kalan süreyi JSON formatında JavaScript'e gönderir.
        *   **Normal GET İsteği Yanıtı (İlk Sayfa Yüklemesi):**
            *   `context = {...}`: Şablona gönderilecek verileri hazırlar (oyuncular, oyun bilgisi, waypointler, oyun durumu, kalan süre vb.).
            *   `return render(request, 'game/monitor.html', context)`: `monitor.html` şablonunu bu verilerle render eder.

*   **`results(request, game_id, creator_id)` Fonksiyonu (Sonuç Sayfası):**
    *   **Amacı:** Tamamlanmış bir oyunun sonuçlarını (skor tablosu, kazanan, hız grafiği) gösterir.
    *   **Parametreler:** `request`, `game_id`, `creator_id`.
    *   **İşleyiş:**
        *   `game = get_object_or_404(...)`: İlgili oyunu bulur.
        *   `user_scores = UserScore.objects.filter(game=game).select_related('user')`: Oyuna ait tüm skor kayıtlarını kullanıcı bilgileriyle birlikte çeker.
        *   `players = [...]`: Her oyuncu için ID, ad, skor ve diskalifiye durumunu içeren bir liste oluşturur (list comprehension).
        *   `sorted_players = sorted(players, key=lambda p: p['score'], reverse=True)`: Oyuncuları skorlarına göre büyükten küçüğe (`reverse=True`) sıralar.
        *   **Renk Atama:** `monitor` fonksiyonundaki gibi oyunculara sıralarına göre ikon rengi atanır.
        *   **Hız Grafiği Verisi Hazırlama (`speed_data`):**
            *   `all_times = UserLocation.objects.filter(game=game)...`: Oyundaki tüm konum kayıtlarının zaman damgalarını çeker.
            *   `speed_data = {'labels': [], 'players': []}`: Grafik için veri yapısını başlatır.
            *   `if all_times:`: Eğer konum kaydı varsa:
                *   İlk ve son zaman damgasını bulur ve formatlayarak (`strftime('%H:%M')`) grafiğin X ekseni etiketleri (`labels`) olarak ayarlar.
            *   `for p in sorted_players:`: Sıralı her oyuncu için:
                *   `locs = UserLocation.objects.filter(...)`: Oyuncunun tüm konumlarını zamanına göre sıralı çeker.
                *   `if locs:`: Eğer oyuncunun konumu varsa:
                    *   İlk ve son konumlarının hızlarını (`speeds = [locs.first().speed or 0, locs.last().speed or 0]`) alır. `or 0` hız değeri `None` ise 0 kullanılmasını sağlar.
                *   `else: speeds = [0, 0]`: Konumu yoksa hızları 0 kabul eder.
                *   `speed_data['players'].append({...})`: Oyuncunun adını, hız listesini (`speeds`) ve ikon rengini içeren bir sözlüğü `speed_data['players']` listesine ekler. Bu yapı ECharts grafiği için uygundur.
        *   `return render(request, 'game/results.html', {...})`: `results.html` şablonunu hazıirlanan verilerle (sıralı oyuncular, oyun bilgisi, kazanan, JSON'a çevrilmiş `speed_data`) render eder. `json.dumps(speed_data)` Python sözlüğünü JSON string'ine çevirir ki JavaScript bunu kullanabilsin.

*   **`calculate_scores(request, game_id, creator_id)` Fonksiyonu:**
    *   **Amacı:** Belirli bir oyun için skorları manuel olarak yeniden hesaplatmak (genellikle test veya düzeltme amaçlı bir URL'den çağrılır, normal akışta `UserScore.save` içinde otomatik yapılır).
    *   **İşleyiş:**
        *   İlgili oyunu bulur (`get_object_or_404`).
        *   `calculate_scores_for_game(game)` fonksiyonunu çağırır.
        *   Kullanıcıyı sonuç sayfasına (`results` view'ına) yönlendirir.

*   **`ordinal(n)` Fonksiyonu:**
    *   **Amacı:** Bir sayıyı alır (örneğin 3) ve onun İngilizce'deki sıra belirten halini döndürür (örneğin "3rd"). `monitor` ve `create_manage` sayfalarında waypoint etiketleri için kullanılır.

### 1.4. Hizmetler (`game/services/score_calculator.py`)

Bu dosya, belirli bir iş mantığını (bu durumda skor hesaplama) view fonksiyonlarından ayırarak daha düzenli bir yapı oluşturmak için kullanılır. "Service layer" (hizmet katmanı) olarak adlandırılır.

*   **`calculate_scores_for_game(game)` Fonksiyonu:**
    *   **Amacı:** Belirli bir oyun (`game` parametresi ile gelen) için tüm oyuncuların skorlarını (`UserScore`) hesaplar ve günceller.
    *   **İşleyiş:**
        *   `apps.get_model(...)`: `Question`, `UserLocation`, `UserScore` modellerini dinamik olarak yükler. Bu, olası "circular import" (birbirini import etmeye çalışan dosyalar) sorunlarını önleyebilir.
        *   `scores = list(UserScore.objects.filter(game=game))`: Oyundaki tüm skor kayıtlarını bir listeye alır.
        *   **Konum Skoru Hesaplama (Sıralama Mantığı):**
            *   `perf_list = []`: Her oyuncunun skor nesnesini ve bir "performans" metriğini (burada ortalama hız gibi bir şey) tutacak liste.
            *   `for score in scores:`: Her oyuncu için:
                *   Oyuncunun tüm konumlarını (`locs`) çeker.
                *   Toplam mesafeyi (`total_dist_m`) hesaplar. `loc.distance or 0` ile `distance` `None` ise 0 kabul edilir.
                *   Mesafeyi km'ye çevirir (`dist_km`).
                *   Oyuncu oyunu bitirmişse (`score.end_date_time` varsa):
                    *   Geçen süreyi saat cinsinden (`hours`) hesaplar.
                    *   Ham performansı (`raw_p`) `dist_km / hours` olarak hesaplar (ortalama hız). Süre 0 ise performansı 0 kabul eder.
                *   Oyuncu bitirmemişse `raw_p` 0 olur.
                *   `(score, raw_p)` ikilisini `perf_list`'e ekler.
            *   `perf_list.sort(key=lambda x: x[1], reverse=True)`: Listeyi ham performansa (`raw_p`) göre büyükten küçüğe sıralar.
            *   `n = len(perf_list)`: Oyuncu sayısını alır.
            *   `loc_score = round((n - idx) * (100.0 / n))`: Sıralamaya göre konum skorunu hesaplar. 1. oyuncu 100, 2. oyuncu `(n-1)/n * 100` gibi bir puan alır. `idx` oyuncunun sıralamadaki indeksidir (0'dan başlar).
        *   **Soru Skoru Hesaplama:**
            *   `correct_qs = Question.objects.filter(...)`: Oyuncunun doğru cevapladığı soruları çeker.
            *   `ques_score = sum(q.ques_dif_level * 5 for q in correct_qs)`: Her doğru soru için `zorluk_seviyesi * 5` puan ekler.
        *   **Zaman Skoru Hesaplama:**
            *   `all_qs = Question.objects.filter(game=game, user=score.user)`: Oyuncunun cevapladığı *tüm* soruları (doğru/yanlış) çeker.
            *   `bonus = sum(q.answer_time * (q.ques_dif_level / 10) for q in all_qs)`: Cevaplama süresi ve zorluğa bağlı bir bonus hesaplar (daha hızlı cevaplamak daha iyi).
            *   `if score.end_date_time:`: Oyuncu bitirmişse:
                *   Harcanan süreyi dakika cinsinden (`spent_min`) hesaplar.
                *   İzin verilen süreyi dakika cinsinden (`allowed_min`) alır.
                *   `time_score = max(allowed_min - spent_min, 0) + bonus`: Kalan süreden puan alır (negatif olamaz) ve bonusu ekler.
            *   `else: time_score = 0`: Bitirmemişse zaman skoru 0'dır.
        *   **Toplam Skor ve Kaydetme:**
            *   `total_score = ques_score + time_score + loc_score`: Üç kategorideki skoru toplar.
            *   `score.ques_score = ...`, `score.time_score = ...`, ... : Hesaplanan skorları `UserScore` nesnesinin ilgili alanlarına atar.
            *   `score.save(update_fields=[...])`: Sadece güncellenen skor alanlarını veritabanına kaydeder. Bu, `UserScore`'un kendi `save` metodunu tekrar tetiklemesini (ve sonsuz döngüye girmesini) önler, çünkü `end_date_time` değişmemiştir.

### 1.5. URL Yönlendirmeleri (`GeoDeer/urls.py`, `game/urls.py`, `mobile/urls.py`)

URL'ler, kullanıcıların tarayıcıya yazdığı adresleri (örneğin `/main-menu/1/`) hangi view fonksiyonunun çalıştıracağını belirleyen eşleştirmelerdir.

*   **`GeoDeer/urls.py` (Ana URL Dosyası):**
    *   Projenin kök URL yönlendirmelerini yapar.
    *   `path('admin/', admin.site.urls)`: Django'nun yönetim arayüzü için standart yol.
    *   `path('main-menu/<int:creator_id>/', main_menu, name='main_menu')`: `/main-menu/` ile başlayan ve ardından bir tam sayı (`int:creator_id`) gelen URL'leri `game/views.py` içindeki `main_menu` fonksiyonuna yönlendirir. `<int:creator_id>` kısmı, URL'deki sayıyı yakalar ve view fonksiyonuna `creator_id` adında bir parametre olarak geçirir. `name='main_menu'` ise bu URL'ye kod içinde (örneğin `redirect` veya `{% url %}` içinde) kolayca referans vermek için kullanılır.
    *   `path('game/', include('game.urls'))`: `/game/` ile başlayan tüm URL'leri `game/urls.py` dosyasına yönlendirir. `include` ile alt uygulamaların URL'lerini dahil etmek yaygın bir pratiktir.
    *   `path('api/', include('mobile.urls'))`: `/api/` ile başlayan tüm URL'leri `mobile/urls.py` dosyasına yönlendirir.
*   **`game/urls.py` (Web Arayüzü URL'leri):**
    *   `game` uygulamasının web sayfaları için URL tanımlarını içerir.
    *   `path('create-manage/<int:creator_id>/<int:game_id>/', views.create_manage, name='create_manage')`: `/game/create-manage/` ardından yaratıcı ID'si ve oyun ID'si gelen URL'leri `create_manage` view'ına yönlendirir.
    *   `path('monitor/<int:creator_id>/<int:pk>/', views.monitor, name='monitor')`: Monitor sayfası için URL. `pk` kullanılmış (oyun ID'si).
    *   `path('results/<int:creator_id>/<int:game_id>/', views.results, name='results')`: Sonuç sayfası için URL.
    *   `path('calculate-scores/<int:creator_id>/<int:game_id>/', views.calculate_scores, name='calculate_scores')`: Skorları manuel hesaplatma URL'si.
*   **`mobile/urls.py` (API URL'leri):**
    *   Mobil uygulamanın kullanacağı API endpoint'lerini tanımlar. Hepsi `/api/` altında yer alır (ana `urls.py`'deki `include` sayesinde).
    *   `path('users/', views.get_user, name='get_user')`: Tüm kullanıcıları listeleme (GET).
    *   `path('users/create/', views.create_user, name='create_user')`: Yeni kullanıcı oluşturma (POST).
    *   `path('users/<int:pk>/', views.user_detail, name='user_detail')`: Belirli bir kullanıcıyı getirme (GET), güncelleme (PUT), silme (DELETE).
    *   Diğer modeller (`games`, `waypoints`, `userlocations`, `userscores`, `questions`) için de benzer CRUD endpoint'leri tanımlanmıştır.
    *   `path('questions/<int:waypoint_id>/', views.question_detail, name='question_detail')`: `Question` için detay endpoint'i `waypoint_id` kullanır, çünkü genellikle bir waypoint'e ait soru güncellenir.

---

## 2. Frontend Mimarisi (Web Arayüzü - HTML ve JavaScript)

Frontend, kullanıcının (oyun yöneticisinin) tarayıcısında gördüğü ve etkileşime girdiği kısımdır. HTML ile yapı oluşturulur, JavaScript ile dinamik davranışlar eklenir.

### 2.1. Genel HTML Yapısı ve Django Template Dili (DTL)

Tüm HTML dosyaları (`main_menu.html`, `create_manage.html`, `monitor.html`, `results.html`) benzer bir temel yapıya sahiptir:

*   `<!DOCTYPE html>`: HTML5 belgesi olduğunu belirtir.
*   `<html>`: Sayfanın kök elemanı.
*   `<head>`: Sayfa hakkında meta bilgiler (karakter seti, başlık), CSS dosyalarına linkler (`<link>`), JavaScript kütüphanelerine linkler (`<script src="...">`) içerir.
*   `<body>`: Sayfada görünen asıl içeriği (başlık çubuğu, ana içerik, alt bilgi) içerir.
*   **Django Template Dili (DTL) Kullanımı:**
    *   `{% load static %}`: Django'nun statik dosyaları (CSS, JavaScript, resimler) yönetmesine yardımcı olan `static` etiketini yükler. `{% static 'images/icon.png' %}` gibi kullanılarak dosyanın doğru URL'si oluşturulur.
    *   `{% load tz %}`: Zaman dilimi ile ilgili etiket ve filtreleri yükler (artık daha çok JavaScript tarafında yapılıyor gibi görünse de).
    *   `{{ variable_name }}`: View fonksiyonundan `render` ile gönderilen `context` sözlüğündeki bir değişkenin değerini HTML içine yerleştirir. Örneğin, `{{ game.game_name }}` oyunun adını yazar.
    *   `{{ variable|filter }}`: Değişkenin değerini belirli bir filtreden geçirerek formatlar. Örnekler:
        *   `{{ game.time|floatformat:0 }}`: Ondalıklı sayıyı tam sayı gibi gösterir.
        *   `{{ game.start_date_time|date:"d/m/Y" }}`: Tarihi GG/AA/YYYY formatında gösterir.
        *   `{{ waypoints|safe }}`: Değişkenin içeriğini HTML olarak güvenli kabul eder ve doğrudan render eder (genellikle view'da hazırlanmış HTML snippet'leri veya JSON verisi için kullanılır - dikkatli kullanılmalıdır).
        *   `{{ speed_data|escapejs }}`: JavaScript içinde güvenle kullanılabilecek şekilde bir string'i escape eder.
    *   `{% for item in list %}` ... `{% empty %}` ... `{% endfor %}`: Bir liste veya sorgu seti üzerinde döngü yapar. Liste boşsa `{% empty %}` bloğu çalışır.
    *   `{% if condition %}` ... `{% elif condition2 %}` ... `{% else %}` ... `{% endif %}`: Koşullu ifadelerle HTML'in belirli kısımlarını gösterir veya gizler.
    *   `{% url 'view_name' param1=value1 %}`: Django'nun URL yönlendirme sistemini kullanarak belirli bir view için doğru URL'yi oluşturur. Bu, URL'ler değişse bile linklerin çalışmasını sağlar. Örneğin, `<a href="{% url 'monitor' creator_id=creator_id pk=game.game_id %}">`.
    *   `{% csrf_token %}`: Güvenlik önlemi olarak, POST metodu ile gönderilen formların içine eklenmesi gereken bir etikettir. Sitedeler arası istek sahteciliği (CSRF) saldırılarını önlemeye yardımcı olur.

### 2.2. `create_manage.html` JavaScript Mantığı

Bu sayfa, oyun yaratıcısının harita üzerinde hedef noktaları (waypoint) eklemesini, düzenlemesini, silmesini ve oyunun genel ayarlarını yapmasını sağlar.

*   **Harita (Leaflet):**
    *   `L.map('map', ...)`: HTML'deki `id="map"` olan `div` içine bir Leaflet haritası oluşturur. `doubleClickZoom: false` çift tıklama ile yakınlaşmayı kapatır.
    *   `L.tileLayer(...)`: Harita üzerinde gösterilecek katmanları (OSM - OpenStreetMap ve Esri Uydu Görüntüsü) tanımlar.
    *   `osmLayer.addTo(map)`: Başlangıçta OSM katmanını haritaya ekler.
    *   `toggleLayer()`: "Satellite View" onay kutusu değiştiğinde çağrılır, katmanlar arasında geçiş yapar (`map.removeLayer`, `map.addLayer`).
    *   `L.marker([lat, lon], ...)`: Belirli koordinatlara bir işaretçi (marker) ekler.
        *   `draggable: false/true`: Sürüklenebilir olup olmadığını ayarlar.
        *   `icon: icon`: Kullanılacak ikon nesnesi.
        *   `.addTo(map)`: Markeri haritaya ekler.
        *   `.bindTooltip(...)`: Marker üzerine gelince veya sürekli görünen bir etiket ekler.
    *   **Mevcut Waypoint'leri Gösterme:** Sayfa yüklendiğinde, Django şablonu (`{% for wp in game.waypoints.all %}`) ile gelen waypoint verileri kullanılarak her biri için bir marker oluşturulur ve `markers` nesnesinde saklanır (`markers[waypoint_index] = marker_object`).
*   **Waypoint Yönetimi:**
    *   **Durum Değişkenleri:**
        *   `waypointCount`: Toplam waypoint sayısı (başlangıç noktası dahil).
        *   `isSaved`: Mevcut düzenlemenin kaydedilip kaydedilmediğini takip eden bayrak. Yeni bir işlem yapmadan önce mevcutun kaydedilmiş olması gerekir.
        *   `isEditable`: Şu anda bir waypoint'in düzenleme modunda olup olmadığını belirten bayrak.
        *   `currentEditIndex`: Şu anda düzenlenmekte olan waypoint'in indeksi (sidebar'daki sırası).
    *   **Fonksiyonlar:**
        *   `editPin(index)`:
            *   Eğer kaydedilmemiş bir değişiklik varsa uyarı verir.
            *   İlgili waypoint'in marker'ını sürüklenebilir (`dragging.enable()`) yapar.
            *   Sidebar'daki ilgili kutudaki input alanlarını aktif hale getirir (`disabled = false`).
            *   "Edit" butonunu gizler, "Save" butonunu gösterir.
            *   `isEditable`, `isSaved`, `currentEditIndex` durum değişkenlerini günceller.
        *   `savePin(index)`:
            *   Eğer marker'ın konumu haritada belirlenmemişse uyarı verir.
            *   Marker'ı kilitler (`locked = true`, `dragging.disable()`).
            *   Sidebar'daki inputları pasif hale getirir (`disabled = true`).
            *   "Save" butonunu gizler, "Edit" butonunu gösterir.
            *   Durum değişkenlerini günceller (`isSaved = true`, `isEditable = false`, `currentEditIndex = null`).
            *   Yeni waypoint ekleme butonlarını tekrar görünür yapar.
        *   `deletePin(index)`: (Sadece son waypoint için görünür)
            *   Kaydedilmemiş değişiklik varsa uyarı verir.
            *   İlgili marker'ı haritadan kaldırır (`map.removeLayer`).
            *   İlgili waypoint kutusunu sidebar'dan kaldırır (`box.remove()`).
            *   `waypointCount`'ı azaltır.
            *   Eğer varsa, bir önceki waypoint'e (yeni son waypoint) "Delete" butonunu ekler.
            *   Durum değişkenlerini sıfırlar.
        *   `addNewWaypoint()`:
            *   Kaydedilmemiş değişiklik veya maksimum waypoint sayısına ulaşılmışsa uyarı verir.
            *   Eski son waypoint'ten (varsa) "Delete" butonunu kaldırır.
            *   `waypointCount`'ı artırır.
            *   Sidebar'a yeni bir waypoint kutusu HTML'i oluşturur (`document.createElement`, `box.innerHTML = ...`) ve ekler. Yeni kutu başlangıçta "Save" modundadır.
            *   Durum değişkenlerini günceller (`isSaved = false`, `currentEditIndex = waypointCount`).
            *   `updateTitles()`'ı çağırır.
        *   `updateTitles()`: Sidebar'daki tüm waypoint kutularını dolaşır ve indekslerine göre başlıklarını ("Start Location", "1st Waypoint", "2nd Waypoint"...) günceller. `ordinal()` fonksiyonunu kullanır.
    *   **Harita Etkileşimi (`map.on('dblclick', ...)`):**
        *   Haritaya çift tıklandığında çalışır.
        *   Eğer `currentEditIndex` null ise (yani düzenleme modu aktif değilse) uyarı verir.
        *   Aktif olan (`currentEditIndex`) waypoint'in marker'ını (varsa eskisini silip) tıklanan konuma yerleştirir. Markeri sürüklenebilir yapar ve sürüklenip bırakıldığında koordinatlarını güncelleyen bir olay dinleyici (`dragend`) ekler.
        *   Marker'ın `coords` özelliğine tıklanan `latlng` değerini atar.
        *   Sidebar'daki isme göre tooltip metnini günceller.
*   **Konum Arama (Nominatim):**
    *   `searchLocation()`: Arama kutusundaki değeri alır, OpenStreetMap'in Nominatim servisine `fetch` ile bir arama isteği gönderir. Gelen JSON yanıtında sonuç varsa, haritayı bulunan ilk sonucun konumuna odaklar (`map.setView`).
*   **Oyunu Kaydetme (`saveGameBtn` tıklanınca):**
    *   `out = []`: Backend'e gönderilecek waypoint verilerini tutacak boş bir liste.
    *   `document.querySelectorAll('.waypoint-box').forEach(...)`: Sidebar'daki tüm waypoint kutuları üzerinde döner.
    *   Her kutu için:
        *   Gerekli bilgileri (ID (varsa), isim, ipucu, soru, cevap, zorluk) input alanlarından alır (`box.querySelector(...).value`).
        *   Marker'ın koordinatlarını (`markers[index].coords`) alır. Koordinat yoksa bu waypoint'i atlar.
        *   Bu bilgileri bir sözlük (object) olarak `out` listesine ekler.
    *   `document.getElementById('waypointsData').value = JSON.stringify(out)`: Oluşturulan `out` listesini JSON string'ine çevirir ve formdaki gizli `waypointsData` input'unun değerine atar.
    *   `document.getElementById('gameInfoForm').submit()`: Ana formu (oyun adı, zamanı vb. içeren) gönderir. Form gönderildiğinde `waypointsData` da diğer form verileriyle birlikte backend'deki `create_manage` view'ına POST isteği olarak gider.
*   **Zaman Dilimi Yönetimi (`DOMContentLoaded` içinde):**
    *   Sayfa yüklendiğinde çalışır.
    *   Backend'den gelen UTC formatındaki başlangıç zamanını (`data-utc-datetime` attribute'undan) alır.
    *   Tarayıcının yerel zaman dilimini (`Intl.DateTimeFormat()...`) tespit eder ve bunu formdaki gizli `userTimezone` input'una yazar.
    *   UTC zamanını JavaScript `Date` nesnesine çevirir.
    *   Bu `Date` nesnesini kullanarak, tarihi (YYYY/MM/DD) ve saati (HH:MM:SS) kullanıcının yerel zaman dilimine göre formatlayıp ilgili input alanlarına (`startDate`, `startTimeOnly`) yazar.
    *   Eğer backend'den bir zaman gelmediyse (yeni oyun), o anki yerel tarih ve saati inputlara yazar.
    *   Form gönderilirken (`submit` event listener), güncel zaman diliminin gizli input'ta olduğundan emin olur (genellikle ilk ayarlama yeterlidir). Bu sayede backend, kullanıcının hangi zaman diliminde tarih/saat girdiğini bilir.

### 2.3. `monitor.html` JavaScript Mantığı

Bu sayfa, yöneticinin bir oyunu canlı olarak izlemesini sağlar. Harita üzerinde oyuncu konumları, izledikleri yollar, skor tablosu ve hız grafiği periyodik olarak güncellenir.

*   **Harita ve Grafik Başlatma:**
    *   Leaflet haritası (`L.map`) ve ECharts bar grafiği (`echarts.init`) oluşturulur.
    *   Harita katmanları (`osmLayer`, `satelliteLayer`) ve geçiş mekanizması (`toggleLayer`) `create_manage.html`'deki gibidir.
    *   **Başlangıç Verileri:** Sayfa ilk yüklendiğinde, Django şablonu (`{% for player in players %}`, `{{ waypoints|safe }}`) ile gelen veriler kullanılarak:
        *   Her oyuncu için son konumuna bir marker (`L.marker`) ve geçmiş konumlarından oluşan bir yol (`L.polyline`) çizilir. Oyuncuların ikonları (`getIcon`) ve yol renkleri atanır. Marker ve polyline'lar `markers` ve `polylines` nesnelerinde saklanır.
        *   Her waypoint için özel renkli (`marker_color` view'da belirlenir) ve etiketli (`label`) bir marker (`L.divIcon` ile özel HTML ikon, `L.marker`) oluşturulur ve `waypointMarkers` nesnesinde saklanır.
        *   Harita, tüm waypoint'leri içerecek şekilde otomatik olarak ayarlanır (`map.fitBounds`).
*   **Periyodik Güncelleme (`updateAll` ve `setInterval`):**
    *   `updateAll()` fonksiyonu:
        *   `fetch(window.location.href, { headers:{ 'X-Requested-With':'XMLHttpRequest' } })`: Mevcut sayfanın URL'sine (yani `monitor` view'ına) bir AJAX GET isteği gönderir. `X-Requested-With` başlığı, bunun bir AJAX isteği olduğunu backend'e bildirir.
        *   `.then(r => r.json())`: Başarılı olursa, gelen JSON yanıtını parse eder.
        *   `.then(data => ...)`: Gelen `data` (içinde güncel `players`, `waypoints`, `game_state`, `remaining_seconds` bilgileri bulunur) ile aşağıdaki güncelleme fonksiyonlarını çağırır:
            *   `updateMarkers(data.players)`
            *   `updateSpeedChart(data.players)`
            *   `renderPlayersTable(data.players)`
        *   Oyun durumunu (`data.game_state`) ve kalan süreyi (`data.remaining_seconds`) kontrol eder.
        *   Oyun bittiyse (`finished`), `setInterval`'ı durdurur (`clearInterval`), zamanlayıcıyı durdurur ve "Game Over" gösterir.
        *   Oyun devam ediyorsa (`running`), kalan süreye göre geri sayım sayacını (`countdownInterval`) başlatır veya günceller.
        *   Oyun başlamadıysa (`not_started`), "Not Started Yet" gösterir.
        *   `.catch(e => ...)`: `fetch` sırasında hata olursa konsola yazdırır.
    *   `updateInterval = setInterval(updateAll, 3000)`: `updateAll` fonksiyonunun her 3000 milisaniyede (3 saniyede) bir otomatik olarak çalışmasını sağlar.
    *   `updateAll()`: Sayfa yüklendiğinde ilk verileri çekmek için bir kez de başlangıçta çağrılır.
*   **Veri Güncelleme Fonksiyonları:**
    *   `updateMarkers(playersData)`:
        *   Gelen güncel `playersData` listesini işler.
        *   Her oyuncu için:
            *   ID'sini `activePlayerIds` kümesine ekler.
            *   Diskalifiye olmuşsa, haritadaki marker'ını ve polyline'ını kaldırır.
            *   Diskalifiye olmamışsa:
                *   Yeni konumunu (`latlng`) alır.
                *   Eğer oyuncu için haritada marker yoksa, yenisini oluşturur (`L.marker`).
                *   Varsa, mevcut marker'ın konumunu (`setLatLng`) ve ikonunu (`setIcon`) günceller.
                *   Yeni yol koordinatlarını (`pathCoords`) alır.
                *   Eğer polyline yoksa, yenisini oluşturur (`L.polyline`).
                *   Varsa, mevcut polyline'ın koordinatlarını (`setLatLngs`) günceller.
        *   `markers` ve `polylines` nesnelerindeki ID'leri kontrol eder. Eğer bir ID `activePlayerIds` içinde yoksa (yani oyuncu artık veri listesinde gelmiyorsa - pek olası değil ama), ilgili marker/polyline'ı haritadan kaldırır.
    *   `updateSpeedChart(playersData)`:
        *   Gelen `playersData` listesini işler.
        *   Diskalifiye olmamış oyuncuların isimlerini (`names`) ve hızlarını (`seriesData`) içeren listeler oluşturur. Hız verisi ECharts'ın beklediği formatta (`{ value: p.speed||0, itemStyle:{ color: ... } }`) hazırlanır.
        *   `chart.setOption({...}, { notMerge: false })` ile bar grafiğinin verilerini ve eksenlerini günceller. `notMerge: false` eski verilerin tamamen üzerine yazılmasını sağlar.
        *   `chart.resize()`: Grafik boyutunu ayarlar.
    *   `renderPlayersTable(playersData)`:
        *   Sol üstteki oyuncu skor tablosunun (`id="players-body"`) içeriğini günceller.
        *   Mevcut satırları (`existingRows`) ve gelen oyuncu ID'lerini (`processedPlayerIds`) takip eder.
        *   Her oyuncu için:
            *   Eğer tabloda satırı yoksa, yeni bir `<tr>` elemanı oluşturur, oyuncu adı, skoru ve "Disqualify" butonu ile doldurur ve tabloya ekler. Butona `handleDisqualifyClick` fonksiyonunu bağlar.
            *   Eğer satırı varsa, skorunu (`.score` class'lı `<td>`) ve "Disqualify" butonunun durumunu (`disabled`) günceller. Satırın üzerinin çizili olup olmadığını (`textDecoration`) diskalifiye durumuna göre ayarlar.
        *   Artık `playersData` içinde olmayan oyuncuların satırlarını tablodan kaldırır.
*   **Geri Sayım Sayacı:**
    *   `remainingTimeDisplay`: Kalan sürenin gösterileceği `<span>` elemanı.
    *   `remainingSeconds`: Backend'den gelen kalan süre (saniye).
    *   `gameState`: Backend'den gelen oyun durumu.
    *   `countdownInterval`: `setInterval` tarafından döndürülen ID, sayacı durdurmak için kullanılır.
    *   `formatTime(seconds)`: Saniyeyi HH:MM:SS formatına çevirir.
    *   `startCountdown()`: Sayacı başlatır. Eğer oyun "running" ve süre > 0 ise, `setInterval` ile her saniye `remainingSeconds`'ı azaltır ve `remainingTimeDisplay`'i günceller. Süre bitince veya oyun durumu değişince `clearInterval` ile sayaç durdurulur. `updateAll` içinde gerektiğinde çağrılır.
*   **Diskalifiye İşlemi:**
    *   `handleDisqualifyClick()`: Tablodaki "Disqualify" butonlarına tıklanınca çalışır.
    *   Onay (`confirm`) ister.
    *   Oyuncu ID'sini butonun `data-player-id` attribute'undan alır.
    *   `fetch` ile backend'deki `monitor` view'ına bir AJAX POST isteği gönderir. İstek gövdesinde (`body`) `player_id` bulunur. `X-CSRFToken` başlığı ile CSRF token'ı gönderilir.
    *   Başarılı JSON yanıtı (`{status: 'success'}`) gelirse, `updateAll()` fonksiyonunu çağırarak arayüzün hemen güncellenmesini sağlar (diskalifiye edilen oyuncu tablodan ve haritadan kalkar). Hata olursa mesaj gösterir.

### 2.4. `results.html` JavaScript Mantığı

Bu sayfa, bitmiş bir oyunun sonuçlarını, skor tablosunu, kazananı, podyumu ve oyuncuların oyun başındaki ve sonundaki ortalama hızlarını gösteren bir çizgi grafik içerir.

*   **Navigasyon:**
    *   `goMenu()`: "Back to Main Menu" butonuna tıklanınca çalışır ve kullanıcıyı ana menüye yönlendirir (`window.location.href`).
*   **Zaman Dilimi Gösterimi (`DOMContentLoaded`):**
    *   Sayfa yüklendiğinde çalışır.
    *   Alt başlık (`subheader`) kısmındaki `data-utc-datetime` attribute'undan oyunun başlangıç zamanını (UTC) alır.
    *   `create_manage.html`'deki gibi, bu UTC zamanını kullanıcının yerel zaman dilimine çevirir ve YYYY-MM-DD HH:MM formatında alt başlıkta (`gameTimeDisplay`) gösterir.
*   **Hız Grafiği (ECharts):**
    *   `speedData = JSON.parse('{{ speed_data|escapejs }}')`: View fonksiyonunda `json.dumps` ile oluşturulan ve `{{ speed_data|escapejs }}` ile HTML'e güvenli bir şekilde yerleştirilen JSON string'ini JavaScript nesnesine çevirir. `speed_data` şu yapıda bir nesnedir:
        ```javascript
        {
          labels: ['StartTime', 'EndTime'], // X ekseni etiketleri
          players: [
            { name: 'Player1', speeds: [startSpeed, endSpeed], icon: 'red' },
            { name: 'Player2', speeds: [startSpeed, endSpeed], icon: 'cyan' },
            // ...
          ]
        }
        ```
    *   `chart = echarts.init(...)`: `id="speed-chart"` olan `div` içine bir ECharts grafiği oluşturur.
    *   `option = {...}`: Grafiğin yapılandırma (konfigürasyon) ayarlarını içeren bir nesne oluşturur:
        *   `title`: Grafik başlığı.
        *   `tooltip`: Fare ile üzerine gelince bilgi gösteren kutucuk ayarları.
        *   `legend`: Grafikteki her çizginin (oyuncunun) adını gösteren kısım.
        *   `xAxis`: X ekseni ayarları (tipi kategori, verisi `speedData.labels`).
        *   `yAxis`: Y ekseni ayarları (tipi sayısal değer, adı 'Speed (km/h)', minimum değeri 0).
        *   `series`: Grafikte çizilecek verileri tanımlar. `speedData.players` listesi üzerinde `map` fonksiyonu kullanılarak her oyuncu için bir seri nesnesi oluşturulur:
            *   `name`: Oyuncunun adı (legend için).
            *   `type: 'line'`: Grafik tipi çizgi.
            *   `data`: Oyuncunun hız verileri (`speeds` listesi - başlangıç ve bitiş hızı).
            *   `smooth: true`: Çizgiyi yumuşak yapar.
            *   `lineStyle`, `itemStyle`: Çizginin ve noktaların rengini oyuncunun ikon rengine göre ayarlar.
    *   `chart.setOption(option)`: Hazırlanan `option` nesnesi ile grafiği çizer.

### 2.5. `main_menu.html` JavaScript Mantığı

Bu sayfada genellikle karmaşık JavaScript işlemleri bulunmaz. Temel etkileşimler standart HTML formları ve linkler üzerinden yapılır.

*   **Formlar:**
    *   "Create Game" butonu bir form içindedir (`<form method="post">`). Tıklandığında, form (içinde `{% csrf_token %}` ile birlikte) backend'deki `main_menu` view'ına bir POST isteği gönderir. View bu isteği yakalar ve yeni oyun oluşturma mantığını çalıştırır.
    *   Her oyun satırındaki "Delete" butonu da kendi küçük formu içindedir. Bu form, gizli bir input (`<button type="submit" name="delete_game" value="{{ game.game_id }}">`) ile silinecek oyunun ID'sini taşır. Tıklandığında, bu form `main_menu` view'ına POST isteği gönderir, view `delete_game` parametresini kontrol eder ve silme işlemini yapar.
*   **Linkler (`<a>`):**
    *   "Monitor", "Results", "Manage" butonları, `{% url %}` etiketi ile oluşturulmuş linklerdir ve kullanıcıyı ilgili view fonksiyonlarına (ve dolayısıyla sayfalara) yönlendirirler.
*   **Zaman Dilimi Gösterimi (`DOMContentLoaded`):**
    *   `results.html`'dekine benzer şekilde çalışır.
    *   Tablodaki her oyun satırı (`<tr>`) için `data-utc-datetime` attribute'undan oyunun başlangıç zamanını (UTC) okur.
    *   Bu UTC zamanını kullanıcının yerel zaman dilimine çevirir.
    *   Tarihi (DD/MM/YYYY) `.game-date` class'lı `<td>` içine, saati (HH:MM) ise `.game-time` class'lı `<td>` içine yazar. Bu, listedeki oyun zamanlarının kullanıcının kendi saatine göre doğru görünmesini sağlar.

---