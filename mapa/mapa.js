/* Mapa dojazdów z Iławy do aeroklubów i obszaru bez lądowiska (biała plama).
 * Biblioteka: Leaflet (cdnjs). Podkład: OpenStreetMap.
 * Trasy drogowe liczy publiczny serwer OSRM w przeglądarce odwiedzającego.
 * Gdy serwer OSRM nie odpowiada, mapa rysuje linię prostą (przerywaną).
 * Granica powiatu: powiat-ilawski.geojson (uproszczona, źródło: ppatrzyk/polska-geojson). */

(function () {
  'use strict';

  var START = { nazwa: 'Iława', lat: 53.5965, lon: 19.5685 };

  // Aerokluby: cele dojazdów. kolor = kolor trasy i znacznika.
  var AEROKLUBY = [
    { id: 'olsztyn', nazwa: 'Aeroklub Warmińsko-Mazurski', lotnisko: 'Olsztyn-Dajtki (EPOD)', lat: 53.7739, lon: 20.4135,
      opis: 'Szkolenie samolotowe, szybowcowe, motoszybowcowe, ultralekkie i spadochronowe. Aeroklub działa od 1946 roku.', www: 'https://aeroklub.olsztyn.pl/', kolor: '#0b5cad' },
    { id: 'grudziadz', nazwa: 'Aeroklub Nadwiślański', lotnisko: 'Grudziądz-Lisie Kąty (EPGI)', lat: 53.52442, lon: 18.84947,
      opis: 'Kurs szybowcowy (SPL), kursy PPL i LAPL. Wyciągarka szybowcowa i samoloty holujące.', www: 'https://lisie.pl/', kolor: '#7a3fb5' },
    { id: 'elblag', nazwa: 'Aeroklub Elbląski', lotnisko: 'Elbląg (EPEL)', lat: 54.1412, lon: 19.4231,
      opis: 'Lotnisko użytku wyłącznego.', www: 'http://aeroklubelblaski.pl/', kolor: '#0f8a5f' },
    { id: 'warszawa', nazwa: 'Aeroklub Warszawski', lotnisko: 'Warszawa-Babice (EPBC)', lat: 52.2692, lon: 20.9072,
      opis: 'Współorganizator fiesty balonowej w gminie Iława w 2022 roku.', www: 'https://aeroklub.waw.pl/', kolor: '#64748b' }
  ];

  // Inne miejsca lotnicze (bez trasy).
  var LADOWISKA = [
    { nazwa: 'Gryźliny (EPGR)', lat: 53.60806, lon: 20.34444, opis: 'Lądowisko samolotowe w ewidencji ULC od 2007 roku. Zgłaszający: Starostwo Powiatowe w Olsztynie. Obok baza Lotniczego Pogotowia Ratunkowego.' },
    { nazwa: 'Stary Kamień k. Prabut', lat: 53.724122, lon: 19.205330, opis: 'Lądowisko poza ewidencją ULC, pas trawiasty 520 × 30 m. Dzierżawa terenu się skończyła: lądowisko może być wyłączone z użytkowania.' }
  ];

  var map = L.map('mapa', { scrollWheelZoom: false }).setView([53.55, 19.65], window.innerWidth < 600 ? 7 : 8);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, trasy: <a href="https://project-osrm.org/">OSRM</a>'
  }).addTo(map);
  map.on('focus', function () { map.scrollWheelZoom.enable(); });
  map.on('blur', function () { map.scrollWheelZoom.disable(); });

  function pin(kolor, ikona) {
    return L.divIcon({
      className: '', iconSize: [30, 30], iconAnchor: [15, 30], popupAnchor: [0, -28],
      html: '<div class="pin" style="background:' + kolor + '"><i class="fa-solid ' + ikona + '"></i></div>'
    });
  }

  function km(a, b) {
    var R = 6371, r = Math.PI / 180;
    var dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  function czas(sekundy) {
    var m = Math.round(sekundy / 60);
    return m < 60 ? m + ' min' : Math.floor(m / 60) + ' h ' + String(m % 60).padStart(2, '0') + ' min';
  }

  // Biała plama: powiat iławski.
  fetch('powiat-ilawski.geojson').then(function (r) { return r.json(); }).then(function (g) {
    var warstwa = L.geoJSON(g, {
      style: { color: '#b42318', weight: 2, dashArray: '6 4', fillColor: '#b42318', fillOpacity: 0.12 }
    }).addTo(map);
    warstwa.bindTooltip('Biała plama: powiat iławski bez lądowiska dla samolotów i szybowców', { sticky: true });
    warstwa.bringToBack();
    // Etykieta w południowej części powiatu, żeby nie zasłaniać znacznika Iławy.
    L.marker([53.45, 19.62], {
      interactive: false,
      icon: L.divIcon({ className: '', iconSize: [120, 40], iconAnchor: [60, 20],
        html: '<div class="spot-label">Biała plama<br><small style="font-weight:500">brak lądowiska</small></div>' })
    }).addTo(map);
  }).catch(function () { /* mapa działa bez granicy powiatu */ });

  // Pierścienie odległości od Iławy.
  [50, 100].forEach(function (r) {
    L.circle([START.lat, START.lon], {
      radius: r * 1000, color: '#6b7280', weight: 1, dashArray: '2 6', fill: false, interactive: false
    }).addTo(map);
    L.marker([START.lat + r / 111.2, START.lon], {
      interactive: false,
      icon: L.divIcon({ className: '', html: '<span style="font:600 12px Inter,sans-serif;color:#6b7280;background:rgba(255,255,255,.8);padding:1px 4px;border-radius:4px">' + r + ' km</span>', iconSize: [50, 16], iconAnchor: [25, 8] })
    }).addTo(map);
  });

  L.marker([START.lat, START.lon], { icon: pin('#111827', 'fa-house'), zIndexOffset: 1000 })
    .bindPopup('<b>Iława</b><br>Punkt startu. Jedyne lądowisko w powiecie w ewidencji ULC: przyszpitalne lądowisko dla śmigłowców.')
    .addTo(map);

  LADOWISKA.forEach(function (l) {
    L.marker([l.lat, l.lon], { icon: pin('#a16207', 'fa-plane-arrival') })
      .bindPopup('<b>' + l.nazwa + '</b><br>' + l.opis).addTo(map);
  });

  var tabela = document.getElementById('dojazdy');

  AEROKLUBY.forEach(function (a) {
    var prosto = Math.round(km(START, a));
    L.marker([a.lat, a.lon], { icon: pin(a.kolor, 'fa-plane') })
      .bindPopup('<b>' + a.nazwa + '</b><br>' + a.lotnisko + '<br>' + a.opis + '<br><a href="' + a.www + '">Strona aeroklubu</a>')
      .addTo(map);

    var tr = document.createElement('tr');
    tr.innerHTML =
      '<td><span class="dot" style="background:' + a.kolor + '"></span><a href="' + a.www + '">' + a.nazwa + '</a></td>' +
      '<td>' + a.lotnisko + '</td>' +
      '<td class="num">' + prosto + ' km</td>' +
      '<td class="num" data-droga>…</td>' +
      '<td class="num" data-czas>…</td>';
    tabela.appendChild(tr);

    var url = 'https://router.project-osrm.org/route/v1/driving/' +
      START.lon + ',' + START.lat + ';' + a.lon + ',' + a.lat + '?overview=simplified&geometries=geojson';

    fetch(url).then(function (r) {
      if (!r.ok) { throw new Error(r.status); }
      return r.json();
    }).then(function (d) {
      var t = d.routes[0];
      L.geoJSON(t.geometry, { style: { color: a.kolor, weight: 4, opacity: 0.85 } })
        .bindTooltip(a.lotnisko + ': ' + Math.round(t.distance / 1000) + ' km, ' + czas(t.duration), { sticky: true })
        .addTo(map);
      tr.querySelector('[data-droga]').textContent = Math.round(t.distance / 1000) + ' km';
      tr.querySelector('[data-czas]').textContent = czas(t.duration);
    }).catch(function () {
      L.polyline([[START.lat, START.lon], [a.lat, a.lon]], { color: a.kolor, weight: 3, dashArray: '8 6' }).addTo(map);
      tr.querySelector('[data-droga]').textContent = 'brak danych';
      tr.querySelector('[data-czas]').textContent = '–';
    });
  });
})();
