var CACHE = "piv-v1";
var ASSETS = [
  "/paris-invaders/",
  "/paris-invaders/index.html",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
  "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css",
  "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css",
  "https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"
];
self.addEventListener("install", function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){return c.addAll(ASSETS).catch(function(){});}));
  self.skipWaiting();
});
self.addEventListener("activate", function(e){
  e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==CACHE;}).map(function(k){return caches.delete(k);}));}));
  self.clients.claim();
});
self.addEventListener("fetch", function(e){
  if(e.request.method!=="GET")return;
  e.respondWith(caches.match(e.request).then(function(cached){
    var fresh = fetch(e.request).then(function(r){
      if(r&&r.status===200){var c=r.clone();caches.open(CACHE).then(function(cache){cache.put(e.request,c);});}
      return r;
    }).catch(function(){return cached;});
    return cached || fresh;
  }));
});
self.addEventListener("notificationclick", function(e){
  e.notification.close();
  e.waitUntil(clients.matchAll({type:"window"}).then(function(cs){
    if(cs.length>0){cs[0].focus();}else{clients.openWindow("/paris-invaders/");}
  }));
});