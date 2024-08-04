const plot_selectors = {

  'bitrate mean': {'unit': 'kbps', 'short': 'bitrate', 'sel1': 'probe', 'sel2': 'bitrate (kbps)'},

  'vmaf score mean': {'unit': null, 'short': 'vmaf', 'sel1': 'vmaf', 'sel2': 'mean'},
  'vmaf score stdev': {'unit': null, 'short': 'vmaf stdev', 'sel1': 'vmaf', 'sel2': 'std dev'},

  'ssimulacra2 score mean': {'unit': null, 'short': 'ssimulacra2', 'sel1': 'ssimulacra2', 'sel2': 'mean'},
  'ssimulacra2 score stdev': {'unit': null, 'short': 'ssimulacra2 stdev', 'sel1': 'ssimulacra2', 'sel2': 'std dev'},

  'encoding time': {'unit': 's', 'short': 'enc time', 'sel1': 'encode', 'sel2': 'time (s)'},
  'decoding time': {'unit': 's', 'short': 'dec time', 'sel1': 'decode', 'sel2': 'time (s)'},

  'encoding cpu mean': {'unit': '%', 'short': 'enc cpu', 'sel1': 'encode', 'sel2': 'cpu mean (%)'},
  'decoding cpu mean': {'unit': '%', 'short': 'dec cpu', 'sel1': 'decode', 'sel2': 'cpu mean (%)'},

  'encoding memory mean': {'unit': 'B', 'short': 'enc ram', 'sel1': 'encode', 'sel2': 'ram mean (B)'},
  'decoding memory mean': {'unit': 'B', 'short': 'dec ram', 'sel1': 'decode', 'sel2': 'ram mean (B)'},

}

var global_json = undefined;
var global_chart = undefined

function on_point_click(codec_name, quality_value) {

  const m = new Modal(codec_name, quality_value);

  console.log(codec_name, quality_value);
  m.create_selectors();
  m.plot_render();
  m.show();
}

function get_series(lsel1, lsel2, rsel1, rsel2) {

  var series = [];

  // sorting global_json by key, actually pretty hard
  const gj_sorted = Object.fromEntries(Object.entries(global_json).sort());

  for (const [group_name, group_data] of Object.entries(gj_sorted)) {

    var cur_item = {name: group_name, data: [], visible: true};

    //var sorted_points = group_data.points.sort(bitrate_sorter);

    for (const point of group_data.points) {

      if (!point) {
        continue;
      }

      if (!point[lsel1] || !point[rsel1] || !point.quality) {
        cur_item.data.push({
          "name": null,
          "x": null,
          "y": null
        });
        continue;
      }

      /* old
      cur_item.data.push({
        "name": "quality: " + (point["crf"] || point["q"]),
        "x": point["bitrate (kbps)"],
        "y": point["vmaf"]
      });*/
      cur_item.data.push({

        "name": "quality: " + point["quality"],
        "x": point[lsel1][lsel2],
        "y": point[rsel1][rsel2],

        events: {
          click: function() {
            on_point_click(group_name, point["quality"]);
          }
        }
      });

    }

    cur_item.data.sort(cur_item_sorter);
    series.push(cur_item);
  }

  return series;

}

function print_clip_info(input_md) {
  const clip_title = document.getElementById("clip-title");
  const clip_metadata = document.getElementById("clip-metadata");
  const visual_comparison_url = document.getElementById("visual-comparison-url");

  clip_title.textContent = input_md.title;
  clip_metadata.textContent = `${input_md.frames} frames: ${input_md.width} x ${input_md.height} @ ${input_md.fps} fps`
  visual_comparison_url.href = `/vivict/?clipname=${input_md.clipname}`
}

function create_selectors(x_axis_choice, y_axis_choice) {

  const xas = document.getElementById('x-axis-selector');
  const yas = document.getElementById('y-axis-selector');

  var choice_idx = 0;

  for (const cas of [xas, yas]) {

    if (cas.nodeName !== 'SELECT') {
      continue;
    }

    for (const sel_name of Object.keys(plot_selectors)) {
      const option = document.createElement('option');
      option.text = sel_name;
      option.value = sel_name;

      if ((x_axis_choice === sel_name && cas === xas) || (y_axis_choice === sel_name && cas === yas)) {
        option.selected = true;
        choice_idx++;
      }

      cas.add(option);

    }

  }

  // if user had choosen both axis names then render it immediately
  // TODO: needs testing
  if (choice_idx === 2) {
    plot_render();
  }

}

function plot_render() {

  const xas = document.getElementById('x-axis-selector');
  const yas = document.getElementById('y-axis-selector');

  var disabled_series = [];
  if (global_chart !== undefined) {
    const legend_items = global_chart.legend.allItems;
    disabled_series = legend_items.filter(x => !x.visible).map(x => x.name);
    console.log("Disabled: " + disabled_series);
    global_chart.destroy();
    global_chart = undefined;
  }

  if (xas.value === yas.value) {
    return;
  }

  const xpo = plot_selectors[xas.value];
  const ypo = plot_selectors[yas.value];

  series = get_series(xpo.sel1, xpo.sel2, ypo.sel1, ypo.sel2);
  for (const item of series) {
    if (disabled_series.includes(item.name)) {
      item.visible = false;
    }
  }

  console.log(series);
  global_chart = make_plot(
    series, 'container', '',
    str_add_unit(xas.value, xpo.unit),
    str_add_unit(xpo.short, xpo.unit),

    str_add_unit(yas.value, ypo.unit),
    str_add_unit(ypo.short, ypo.unit)
  );

  // add current selection to url params so that somebody could copy and share url
  const urlParams = new URLSearchParams(window.location.search);
  urlParams.set("x_axis_choice", xas.value);
  urlParams.set("y_axis_choice", yas.value);
  window.history.replaceState(null, null, "?"+urlParams);
}

async function fetch_and_plot() {

  const urlParams = new URLSearchParams(window.location.search);
  const clipname = urlParams.get('clipname');
  const x_axis_choice = urlParams.get('x_axis_choice');
  const y_axis_choice = urlParams.get('y_axis_choice');

  console.log("Clipname: " + clipname);

  if (clipname === null) {
    return;
  }

  const response = await fetch(`/data/${clipname}/metafile.json`);
  global_json = await response.json();
  console.log(global_json);

  print_clip_info(global_json["input metadata"]);
  delete global_json["input metadata"];
  delete global_json["original"];

  create_selectors(x_axis_choice, y_axis_choice);

}

document.addEventListener('DOMContentLoaded', fetch_and_plot);
