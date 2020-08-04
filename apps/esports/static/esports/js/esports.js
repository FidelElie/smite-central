// ! Cached Selectors And Variables
banner_video = document.getElementById("video");

video_player_buttons = document.getElementsByClassName("video-buttons")[0].children;
mute_highlight = video_player_buttons[0];
previous_highlight = video_player_buttons[1];
next_highlight = video_player_buttons[2];
pause_highlight = video_player_buttons[3];
to_video = video_player_buttons[4];

indicator_titles = document.getElementsByClassName("video-titles");

scroll_to_content = document.getElementById("down-scroll");
content = document.getElementsByClassName("content")[0];

esports_search = document.getElementById("esports-search");

videos = document.getElementsByClassName("video");
videos_loaded = Array(videos.length).fill(false);
video_index = 0;

mobile_query = window.matchMedia("(max-width: 600px)");
hover_query = window.matchMedia("(hover: hover)");

transform_functions = {
  match: () => {},
  nomatch: () => {}
}

hover_functions = {
  match: () => {
    Array.from(video_player_buttons).forEach(button => {
      let tooltip = button.children[0];
      button.addEventListener("mouseenter", () => {
        tooltip.classList.add("tooltip-visible")
      });
      button.addEventListener("mouseleave", () => {
        tooltip.classList.remove("tooltip-visible")
      });
    })
  },
  nomatch: () => {}
}

// ! Setup

indicator_titles[video_index].classList.add("visible")

setToggle(esports_search);

// ! Event Handlers

mute_highlight.addEventListener("click", toggleMute);
previous_highlight.addEventListener("click", () => {moveIndex(false);});
next_highlight.addEventListener("click", () => {moveIndex(true);});
pause_highlight.addEventListener("click", togglePause);
to_video.addEventListener("click", navigateToVideo);

Array.from(videos).forEach(video => {
  video.addEventListener("ended", () => {next_highlight.click()})
})

scroll_to_content.addEventListener("click", function() {scrollToY(content.offsetTop);});

hover_query.addListener(function() {parseMedia(this, hover_functions)});

// ! Runtime Functions
parseMedia(mobile_query, transform_functions);
parseMedia(hover_query, hover_functions);

toggle_video_mutes(true);
startHighlight();

// ! General Functions
function moveIndex(direction) {
  if (direction) {
    new_index = video_index + 1 <= videos.length - 1 ? video_index + 1 : 0;
  } else {
    new_index = video_index - 1 >= 0 ? video_index - 1 : videos.length - 1;
  }
  setIndex(new_index);
}

function setIndex(index) {
  indicator_titles[video_index].classList.remove("visible")
  stopHighlight();
  video_index = index;
  indicator_titles[video_index].classList.add("visible")
  startHighlight();
}

function stopHighlight() {
  videos[video_index].classList.remove("active");
  videos[video_index].pause();
}

function startHighlight() {
  videos[video_index].classList.add("active");
  if (!videos_loaded[video_index]) {
    videos_loaded[video_index] = true;
    videos[video_index].load();
  }
  videos[video_index].currentTime = 0;
  videos
  if (pause_highlight.classList.contains("mdi-pause")) {
    videos[video_index].play();
  }
}

function toggle_video_mutes(toggle_boolean) {
  Array.from(videos).forEach(video => {
    video.muted = toggle_boolean;
  });
}

function togglePause() {
  let tooltip = pause_highlight.children[0];
  if (pause_highlight.classList.contains("mdi-pause")) {
    addIcon(pause_highlight, "mdi-play");
    tooltip.innerText = "Play Highlight";
    videos[video_index].pause();
  } else {
    addIcon(pause_highlight, "mdi-pause");
    tooltip.innerText = "Pause Highlight";
    videos[video_index].play();
  }
}

function toggleMute() {
  let tooltip = mute_highlight.children[0];
  if (mute_highlight.classList.contains("mdi-volume-mute")) {
    addIcon(mute_highlight, "mdi-volume-high");
    tooltip.innerText = "Unmute Highlight";
    toggle_video_mutes(false);
  } else {
    addIcon(mute_highlight, "mdi-volume-mute");
    tooltip.innerText = "Mute Highlight";
    toggle_video_mutes(true);
  }
}

function navigateToVideo() {
  let current_highlight = videos[video_index];
  let corresponding_video_id = current_highlight.getAttribute("data-id");
  window.location = `video/${corresponding_video_id}`;
}
