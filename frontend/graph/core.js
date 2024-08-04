function cur_item_sorter(a, b) {

  if (a.x === null || b.x === null) {
    return 0;
  }

  if (a.x > b.x) {
    return 1;
  } else if (a.x === b.x) {
    return 0;
  } else {
    return -1;
  }
}

function str_add_unit(axis_name, unit) {
  return axis_name + ((unit !== null) ? ` (${unit})` : '');
}

function make_plot(series, container_id, title, x_axis_name, x_axis_short, y_axis_name, y_axis_short) {

  return new Highcharts.Chart({
    chart: {
      type: 'line',
      renderTo: container_id,
      zoomType: 'xy',
      backgroundColor: '#000',
      plotBackgroundColor: '#000',
      style: {
        fontFamily: 'Monospace',
        color: "#fff",
      }
    },
    title: {
      text: title,
      style: {
        color: '#0bd',
        fontFamily: 'Monospace'
      }
    },
    //colors: ["#f66", "#f33", "#f09", "#f60", "#f93", "#f96", "#841", "#a62", "#990", "#bb0", "#dd0", "#ff0", "#fff", "#ddd", "#bbb", "#0af", "#07f", "#04f", "#01f", "#c0f", "#90f", "#70f", "#40f", "#0f0", "#0c0", "#0a0"],
    colors: [
      '#00bbdd', '#ff0044', '#2b9348', '#8a5a83', '#f95d6a', '#1f9e89', '#00a8cc', '#f19c79',
      '#006daa', '#00539c', '#3792cb', '#f7d08a', '#ff7b54', '#16db93', '#044f77', '#ffbe0b',
      '#02c39a', '#583d72', '#ff6363', '#028090', '#0052a5', '#ff4500', '#7ed957', '#ba55d3',
      '#ff5252', '#3c6e71', '#9a1750', '#008000', '#fd0061', '#808000', '#d81e5b', '#228b22',
      '#ff0000', '#ff69b4', '#556b2f', '#ffa500', '#dc143c', '#006400', '#9932cc'
    ],
    legend: {
      itemStyle: {
        fontFamily: 'Monospace',
        color: "#fff",
      },
      itemHoverStyle: {
        color: '#00bcd4'
      },
      itemHiddenStyle: {
        color: '#666'
      }
    },
    tooltip: {
      backgroundColor: '#000',
      borderColor: '#fff',
      borderRadius: 10,
      borderWidth: 3,
      style: {
        fontFamily: 'Monospace',
        color: "#fff",
      },
      formatter() {
        //console.log(this);
        return `<b>${this.series.name}</b><br>${this.point.name}<br>${x_axis_short}: ${this.x}<br>${y_axis_short}: ${this.y}`;
      }
    },
    plotOptions: {
      series: {
        turboThreshold: 0,
        boostThreshold: 1,
        lineWidth: 2,
        states: {
          hover: {
            enabled: true,
            lineWidth: 3
          }
        }
      }
    },
    xAxis: {
      lineColor: '#fff',
      tickColor: '#fff',
      labels: {
        style: {
          color: '#fff',
          fontFamily: 'Monospace'
        }
      },
      title: {
        text: x_axis_name,
        style: {
          color: '#aaa',
          fontFamily: 'Monospace'
        }
      }
    },
    yAxis: {
      lineColor: '#fff',
      tickColor: '#fff',
      labels: {
        style: {
          color: '#fff',
          fontFamily: 'Monospace'
        }
      },
      title: {
        text: y_axis_name,
        style: {
          color: '#aaa',
          fontFamily: 'Monospace'
        }
      },
      /*
      plotLines: [{
        color: '#f04',
        dashStyle: 'Dash',
        width: 2,
        value: 84 // Need to set this probably as a var.
      }]*/
    },
    series: series
  });
}
