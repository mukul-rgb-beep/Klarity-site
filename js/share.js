/* Share bar: reveal Share… where the browser has a share sheet, and make Copy link work. */
(function () {
  var bar = document.querySelector('.share-bar');
  if (!bar) return;
  var url = bar.getAttribute('data-url'), title = bar.getAttribute('data-title');
  var native = bar.querySelector('[data-share-native]');
  if (native && navigator.share) {
    native.hidden = false;
    native.addEventListener('click', function () {
      navigator.share({ title: title, url: url }).catch(function () {});
    });
  }
  var copy = bar.querySelector('[data-share-copy]');
  if (!copy) return;
  var label = copy.querySelector('span');
  function done(ok) {
    label.textContent = ok ? 'Copied' : 'Press ⌘C to copy';
    setTimeout(function () { label.textContent = 'Copy link'; }, 2200);
  }
  function fallback() {
    var t = document.createElement('textarea');
    t.value = url; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
    document.body.appendChild(t); t.select();
    var ok = false; try { ok = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(t); done(ok);
  }
  copy.addEventListener('click', function () {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () { done(true); }, fallback);
    } else { fallback(); }
  });
})();

/* "Send this to my Mac" on a product card: the share sheet where the browser has one.
   Without it, or without this script, the link's own mailto: opens instead. Nothing is collected. */
(function () {
  var links = document.querySelectorAll('[data-send-mac]');
  if (!links.length || !navigator.share) return;
  Array.prototype.forEach.call(links, function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      navigator.share({ title: a.getAttribute('data-title'), url: a.getAttribute('data-url') }).catch(function () {});
    });
  });
})();
