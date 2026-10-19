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
