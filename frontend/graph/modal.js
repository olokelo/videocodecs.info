const plot_selectors_modal = {

  'encoding process cpu': {'unit': '%', 'short': 'enc cpu', 'unitx': 's', 'shortx': 'enc time', 'suffix': 'encode.process-stats.json', 'iter': 'records', 'selx': 'time_s', 'sel1': 'cpu_percent', 'sel2': undefined},
  'decoding process cpu': {'unit': '%', 'short': 'dec cpu', 'unitx': 's', 'shortx': 'dec time', 'suffix': 'decode.process-stats.json', 'iter': 'records', 'selx': 'time_s', 'sel1': 'cpu_percent', 'sel2': undefined},

  'encoding process memory': {'unit': 'B', 'short': 'enc ram', 'unitx': 's', 'shortx': 'enc time', 'suffix': 'encode.process-stats.json', 'iter': 'records', 'selx': 'time_s', 'sel1': 'mem_rss', 'sel2': undefined},
  'decoding process memory': {'unit': 'B', 'short': 'dec ram', 'unitx': 's', 'shortx': 'dec time', 'suffix': 'decode.process-stats.json', 'iter': 'records', 'selx': 'time_s', 'sel1': 'mem_rss', 'sel2': undefined},

  'frame bitrate': {'unit': 'kbps', 'short': 'bitrate', 'unitx': null, 'shortx': 'video frame', 'suffix': 'frame-bitrate.json', 'iter': 'frames', 'selx': 'frameNum', 'sel1': 'bitrate (kbps)', 'sel2': undefined},
  'frame vmaf score': {'unit': null, 'short': 'vmaf', 'unitx': null, 'shortx': 'video frame', 'suffix': 'vmaf.json', 'iter': 'frames', 'selx': 'frameNum', 'sel1': 'metrics', 'sel2': 'vmaf'},

}

class Modal {

  constructor(codec_name, quality_value) {

    this.codec_name = codec_name;
    this.quality_value = quality_value;

    this.mgs = document.getElementById('modal-graph-selector');
    this.main_chart = undefined;

    this.modal_close_btn = document.getElementById('modal-close-btn');
    this.modal_overlay = document.getElementById('modal-overlay');

    const mtl = document.getElementById('modal-title');
    mtl.textContent = `${codec_name} - quality ${quality_value}`;

    this.on_change_cb = this.plot_render.bind(this, false);
    this.mgs.addEventListener("change", this.on_change_cb);

    this.on_hide_cb = this.hide.bind(this);
    this.modal_close_btn.addEventListener("click", this.on_hide_cb);

    const mci_raw = document.getElementById('modal-codec-info-raw');
    mci_raw.href = this.get_data_path(this.get_selector_data_file('stats.yaml'));

    // find collection data directory
    const collection_dir = this.get_data_path(this.get_selector_data_file('')).match(/(.*)[\/\\]/)[1]||'';

    const mci_version = document.getElementById('modal-codec-info-version');
    mci_version.href = collection_dir + '/codec_version.txt';

  }

  // find the file with data required to make ceratin points plot
  get_selector_data_file(suffix) {

    const cur_codec_data = global_json[this.codec_name];
    for (const p of cur_codec_data.points) {
      if (p.quality == this.quality_value) {
        return p["encoded path"] + "." + suffix;
      }
    }

  }

  get_data_path(data_file) {

    const urlParams = new URLSearchParams(window.location.search);
    const clipname = urlParams.get('clipname');

    return `/data/${clipname}/${data_file}`

  }

  async large_plot_warn() {

    const warn_elem = document.createElement('span');
    warn_elem.innerHTML = '<h2>Warning!</h2>Selected graph has more than 2000 data points. It might freeze your browser.<br><br>'

    const accept_elem = document.createElement('a');
    accept_elem.href = '#'; // Set the link's href attribute to '#' or your desired URL
    accept_elem.textContent = 'draw it nevertheless'; // Set the link text

    const plot_render_large = this.plot_render.bind(this, true);
    accept_elem.addEventListener('click', plot_render_large);

    const modal_container = document.getElementById('modal-container');

    // Append the link element to the div
    modal_container.appendChild(warn_elem);
    modal_container.appendChild(accept_elem);
  }

  async plot_render(large_plot_ok=false) {

    //console.log("render plot: " + large_plot_ok);

    const po = plot_selectors_modal[this.mgs.value];

    const selector_data_file = this.get_selector_data_file(po.suffix);

    const response = await fetch(this.get_data_path(selector_data_file));
    const cur_json = await response.json();

    if (cur_json[po.iter].length > 2000 && !large_plot_ok) {
      this.large_plot_warn();
      return;
    }

    var line = {name: this.mgs.value, data: []};
    for (const cur_point of cur_json[po.iter]) {

      const cur_x = cur_point[po.selx];
      const cur_y = (po.sel2 !== undefined) ? cur_point[po.sel1][po.sel2] : cur_point[po.sel1];

      line.data.push({
        name: '',
        x: cur_x,
        y: cur_y
      });
      line.data.sort(cur_item_sorter);

    }

    this.main_chart = make_plot(
      [line,], 'modal-container', '',
      str_add_unit(po.shortx, po.unitx),
      str_add_unit(po.shortx, po.unitx),

      str_add_unit(this.mgs.value, po.unit),
      str_add_unit(po.short, po.unit)
    );

  }

  create_selectors() {

    // clear previous options
    this.mgs.innerHTML = "";

    for (const sel_name of Object.keys(plot_selectors_modal)) {
      const option = document.createElement('option');
      option.text = sel_name;
      option.value = sel_name;

      this.mgs.add(option);
    }

  }

  show() {
    this.modal_overlay.style.display = 'block';
  }

  hide() {
    console.log("hide");
    if (this.main_chart !== undefined) {
      this.main_chart.destroy();
    }
    this.modal_close_btn.removeEventListener("click", this.on_hide_cb);
    this.modal_overlay.style.display = 'none';
  }

}
