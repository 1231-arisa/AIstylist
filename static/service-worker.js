self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open('camgeo-v1').then(function(cache) {
      return cache.addAll([
        '/',
        '/static/manifest.json',
        '/static/icon-192.png',
        '/static/icon-512.png',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
        'https://code.jquery.com/jquery-3.7.1.min.js',
        'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
      ]);
    })
  );
});

self.addEventListener('fetch', function(e) {
  e.respondWith(
    caches.match(e.request).then(function(response) {
      return response || fetch(e.request);
    })
  );
});
