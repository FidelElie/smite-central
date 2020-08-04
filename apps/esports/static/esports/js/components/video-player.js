player_contents = document.getElementsByClassName("player-contents")[0];

video_progress_container = document.getElementsByClassName("player-progress")[0];
video_progress_bar = document.getElementsByClassName("progress-bar")[0];
video_progress_indicator = document.getElementsByClassName("progress-indicator")[0];
video_progress_tooltip = document.getElementsByClassName("progress-tooltip")[0];

video_play = document.getElementById("player-play-pause");
video_mute = document.getElementById("player-mute");
video_volume_slider = document.getElementById("player-volume-input");
video_backwards = document.getElementById("player-back");
video_forwards = document.getElementById("player-forward");
video_start = document.getElementById("player-to-start");

video_progress_button = document.getElementById("player-progress-show");

video_skip_button = document.getElementById("player-skip");
video_skip_slider = document.getElementById("player-skip-amount");

video_speed_button = document.getElementById("player-speed");
video_speed_slider = document.getElementById("player-speed-input");

video_fullscreen = document.getElementById("player-fullscreen");

video_back = document.getElementsByClassName("back-button")[0];

ranges = document.querySelectorAll(".control-range");

states = {
  unstarted: -1,
  ended: 0,
  playing: 1,
  paused: 2,
  buffering: 3,
  video_cued: 5
}

slider_data = [
  {
    element: video_volume_slider,
    func: changeVolume,
    filters: null,
    text: null
  },
  {
    element: video_skip_slider,
    func: null,
    filters: [1, 5, 30, 60, 300],
    text: ["1 Second", "5 Seconds", "30 Seconds", "1 Minute", "5 Minutes"]
  },
  {
    element: video_speed_slider,
    func: changePlaybackSpeed,
    filters: [0.25, 0.5, 1, 1.5, 2],
    text: ["Slowest", "Slower", "Normal", "Faster", "Fastest"]
  }
];

unmuted_volume_value = 100;

// ! Video Player Setup
tag = document.createElement('script');
player;
tag.src = "https://www.youtube.com/iframe_api";
firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

function onYouTubeIframeAPIReady() {
  // ID Provided in preceding HTML tag script
  player = new YT.Player('player', {
    videoId: chosen_video_id,
    playerVars: {
      controls: 0,
      modestbranding: 0,
      enablejsapi: 1,
      rel: 1,
      origin: "http://127.0.0.1:8000",
      disablekb: 1,
      playinline: 1,

    },
    events: {
      'onStateChange': onPlayerStateChange
    }
  });
}

function onPlayerStateChange() {
  video_is_cued = player.getPlayerState() == states.video_cued;
  video_is_paused = player.getPlayerState() == states.paused;
  video_is_playing = player.getPlayerState() == states.playing;
  if (video_is_cued || video_is_paused) {
    addIcon(video_play, "mdi-play");
    changeTooltip(video_play, "Play");
    clearInterval(video_timings);
  } else if (video_is_playing) {
    setVideoTime();
    addIcon(video_play, "mdi-pause");
    changeTooltip(video_play, "Pause");
    video_timings = setInterval(setVideoTime, 1000 * player.getPlaybackRate());
  }
  player_contents.focus();
}

// ! Event Handlers
video_play.addEventListener("click", togglePlayback);
video_mute.addEventListener("click", toggleMute);
video_backwards.addEventListener("click", () => { movePlayback(false); });
video_forwards.addEventListener("click", () => { movePlayback(true); });
video_start.addEventListener("click", () => { player.seekTo(0, true) });
video_progress_button.addEventListener("click", toggleProgressBar)
video_skip_button.addEventListener("click", () => {
  toggleContents(video_skip_slider, video_speed_slider);
});
video_speed_button.addEventListener("click", () => {
  toggleContents(video_speed_slider, video_skip_slider);
});
video_fullscreen.addEventListener("click", toggleFullscreen);

ranges.forEach(range => {
  let input = range.querySelector(".sliders");
  let output = range.querySelector(".value-indicator");
  let input_data = slider_data.filter(x => x.element === input)[0];
  let values = input_data.text != null ? input_data.text : null;
  input.addEventListener("input", () => {
    setTooltip(input, output, values);
    if (input_data.func != null) { input_data.func(); }
  });
  setTooltip(input, output, values);

  input.addEventListener("mousedown", () => { output.classList.add("visible"); })
  input.addEventListener("touchstart", () => { output.classList.add("visible"); })

  input.addEventListener("mouseup", () => {
    setTimeout(() => { output.classList.remove("visible") }, 250)})
  input.addEventListener("touchend", () => {
    setTimeout(() => { output.classList.remove("visible") }, 250)})
})

video_progress_container.addEventListener("click", function (event) {
  let new_time = getProgress(event.pageX)
  player.seekTo(new_time, true);
  setVideoTime(new_time);
})

// ! Video Element Functions
function getProgress(event_local) {
  let local = event_local - $(video_progress_container).offset().left;
  let percentage_width = getPercentageWidth(local);
  if (percentage_width < 0) { percentage_width = 0; }
  if (percentage_width > 1) { percentage_width = 1; }

  let current_time = percentage_width * player.getDuration();
  video_progress_tooltip.innerText = secondsToTimeString(current_time);
  video_progress_indicator.style.width = `${percentage_width * 100}%`;

  return current_time
}

function showProgressIndicators() {
  video_progress_tooltip.classList.add("visible");
  video_progress_indicator.classList.add("visible");
}

function hideProgressIndicators() {
  video_progress_tooltip.classList.remove("visible");
  video_progress_indicator.classList.remove("visible");
}

// ! Video Player Control Functions

function togglePlayback() {
  let video_is_cued = player.getPlayerState() == states.video_cued;
  let video_is_paused = player.getPlayerState() == states.paused;
  let video_is_playing = player.getPlayerState() == states.playing;
  if (video_is_cued || video_is_paused) {
    player.playVideo();
  } else if (video_is_playing) {
    player.pauseVideo();
  }
}

function toggleMute() {
  if (!player.isMuted()) {
    unmuted_volume_value = video_volume_slider.value != 0 ? video_volume_slider.value : 100;
    video_volume_slider.value = 0;
  } else {
    video_volume_slider.value = unmuted_volume_value;
  }
  changeVolume()
}

function changeVolume() {
  player.setVolume(video_volume_slider.value);
  if (video_volume_slider.value > 0 && video_volume_slider.value < 50) {
    addIcon(video_mute, "mdi-volume-medium");
    changeTooltip(video_mute, "Mute");
    player.unMute();
  } else if (video_volume_slider.value >= 50) {
    addIcon(video_mute, "mdi-volume-high");
    changeTooltip(video_mute, "Mute");
    player.unMute();
  } else {
    addIcon(video_mute, "mdi-volume-off");
    changeTooltip(video_mute, "Unmute");
    player.mute();
  }
}

function movePlayback(direction) {
  let current_time = player.getCurrentTime();
  let skip_data = slider_data.filter(x => x.element === video_skip_slider)[0];
  let skip_value = skip_data.filters[video_skip_slider.value];
  if (direction) {
    current_time += skip_value;
  } else {
    current_time -= skip_value;
  }
  player.seekTo(current_time, true);
}

function toggleProgressBar() {
  if (!video_progress_container.classList.contains("shown")) {
    video_progress_container.classList.add("shown");
  } else {
    video_progress_container.classList.remove("shown");
  }
}

function changePlaybackSpeed() {
  let speed_data = slider_data.filter(x => x.element === video_speed_slider)[0];
  player.setPlaybackRate(speed_data.filters[video_speed_slider.value]);
  filters_midpoint = Math.floor(speed_data.filters.length / 2);

  if (video_speed_slider.value < filters_midpoint) {
    addIcon(video_speed_button, "mdi-speedometer-slow");
  } else if (video_speed_slider.value > filters_midpoint) {
    addIcon(video_speed_button, "mdi-speedometer");
  } else {
    addIcon(video_speed_button, "mdi-speedometer-medium");
  }
}

function toggleFullscreen() {
  if (!player_contents.classList.contains("fullscreen")) {
    addIcon(video_fullscreen, "mdi-fullscreen-exit");
    player_contents.classList.add("fullscreen");
  } else {
    addIcon(video_fullscreen, "mdi-fullscreen");
    player_contents.classList.remove("fullscreen");
  }
}

function setVideoTime(specified_time = null) {
  if (specified_time != null) {
    duration_percentage = getPercentageTime(specified_time);
  } else {
    duration_percentage = getPercentageTime(player.getCurrentTime());
  }
  video_progress_bar.style.width = `${duration_percentage * 100}%`;
}

// ! Specific Functions

function getPercentageTime(specified_time) {
  return specified_time / player.getDuration();
}

function getPercentageWidth(specified_width) {
  return specified_width / $(player_contents).width();
}

function setTooltip(range, bubble, values = null) {
  let val = values != null ? values[range.value] : range.value;
  let min = range.min ? range.min : 0;
  let max = range.max ? range.max : 100;
  let newVal = Number(((range.value - min) * 100) / (max - min));
  bubble.innerHTML = val;
  bubble.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`;
}

function changeTooltip(element, text) {
  tooltip = element.children[0];
  tooltip.innerText = text
}
