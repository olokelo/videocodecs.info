import React, {Component} from 'react';
import {HotKeys} from 'react-hotkeys';
import VideoControls from './VideoControls';
import VideoPlayer from './VideoPlayer';
import './index.css';
import SourceSelector from '../SourceSelector'
import VCISourcePicker from '../VCISourcePicker'
import SplitView from '../SplitView';
import TimeDisplay from './TimeDisplay';
import OffsetIndicator from './OffsetIndicator';
import {Help, HelpButton} from '../Help';
import {COMMANDS, KEY_MAP} from '../../keymap'
import {openFullscreen, isFullscreen, closeFullscreen} from "../../util/FullscreenUtils";
import {copyToClipboard} from "../../util/CopyClipboard";
import {MdPlayArrow, MdCloudDownload} from 'react-icons/md';
import cx from 'classnames';
import {isHlsPlaylist} from "../../util/HlsUtils";
import {isDashOrHls, sourceType} from "../../util/SourceUtils";

const urlParams = new URLSearchParams(window.location.search);
const DEFAULT_SOURCE = "";
const leftVideoUrl = urlParams.get('leftVideoUrl') || DEFAULT_SOURCE;
const rightVideoUrl = urlParams.get('rightVideoUrl') || leftVideoUrl;
const leftVideoVariant = Number(urlParams.get('leftVideoVariant')) || 0;
const rightVideoVariant = Number(urlParams.get('rightVideoVariant')) || 0;
const startPosition = Number(urlParams.get('position')) || 0;
const hideSourceSelector = Boolean(urlParams.get('hideSourceSelector'));
const showHelp = Boolean(urlParams.get('showHelp'));
const clipName = urlParams.get('clipname');

const DEFAULT_SOURCE_LEFT = {
    type: sourceType(leftVideoUrl),
    name: leftVideoUrl,
    url: leftVideoUrl,
    variant: leftVideoVariant,
    position: startPosition
};
const DEFAULT_SOURCE_RIGHT = {
    type:  sourceType(rightVideoUrl),
    name: rightVideoUrl,
    url: rightVideoUrl,
    variant: rightVideoVariant,
    position: startPosition
};

class VideoViewer extends Component {
    constructor(props) {
        super(props);
        this.setVideoViewerRef = videoViewer => {
            this.videoViewer = videoViewer;
        };
        this.setRightVideoRef = rightVideo => {
            this.rightVideo = rightVideo;
        };
        this.setLeftVideoRef = leftVideo => {
            this.leftVideo = leftVideo;
        };
        this.setSplitViewRef = splitView => {
            this.splitView = splitView;
        };

        this.setRightVCISourcePickerRef = VCI_SP => {
            if (DEFAULT_SOURCE_RIGHT.url !== "" && VCI_SP !== null) { VCI_SP.defaultUrl = DEFAULT_SOURCE_RIGHT.url; }
            this.rightVCI_SP = VCI_SP;
        };
        this.setLeftVCISourcePickerRef = VCI_SP => {
            if (DEFAULT_SOURCE_LEFT.url !== "" && VCI_SP !== null) { VCI_SP.defaultUrl = DEFAULT_SOURCE_LEFT.url; }
            this.leftVCI_SP = VCI_SP;
        };

        this.state = {
            playing: false,
            playbackRate: 1.0,
            duration: 0,
            position: 0,
            leftSource: {name: "NONE", url: null, variant: leftVideoVariant},
            rightSource:{name: "NONE", url: null, variant: rightVideoVariant},
            tracking: true,
            splitBorderVisible: true,
            rightVideoOffset: 0,
            showHelp: showHelp,
            showSourceSelector: !hideSourceSelector,
            playReverse: false,
            userDefinedPanZoom: false
        };
        console.dir(this.state);

        this.onFullScreenChange = this.onFullScreenChange.bind(this);
    }

    setPosition(position) {
        this.setState({position});
    }

    setPlaying(playing) {
        this.setState({playing})
    }

    setLeftSource(leftSource) {
        this.setState({leftSource})
    }

    setRightSource(rightSource) {
        this.setState({rightSource})
    }

    toggleTracking() {
        this.setState({tracking: !this.state.tracking})
    }

    changeOffset(delta) {

        if(delta === 0) {
            this.setState({rightVideoOffset: delta});
        } else {
            this.setState({rightVideoOffset: this.state.rightVideoOffset + delta});
        }

        if (!this.state.playing) {
            this.seek(this.leftVideo.currentTime());
        } else {
            this.pause()
                .then(() => this.play())
        }
    }

    playPause() {
        if(this.state.playing) {
            this.pause();
        } else {
            this.play();
        }
    }

    async step(steps) {
        const newTime = this.rightVideo.currentTime() + 0.04 * steps;
        this.rightVideo.quickSeek(newTime);
        this.leftVideo.quickSeek(newTime);
    }

    fullscreen() {
        if(isFullscreen()) {
            closeFullscreen();
        } else {
            openFullscreen(this.videoViewer);
        }
    }

    onTimeUpdate(time) {
        this.setPosition(time);
    }

    onDurationSet(duration) {
        this.setState({duration})
    }

    syncPlayers() {
        this.leftVideo.seek(this.rightVideo.currentTime());
        this.setPosition(this.leftVideo.currentTime());
    }

    async playForward() {
        if (this.state.playing) {
            await this.pause();
        }
        return this.play();
    }

    async play() {

        // both videos should have enough buffer to start playback for at least a while
        if (this.leftVideo.videoElement.readyState < 3 || this.rightVideo.videoElement.readyState < 3) {
            return Promise.resolve();
        }

        if(this.state.playing) {
            return Promise.resolve();
        }

        this.leftVideo.videoElement.playbackRate = this.state.playbackRate;
        this.rightVideo.videoElement.playbackRate = this.state.playbackRate;

        await Promise.all([this.rightVideo.play(), this.leftVideo.play()]);
        this.setPlaying(true);

    }

    async setSpeed() {

        var prate = this.state.playbackRate;
        prate = ((prate - 0.1) % 1).toFixed(1);
        if (prate == 0) {
            prate = 1;
        }
        this.leftVideo.videoElement.playbackRate = prate;
        this.rightVideo.videoElement.playbackRate = prate;
        this.setState({playbackRate: prate});
        console.log(this.state.playbackRate);
    }

    async createShareUrl() {
        if (this.state.leftSource.type === 'file' || this.state.rightSource.type === 'file') {
            alert("Shareable URL cannot be created since you are viewing a local file!");
        } else {
            const leftVariantParam = isDashOrHls(this.state.leftSource.type) ?
                `&leftVideoVariant=${this.state.leftSource.variant}` : "";
            const rightVariantParam = isDashOrHls(this.state.rightSource.type) ?
                `&rightVideoVariant=${this.state.rightSource.variant}` : "";
            const path = `${window.location.host}${window.location.pathname}?position=${this.state.position}`
            + `&leftVideoUrl=${this.state.leftSource.url}${leftVariantParam}`
            + `&rightVideoUrl=${this.state.rightSource.url}${rightVariantParam}`
            + (urlParams.get('hideSourceSelector') ? `&hideSourceSelector=${urlParams.get('hideSourceSelector')}` : "")
            + (urlParams.get('showHelp') ? `&showHelp=${urlParams.get('showHelp')}` : "")
            + (urlParams.get('clipName') ? `&clipname=${urlParams.get('clipname')}` : "")
            console.log("Copying to clipboard: " + path);
            copyToClipboard(path)
        }
    }

    async pause() {
        if (!this.state.playing) {
            return Promise.resolve();
        }
        this.rightVideo.pause();
        this.leftVideo.pause();
        this.setPlaying(false);
        return this.seek(this.leftVideo.currentTime());
    }

    async seek(pos) {
        this.setState({position: pos});
        return Promise.all([this.leftVideo.seek(pos), this.rightVideo.seek(pos + this.state.rightVideoOffset * 0.04)]);
    }

    async onLeftVariantChange(variant) {
        console.log(`left variant changed: ${JSON.stringify(variant)}`);
        await this.changeVariant(this.leftVideo, variant)
    }

    async onRightVariantChange(variant) {
        console.log(`right variant changed: ${JSON.stringify(variant)}`);
        await this.changeVariant(this.rightVideo, variant)
    }

    async onLeftSourceChange(source) {
        await this.changeSource(this.leftVideo, source);

        if (!source.url.includes("blob")) {
            urlParams.set('leftVideoUrl', source.url);
            window.history.replaceState(null, null, "?"+urlParams);
        }

        this.setLeftSource(source);
        this.splitView.focus();
    }

    async onRightSourceChange(source) {
        await this.changeSource(this.rightVideo, source);

        if (!source.url.includes("blob")) {
            urlParams.set('rightVideoUrl', source.url);
            window.history.replaceState(null, null, "?"+urlParams);
        }

        this.setRightSource(source);
        this.splitView.focus();
    }

    async changeVariant(videoElement, variant) {
        this.pauseAndExecute(videoElement, async () => {
            this.setState({leftSource: Object.assign({}, this.state.leftSource, {variant})});
            await videoElement.setVariant(variant);
            //await this.step(0); // Seek to current time to improve dash switching time?
        });
    }

    async changeSource(videoElement, source) {
        console.log(`Change source ${source.url} ${source.variant}`);
        this.pauseAndExecute(videoElement, async () => {
            await videoElement.loadSource(source.url, source.variant);
        });
    }

    async pauseAndExecute(videoElement, action) {
        const wasPlaying = this.state.playing;
        const wasPlayingReverse = this.state.playReverse;
        await this.pause();
        const time = videoElement.currentTime();
        console.log(`${JSON.stringify(videoElement.props)} time: ${time}`);
        await action();
        await this.seek(time);
        if (wasPlaying) {
            await this.play();
        }
        if (wasPlayingReverse) {
            await this.playReverse();
        }
    }

    zoomIn() {
        this.leftVideo.zoomIn();
        this.rightVideo.zoomIn();
        this.setState({userDefinedPanZoom: true});
    }

    zoomOut() {
        this.leftVideo.zoomOut();
        this.rightVideo.zoomOut();
        this.setState({userDefinedPanZoom: true});
    }

    resetPanZoom() {
        this.leftVideo.resetPanZoom();
        this.rightVideo.resetPanZoom();
        this.setState({userDefinedPanZoom: false});
    }

    pan(deltaX, deltaY) {
        this.leftVideo.pan(deltaX, deltaY);
        this.rightVideo.pan(deltaX, deltaY);
        this.setState({userDefinedPanZoom: true});
    }

    shortCutHandlers = [
        [COMMANDS.STEP_FORWARD, () => this.step(25)],
        [COMMANDS.STEP_FORWARD_FRAME, () => this.step(1)],
        [COMMANDS.STEP_BACKWARD_FRAME, () => this.step(-1)],
        [COMMANDS.STEP_BACKWARD, () => this.step(-25)],
        [COMMANDS.PLAY_PAUSE, () => this.playPause()],
        [COMMANDS.FULLSCREEN, () => this.fullscreen()],
        [COMMANDS.TOGGLE_TRACKING, () => this.toggleTracking()],
        [COMMANDS.LEFT_ONLY, () => this.splitView.setSplitPosition(100)],
        [COMMANDS.RIGHT_ONLY, () => this.splitView.setSplitPosition(0)],
        [COMMANDS.TIMESHIFT_INCREASE, () => this.changeOffset(1)],
        [COMMANDS.TIMESHIFT_DECREASE, () => this.changeOffset(-1)],
        [COMMANDS.TIMESHIFT_RESET, () => this.changeOffset(0)],
        [COMMANDS.ZOOM_IN, () => this.zoomIn()],
        [COMMANDS.ZOOM_OUT, () => this.zoomOut()],
        [COMMANDS.PAN_UP, () => this.pan(0, 10)],
        [COMMANDS.PAN_DOWN, () => this.pan(0, -10)],
        [COMMANDS.PAN_RIGHT, () => this.pan(-10, 0)],
        [COMMANDS.PAN_LEFT, () => this.pan(10, 0)],
        [COMMANDS.REST_PAN_ZOOM, () => this.resetPanZoom()],
        [COMMANDS.SHARE, () => this.createShareUrl()],
        [COMMANDS.PLAY, () => this.playForward()],
        [COMMANDS.PAUSE, () => this.pause()],
        [COMMANDS.TOGGLE_HELP, () => this.toggleShowHelp()],
        [COMMANDS.TOGGLE_SPLIT_BORDER_VISIBLE, () => this.toggleSplitBorderVisible()]
    ].reduce((result, [command, action]) => Object.assign(result, {[command.name]: action}), {});

    toggleShowHelp() {
        this.setState({showHelp: !this.state.showHelp});
    }

    toggleSplitBorderVisible() {
        this.setState({splitBorderVisible: !this.state.splitBorderVisible});
    }

    onFullScreenChange() {
        if (!this.state.userDefinedPanZoom) {
            this.resetPanZoom();
        }
    }
    
    async loadMetafile(clipname) {

        //fetch(`/clipdata/${clipname}/${clipname}.meta.json`);
        try {
            const response = await fetch(`/data/${clipname}/metafile.json`);
            const metafile_json = await response.json();

            const input_metadata = metafile_json["input metadata"];
            delete metafile_json["input metadata"];

            this.leftVCI_SP.onMetafileLoaded(metafile_json, input_metadata);
            this.rightVCI_SP.onMetafileLoaded(metafile_json, input_metadata);
            console.log("setting metafile");
        } catch (error) {
            console.error('Got error when loading metafile: ' + error);
        }

    }

    componentDidMount() {

        console.log("selected clip: " + clipName);
        this.loadMetafile(clipName);

        this.splitView.focus();
        this.seek(startPosition)
            .catch(e => console.trace(e));
        this.videoViewer.addEventListener('fullscreenchange', this.onFullScreenChange);
    }

    componentWillUnmount(){
        this.videoViewer.removeEventListener('fullscreenchange', this.onFullScreenChange);
    }

    render() {

        return (
            <div className="video-viewer"
                 tabIndex="0"
                 ref={this.setVideoViewerRef}>

                <TimeDisplay position={this.state.position}/>

                <a className="torrent-dl-icon" href={"/data-torrents/" + clipName + ".torrent"} download>
                    <MdCloudDownload size="36px"/>
                </a>

                <HotKeys className="hotkeys-div" keyMap={KEY_MAP} handlers={this.shortCutHandlers}>
                    <SplitView tracking={this.state.tracking}
                               splitBorderVisible={this.state.splitBorderVisible}
                               onDrag={(dx,dy) => this.pan(dx,dy)}
                               onClick={() => this.playPause()}
                               ref={this.setSplitViewRef}
                               leftSideContent={(
                                <VideoPlayer muted ref={this.setLeftVideoRef}
                                    onInterruptPause={() => this.pause()} />
                               )}>

                        <VideoPlayer ref={this.setRightVideoRef}
                                     onTimeUpdate={(time) => this.onTimeUpdate(time)}
                                     onDurationSet={(duration) => this.onDurationSet(duration)}
                                     onInterruptPause={() => this.pause()} />
                        <div className={cx("big-play-button", {
                            "hidden": this.state.playing || this.state.position !== 0
                        })}
                             onClick={() => this.play()}
                        >
                            <MdPlayArrow size="32px"/>
                        </div>
                    </SplitView>

                    <VideoControls visible={this.state.showSourceSelector}
                                   playing={this.state.playing}
                                   playbackRate={this.state.playbackRate}
                                   onPlay={() => this.playPause()}
                                   onStep={(n) => this.step(n)}
                                   onFullscreen={() => this.fullscreen()}
                                   onChangeSpeed={() => this.setSpeed()}
                                   duration={this.state.duration}
                                   onSeek={(pos) => this.seek(pos)}
                                   position={this.state.position}
                    />

                    <VCISourcePicker ref={this.setLeftVCISourcePickerRef}
                                     sourceChangeCb={(value) => this.onLeftSourceChange(value)}
                                     className="left-vci-source-picker"/>
                    <VCISourcePicker ref={this.setRightVCISourcePickerRef}
                                     sourceChangeCb={(value) => this.onRightSourceChange(value)}
                                     className="right-vci-source-picker"/>

                    <OffsetIndicator offset={this.state.rightVideoOffset}/>

                    <Help visible={this.state.showHelp} onClick={() => this.toggleShowHelp()} />
                    <HelpButton onClick={() => this.toggleShowHelp()} />

                </HotKeys>
            </div>

        );
    }
}

export default VideoViewer;