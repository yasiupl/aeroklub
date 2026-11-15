/* Aktualności on the home page.
 * Now: the official Facebook Page Plugin (timeline), loaded only after the visitor clicks the button.
 * Before the click the page sends no request to Facebook and Facebook sets no cookies.
 * Later: a fediverse feed can replace this source; the Facebook plugin stays as the fallback. */
(function () {
  'use strict';

  var box = document.getElementById('aktualnosci-feed');
  var btn = document.getElementById('aktualnosci-pokaz');
  if (!box || !btn) return;

  var PAGE_URL = box.getAttribute('data-facebook-page');
  btn.hidden = false;

  function pluginUrl(width, height) {
    var p = {
      href: PAGE_URL,
      tabs: 'timeline',
      width: width,
      height: height,
      small_header: 'false',
      adapt_container_width: 'true',
      hide_cover: 'false',
      show_facepile: 'false',
      locale: 'pl_PL'
    };
    return 'https://www.facebook.com/plugins/page.php?' + Object.keys(p).map(function (k) {
      return k + '=' + encodeURIComponent(p[k]);
    }).join('&');
  }

  btn.addEventListener('click', function () {
    // The plugin accepts widths from 180 to 500 px.
    var width = Math.max(180, Math.min(500, Math.floor(box.clientWidth)));
    var height = window.innerWidth < 600 ? 600 : 700;
    var frame = document.createElement('iframe');
    frame.src = pluginUrl(width, height);
    frame.width = width;
    frame.height = height;
    frame.title = 'Aktualności Aviava na Facebooku';
    frame.setAttribute('scrolling', 'no');
    frame.setAttribute('allow', 'encrypted-media');
    frame.className = 'fb-plugin';
    box.innerHTML = '';
    box.appendChild(frame);
    btn.parentNode.removeChild(btn);
    var note = document.getElementById('aktualnosci-uwaga');
    if (note) note.parentNode.removeChild(note);
  });
})();
