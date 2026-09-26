// Ids are page-global once inlined. In the second and later copies of this
// diagram on one page, suffix every id and rewrite the references to them
// (href, url(#...), SMIL syncbase begin/end), so animation timing binds to
// this copy's own elements instead of the first copy's.
{
  const copies = [...document.querySelectorAll('.fg-diagram.' + root.classList[1])];
  const nth = copies.indexOf(root);
  if (nth > 0) {
    const sfx = '-i' + nth;
    const ids = new Set();
    root.querySelectorAll('[id]').forEach((el) => { ids.add(el.id); el.id += sfx; });
    root.querySelectorAll('*').forEach((el) => {
      for (const a of [...el.attributes]) {
        let v = a.value;
        if ((a.name === 'href' || a.name === 'xlink:href') && v[0] === '#' && ids.has(v.slice(1))) v += sfx;
        else if (a.name === 'begin' || a.name === 'end') {
          v = v.replace(/([\w-]+)\.(begin|end)/g, (m, id, e) => (ids.has(id) ? id + sfx + '.' + e : m));
        } else v = v.replace(/url\(#([\w-]+)\)/g, (m, id) => (ids.has(id) ? 'url(#' + id + sfx + ')' : m));
        if (v !== a.value) el.setAttribute(a.name, v);
      }
    });
  }
}
