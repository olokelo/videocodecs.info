import React, { Component } from 'react';
import { MdFileDownload, MdOpenInBrowser } from "react-icons/md";
import cx from 'classnames';
import './index.css';

class VCISourcePicker extends Component {

    constructor(props) {
        super(props);
        this.metafile = null;
        this.input_metadata = null;
        this.defaultUrl = null;
        this.sourceChangeCb = this.props.sourceChangeCb;
        this.state = {
            selectedCodec: null,
            selectedQuality: null,
            sourceUrl: "",
            sourceInfo: "",
        };
    }

    shouldComponentUpdate(nextProps, nextState) {
        return !(this.state === nextState);  
    }

    basename(fpath) {
        if (fpath === undefined) { return; }
        return fpath.split('/').reverse()[0];
    }

    // clears clip fields
    // useful for playing local file
    clearVCI() {
        this.setState({sourceInfo: "External File", sourceUrl: "#"});
    }

    fetchLocalFileSourceInfo(fname, silent=true) {
        fname = this.basename(fname);
        console.log("Got local fname: " + fname);

        for (const [profileName, profileData] of Object.entries(this.metafile)) {
            for (const p of profileData.points) {
                if ([p["lossless proxy path"], p["encoded path"]].map(x => this.basename(x)).includes(fname)) {
                    this.printSourceInfo(p, true);
                    this.selectCodec(profileName, silent);
                    this.selectQuality(p.quality, profileName, silent);
                    return true;  // clip found and state altered
                };
            }
        }

        // tried to load a local file which can't be matched to any remote clip
        this.clearVCI();

        return false;  // url provided by the user was not found in metafile
    }

    onFileSelected(evt) {
        if (evt.target.files && evt.target.files[0]) {
            const file = evt.target.files[0];
            this.props.sourceChangeCb({
                type: 'file',
                name: file.name,
                url: window.URL.createObjectURL(file),
            });
            this.setState({sourceUrl: "#"});
            this.fetchLocalFileSourceInfo(file.name);
        }
    }

    onMetafileLoaded(metafile, input_metadata) {

        this.metafile = metafile;
        this.input_metadata = input_metadata;

        // load default video path specified in url
        console.log(this.defaultUrl);
        if (this.defaultUrl !== null && this.defaultUrl !== "") {
            const fileMatched = this.fetchLocalFileSourceInfo(this.defaultUrl, false);
            if (fileMatched) {
                return;
            }
        }

        const codecNames = Object.keys(this.metafile);
        codecNames.sort();
        const selectedCodec = codecNames[0];

        //this.setState({selectedCodec});
        this.selectCodec(selectedCodec);

    }
    
    removeUndefined(arr, attr) {
        console.log(arr);
        return arr.filter(function(e) {
            return e[attr] !== undefined;
        });
    }

    getQualityValues(codecName) {
        return this.removeUndefined(this.metafile[codecName].points, "quality").map(p => {return Number(p.quality);});
    }

    selectCodec(codecName, silent=false) {

        this.setState({selectedCodec: codecName});

        // select lowest possible quality by default
        // bandwidth should be thankful :)
        // higher the quality, the lower it really is so using Math.max here
        console.log(this.getQualityValues(codecName));
        const minQuality = Math.max(...this.getQualityValues(codecName));
        console.log("min q: " + minQuality);
        this.selectQuality(minQuality, codecName, silent);

    }

    printSourceInfo(p, is_local=false) {
        console.log("IsLocal: " + is_local);
        var sourceInfo = `VMAF: ${p.vmaf.mean} @ ${p.probe["bitrate (kbps)"]}kbps\nEncode time: ${p.encode["time (s)"]}s @ ${p.encode["cpu mean (%)"]}% cpu`;
        if (p["lossless proxy path"] !== undefined) {
            sourceInfo += '\nproxy clip'
        }
        if (is_local) {
            sourceInfo += '\nlocal file'
        }
        this.setState({sourceInfo});
    }

    selectQuality(qualityValue, codecName, silent=false) {

        console.log(`selectQuality called with qv = ${qualityValue} , cn = ${codecName}`);

        this.setState({selectedQuality: qualityValue});

        // selectedCodec will be set to codecName if defined, otherwise state 
        const selectedCodec = codecName !== undefined ? codecName : this.state.selectedCodec;
        console.log("codec selected: " + selectedCodec);

        var p = undefined;
        for (p of this.metafile[selectedCodec].points) {
            // double equal is actually intentional, you could pass qualityValue as int or string
            if (p.quality == qualityValue) {
                break;
            }
        }

        const fpath = p["lossless proxy path"] || p["encoded path"];
        const sourceUrl = `/data/${this.input_metadata.clipname}/` + fpath;
        console.log(sourceUrl);

        if (!silent) { 
            this.printSourceInfo(p);
            this.setState({sourceUrl});
            this.sourceChangeCb({name: this.basename(fpath), url: sourceUrl, variant: 0});
        }

    }

    render() {

        if (this.metafile === null || this.state.selectedCodec === null) {
            return "";
        }

        var codecNames = Object.keys(this.metafile);
        codecNames.sort();
        const codec_options = codecNames.map(x => {
            return (
            <option key={x} value={x}>
                {x}
            </option>);
        });

        var qualityValues = this.getQualityValues(this.state.selectedCodec);
        qualityValues.sort();
        console.log("Quality Values: " + qualityValues);

        const quality_options = qualityValues.map(x => {
            return (
                <option key={x} value={x}>
                    {x}
                </option>
            );
        });

        console.log("Rendering VCI");
        return (
            <div className={cx("vci-source-picker", this.props.className, { 'hidden': false })}>

                <label className="source-file-input">
                    <MdOpenInBrowser size={28} style={{ cursor: 'pointer' }}/>
                    <input type="file" onChange={(evt) => this.onFileSelected(evt)} />
                </label>
                <div className="spacer"></div>

                <select onChange={(e) => {this.selectCodec(e.target.value);}} value={this.state.selectedCodec} name="codec-chooser" id="codec-chooser">
                    {codec_options}
                </select>

                <select onChange={(e) => {this.selectQuality(e.target.value);}} value={this.state.selectedQuality} name="quality-chooser" id="quality-chooser">
                    {quality_options}
                </select>

                <div className="spacer"></div>
                <a href={this.state.sourceUrl} download={(this.state.sourceUrl !== "#") ? '' : undefined}>
                    <MdFileDownload size={28} style={{ cursor: 'pointer' }}/>
                </a>

                <br></br>
                <p className="source-info">{this.state.sourceInfo}</p>

            </div>
        )
    }
}

export default VCISourcePicker;
