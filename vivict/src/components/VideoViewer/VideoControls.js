import React from 'react';
import cx from 'classnames';
import {MdPlayArrow, MdPause, MdNavigateBefore, MdNavigateNext, MdFullscreen} from 'react-icons/md';


const VideoControls = ({onPlay, onStep, onFullscreen, onChangeSpeed, playbackRate, playing, onSeek, position, duration}) => {

    return (<div className="controls">
        <button className="btn btn-default" onClick={(event) => {
            onStep(-1);
            event.stopPropagation();
        }}><MdNavigateBefore /></button>
        <button className={cx('btn', 'btn-default') }
                onClick={(event) => {
                    console.log('play/pause: ' );
                    onPlay();
                    event.stopPropagation();
                }}>{playing ? (<MdPause/>) : (<MdPlayArrow />)}</button>
        <button className="btn btn-default" onClick={(event) => {
            onStep(1);
            event.stopPropagation();
        }}><MdNavigateNext/></button>

        <input type="range" value={position} min="0" max={duration} step="0.04" onInput={(e) => {
            console.log(`range value: ${e.target.value}`);
            const nextPos = parseFloat(e.target.value);
            onSeek(nextPos);
            e.stopPropagation();
        }} />

        <button className="btn btn-default glyphicon glyphicon-fullscreen" onClick={(event) => {
            onFullscreen();
            event.stopPropagation();
        }}><MdFullscreen/></button>


        <button className="btn btn-default" onClick={(event) => {
            onChangeSpeed();
            event.stopPropagation();
        }}>{playbackRate}x</button>
    </div>)
};

export default VideoControls;