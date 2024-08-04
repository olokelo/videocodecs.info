async function main() {

  const response = await fetch(`/data/clips.json`);
  const clips = await response.json();

  const clip_list_div = document.getElementById('clip-list');

  for (const clipname of Object.keys(clips.clips)) {

    const clipdesc = clips.clips[clipname]['desc'];
    const clipsrc = clips.clips[clipname]['src'];

    const p = document.createElement('p');
    const a = document.createElement('a');
    const s = document.createElement('a');

    a.href = `/graph/?clipname=${clipname}`;
    a.textContent = clipname;
    p.appendChild(a);

    const desctext = document.createTextNode(` - ${clipdesc} - `);
    p.appendChild(desctext);

    s.href = clipsrc;
    s.textContent = 'source';
    p.appendChild(s);

    clip_list_div.append(p);
  }

}

document.addEventListener('DOMContentLoaded', main);
