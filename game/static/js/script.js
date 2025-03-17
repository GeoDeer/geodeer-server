document.addEventListener("DOMContentLoaded", function () {
    // Leaflet Harita Başlat
    let map = L.map('map', {
        center: [39.866703, 32.735556],
        zoom: 15,
        zoomControl: true,
        dragging: true,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        touchZoom: true
    });

    // OpenStreetMap Katmanı
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Buton Fonksiyonları
    document.querySelector(".main-menu").addEventListener("click", function() {
        alert("Back to Main Menu");
    });

    document.querySelector(".show-results").addEventListener("click", function() {
        alert("Showing the Results");
    });
});
