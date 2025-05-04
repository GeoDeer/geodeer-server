# geodeer-server

## Proje Dokümantasyonu (Türkçe)

Bu dokümantasyon, GeoDeer projesinin backend ve frontend bileşenlerinin detaylı bir açıklamasını sunmaktadır.

### 1. Backend Mimarisi

#### 1.1. Modeller (`game/models.py`)

Veritabanı yapısını tanımlar. GeoDjango kullanılarak coğrafi veriler işlenir.

*   **`User`**: Kullanıcı bilgilerini (ID, kullanıcı adı, e-posta, şifre) tutar.

*   **`Game`**: Oyunun temel bilgilerini içerir:
    *   `game_id`: Otomatik artan birincil anahtar.  #primary key
    *   `game_name`: Oyunun adı.
    *   `start_date_time`: Oyunun başlangıç tarihi ve saati.
    *   `number_of_players`: Oyuncu sayısı (FloatField?).
    *   `time`: Oyun süresi (FloatField?).
    *   `invite_id`: Otomatik üretilen davet kodu (`generate_invite_id` metodu ile).
    *   `game_creator`: Oyunu oluşturan `User` ile ForeignKey ilişkisi (`related_name='created_games'`).
    *   `save()` metodu: İlk kayıtta `invite_id` otomatik oluşturulur.

*   **`Waypoint`**: Oyundaki hedef noktaları temsil eder:
    *   `waypoint_id`: Otomatik artan birincil anahtar.
    *   `game`: Ait olduğu `Game` ile ForeignKey ilişkisi (`related_name='waypoints'`).
    *   `waypoint_name`: Noktanın adı.
    *   `is_last`: Bu noktanın son hedef olup olmadığını belirten Boolean bayrak (`update_is_last_flag` ile güncellenir).
    *   `lat`, `lon`, `height`: Coğrafi koordinatlar ve yükseklik.
    *   `hint`, `question`, `answer`: Nokta ile ilgili ipucu, soru ve cevap.
    *   `ques_dif_level`: Soru zorluk seviyesi.
    *   `waypoint_geom`: Noktanın GeoDjango `PointField` geometrisi (SRID 4326).
    *   `waypoint_buffer`: Nokta etrafında oluşturulan `PolygonField` tampon bölge (`create_buffer` metodu ile oluşturulur, SRID 4326).
    *   `create_buffer()`: Belirtilen mesafede (varsayılan 5m) tampon bölge oluşturur, projeksiyon dönüşümleri (4326 -> 3857 -> 4326) kullanır.
    *   `save()`: `waypoint_geom` ve `waypoint_buffer`'ı oluşturur/günceller. `update_is_last_flag` ve `create_question` metodlarını tetikler. # update_is_last deperi konum eğer son noktaysa true olarak döner
    *   `update_is_last_flag()`: Oyun içindeki waypoint'leri ID'ye göre sıralayarak sonuncusunun `is_last` bayrağını `True` yapar, diğerlerini `False`.
    *   `create_question()`: Eğer bu waypoint için henüz `Question` nesnesi yoksa, otomatik olarak bir tane oluşturur. #boş olarak 

*   **`UserLocation`**: Oyuncuların konum güncellemelerini kaydeder:
    *   `user`, `game`: İlgili `User` ve `Game` ile ForeignKey ilişkileri. # user dediğimiz değer oyunu oyanayan kulanıcnın id si -- game dediğimiz de oyunun id si
    *   `lat`, `lon`: Konum koordinatları.
    *   `location_geom`: Konumun GeoDjango `PointField` geometrisi (SRID 4326).
    *   `time_stamp`: Konumun kaydedildiği zaman damgası.
    *   `time_diff`: Bir önceki konuma göre geçen süre (saat cinsinden).
    *   `distance`: Bir önceki konuma olan mesafe (metre cinsinden, GeoDjango ile hesaplanır).
    *   `speed`: Hesaplanan hız (km/s).
    *   `save()`: Yeni konum kaydedilirken, bir önceki konuma göre `time_diff`, `distance` ve `speed` hesaplanır. Eğer bu, kullanıcının oyundaki ilk konumu ise, `UserScore` tablosunda ilgili kullanıcı için bir kayıt oluşturulur (`transaction.on_commit` ile).

*   **`UserScore`**: Oyuncuların skorlarını ve durumlarını tutar:
    *   `user`, `game`: İlgili `User` ve `Game` ile ForeignKey ilişkileri.
    *   `location_score`, `time_score`, `ques_score`, `total_score`: Farklı kategorilerdeki ve toplam skorlar.
    *   `is_disqualified`: Oyuncunun diskalifiye olup olmadığını belirtir.
    *   `end_date_time`: Oyuncunun oyunu bitirdiği zaman.
    *   `save()`: `end_date_time` alanı güncellendiğinde (ve ilk kez null değilse), `game.services.score_calculator.calculate_scores_for_game` fonksiyonunu çağırarak tüm oyunun skorlarını yeniden hesaplar.

*   **`Question`**: Waypoint'lerde sorulan soruları ve cevap durumlarını yönetir:
    *   `game`, `user`, `waypoint`: İlgili `Game`, `User` (cevaplayan) ve `Waypoint` ile ForeignKey ilişkileri.
    *   `ques_dif_level`: Soru zorluk seviyesi (Waypoint'ten alınabilir).
    *   `answer_time`: Cevaplama süresi.
    *   `is_correct`: Cevabın doğru olup olmadığını belirten Boolean.
    *   `save()`: Gerekli alanlar (zorluk, game, user) ilişkili `Waypoint` üzerinden otomatik doldurulabilir.

#### 1.2. API Views (`mobile/views.py`)

Mobil uygulama ile backend arasındaki RESTful API endpoint'lerini sağlar. Django REST Framework (DRF) kullanılır.

*   **Genel Yapı:** Her model için listeleme (`get_*`), oluşturma (`create_*`) ve detay (`*_detail` - GET, PUT, DELETE) view'ları bulunur.

*   **Decorator'lar:** `@api_view(['GET', 'POST', ...])` ile hangi HTTP metodlarının desteklendiği belirtilir.

*   **Serializer'lar:** Modelleri JSON'a ve JSON'dan modellere dönüştürmek ve veri doğrulamak için kullanılır (örn: `UserSerializer`, `GameSerializer`, `WaypointSerializer`, `QuestionSerializer`). `serializer.is_valid()` ile doğrulama yapılır.

*   **Yanıtlar:** `Response(serializer.data, status=...)` ile standart HTTP yanıtları ve durum kodları (örn: `status.HTTP_200_OK`, `status.HTTP_201_CREATED`, `status.HTTP_400_BAD_REQUEST`, `status.HTTP_404_NOT_FOUND`) döndürülür.

*   **Detay View'ları:** Genellikle `pk` (primary key) veya spesifik bir ID (örn: `question_detail` için `waypoint_id`) alarak ilgili nesne üzerinde işlem yaparlar. `Question` için `PUT` isteğinde `partial=True` kullanılarak kısmi güncelleme desteklenir.

#### 1.3. Web Views (`game/views.py` - Tahmin Edilen Mantık)

Web arayüzünü oluşturan view fonksiyonları.

*   **`main_menu(request, creator_id)`**:
    *   GET: Kullanıcının oyunlarını listeler, `main_menu.html`'i render eder.
    *   POST: Yeni oyun oluşturur (`create_manage`'e yönlendirir) veya mevcut bir oyunu siler.

*   **`create_manage_view(request, creator_id, game_id=None)`**:
    *   GET: Mevcut oyunu (`game_id` varsa) veya yeni oyun formunu yükler, `create_manage.html`'i render eder. Waypoint verilerini context'e ekler.
    *   POST: Formdan gelen genel oyun bilgilerini ve JSON formatındaki waypoint verilerini (`waypoints_data`) işler. `Game` ve ilişkili `Waypoint` nesnelerini oluşturur/günceller. Başarılı olunca `main_menu`'ye yönlendirir.

*   **`monitor_view(request, creator_id, pk)`**:
    *   GET: Oyun bilgilerini, waypoint'leri, oyuncu konum/skor/yol verilerini çeker. AJAX isteği ise sadece güncel oyuncu verilerini JSON olarak döner, normal istek ise `monitor.html`'i render eder.
    *   POST (AJAX): Gelen `player_id` ile ilgili oyuncuyu diskalifiye eder (`UserScore.is_disqualified=True`), başarı durumunu JSON döner.

*   **`results_view(request, creator_id, game_id)`**:
    *   GET: Oyun bilgilerini, sıralı oyuncu skorlarını (`UserScore`) ve zaman içindeki hız verilerini (`UserLocation`'dan işlenmiş) çeker. `results.html`'i render eder.

#### 1.4. URL Yönlendirmeleri (`GeoDeer/urls.py`, `game/urls.py`, `mobile/urls.py`)

URL'leri ilgili view fonksiyonlarına bağlar.

*   **`GeoDeer/urls.py`**: Ana yönlendirme dosyası. `/admin/`, `/main-menu/`, `/game/`, `/api/` gibi kök yolları tanımlar ve `include` ile alt uygulamaların URL'lerini dahil eder.

*   **`game/urls.py`**: Web arayüzü URL'lerini tanımlar (örn: `create-manage/`, `monitor/`, `results/`). Path converter'lar (`<int:creator_id>`, `<int:pk>`) kullanılır.

*   **`mobile/urls.py`**: API endpoint URL'lerini (`/api/` altında) tanımlar (örn: `users/`, `games/`, `waypoints/`, `questions/<int:waypoint_id>/`).

### 2. Frontend Mimarisi (Template İçindeki JavaScriptler)

#### 2.1. `create_manage.html` JavaScript

Oyun oluşturma ve düzenleme arayüzünün dinamik davranışlarını yönetir.

*   **Harita:** Leaflet kütüphanesi kullanılır. OSM ve Uydu katmanları eklenir, katman geçişi sağlanır. Mevcut waypoint'ler haritada gösterilir.

*   **Waypoint Yönetimi:**
    *   **Durum Değişkenleri:** `waypointCount`, `isSaved`, `isEditable`, `currentEditIndex` ile waypoint ekleme/düzenleme/silme işlemleri kontrol edilir.
    *   **Fonksiyonlar:**
        *   `editPin()`: Seçilen waypoint'i düzenleme moduna alır (marker sürüklenir, inputlar aktifleşir).
        *   `savePin()`: Düzenlenen waypoint'i kaydeder (marker kilitlenir, inputlar pasifleşir).
        *   `deletePin()`: Seçilen waypoint'i siler (marker ve sidebar'dan kaldırır).
        *   `addNewWaypoint()`: Sidebar'a ve potansiyel olarak haritaya yeni bir waypoint ekler, düzenleme moduna geçer.
        *   `updateTitles()`: Waypoint başlıklarını günceller.
    *   **Harita Etkileşimi:** Haritaya çift tıklama (`map.on('dblclick', ...)`) ile düzenleme modundaki waypoint'in konumu belirlenir/güncellenir.

*   **Konum Arama:** Nominatim API kullanılarak haritada konum araması yapılır (`searchLocation`).

*   **Oyunu Kaydetme:** "Save Game" butonu tıklandığında, tüm waypoint bilgileri (isim, soru, cevap, koordinatlar vb.) sidebar'dan ve haritadaki marker'lardan toplanır, JSON formatına çevrilir ve hidden bir input (`#waypointsData`) aracılığıyla ana form (`#gameInfoForm`) ile birlikte backend'e gönderilir.

#### 2.2. `monitor.html` JavaScript

Oyunun canlı olarak izlenmesini sağlar.

*   **Harita ve Grafik:** Leaflet haritası ve ECharts bar grafiği kullanılır.

*   **Başlangıç:** Mevcut oyuncuların konumları (özel ikonlarla) ve yolları haritada çizilir. Waypoint'ler de özel ikonlarla gösterilir.

*   **Periyodik Güncelleme:** `setInterval` ile düzenli aralıklarla (`updateAll`) backend'den AJAX isteği ile güncel veriler (oyuncu konumları, yolları, skorları, hızları, diskalifiye durumu) çekilir.

*   **Veri Güncelleme Fonksiyonları:**
    *   `updateMarkers()`: Gelen verilere göre haritadaki oyuncu marker'larını ve yollarını günceller/kaldırır.
    *   `updateSpeedChart()`: Gelen verilere göre ECharts bar grafiğini güncelleyerek anlık hızları gösterir.
    *   `renderPlayersTable()`: Gelen verilere göre sol üstteki oyuncu skor tablosunu yeniden oluşturur.

*   **Diskalifiye:** Tablodaki "Disqualify" butonları ile oyuncuyu diskalifiye etmek için backend'e AJAX POST isteği gönderilir. Başarılı olursa arayüz güncellenir (ilgili satır/marker/polyline kaldırılır veya durumu değiştirilir). *Not: Başlangıçta butonlar demo için pasif.*

#### 2.3. `results.html` JavaScript

Oyun sonuçlarını gösterir.

*   **Navigasyon:** `goMenu` fonksiyonu ile ana menüye dönüş sağlanır.

*   **Hız Grafiği:** ECharts kütüphanesi kullanılır.
    *   Backend'den JSON formatında gelen zaman içindeki ortalama hız verileri (`speed_data`) parse edilir.
    *   Bu veriler kullanılarak bir çizgi grafik (`line`) oluşturulur. X ekseni zamanı, Y ekseni hızı gösterir. Her oyuncu için ayrı bir çizgi çizilir ve renkleri ikonlarına göre belirlenir.

#### 2.4. `main_menu.html` JavaScript

Bu sayfada özel JavaScript kodu bulunmamaktadır. Temel işlemler HTML formları ve linkler üzerinden yapılır.