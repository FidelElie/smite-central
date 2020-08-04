video_container = document.getElementsByClassName("video-player")[0];

home_button = document.getElementById("home-button");

keyboard_button = document.getElementById("keyboard-button");
keyboard_contents = document.getElementsByClassName("keyboard-contents")[0];

previous_match = document.getElementsByClassName("previous-match")[0];
next_match = document.getElementsByClassName("next-match")[0];

match_nav_toggle = document.getElementById("player-display-match-nav");

mobile_query = window.matchMedia("(max-width: 600px)");
hover_query = window.matchMedia("(hover: hover)");

transform_functions  = {
  match: () => {
    keyboard_contents.style.maxHeight = "0px";
    video_container.style.bottom = "";
  },
  nomatch: () => {}
}

hover_functions  = {
  match: () => {
    video_progress_container.addEventListener("mouseover", function(event) {
      getProgress(event.pageX);
      showProgressIndicators();
    });

    video_progress_container.addEventListener("mousemove", function (event) {
      getProgress(event.pageX);
      showProgressIndicators();
    });

    video_progress_container.addEventListener("mouseleave", hideProgressIndicators);
  },
  nomatch: () => {
    video_progress_container.addEventListener("touchstart", function (event) {
      event.preventDefault();
      showProgressIndicators();
    });

    video_progress_container.addEventListener("touchmove", function(event) {
      event.preventDefault();
      getProgress(event.changedTouches[0].pageX);
    })

    video_progress_container.addEventListener("touchend", function(event) {
      event.preventDefault();
      let new_time = getProgress(event.changedTouches[0].pageX);
      player.seekTo(new_time, true);
      setVideoTime(new_time);
      hideProgressIndicators();
    });
  }
}

registered_keys = {}

key_data = [
  {
    codes: "KeyM",
    func: toggleMute,
  },
  {
    codes: "Space",
    func: togglePlayback,
  },
  {
    codes: "KeyF",
    func: toggleFullscreen
  },
  {
    codes: "ArrowLeft",
    func: () => {movePlayback(false)}
  },
  {
    codes: "ArrowRight",
    func: () => {movePlayback(true)}
  },
  {
    codes: "KeyP",
    func: toggleProgressBar
  },
  {
    codes: "KeyA + ArrowLeft",
    func: () => {changeSliderValue(slider_data[1], false)}
  },
  {
    codes: "KeyA + ArrowRight",
    func: () => {changeSliderValue(slider_data[1], true)}
  },
  {
    codes: "KeyS + ArrowLeft",
    func: () => {changeSliderValue(slider_data[2], false)}
  },
  {
    codes: "KeyS + ArrowRight",
    func: () => {changeSliderValue(slider_data[2], true)}
  }
]


// ! Event Handlers
video_back.addEventListener("click", function() {
  if (document.referrer != "") {
    window.history.back()
  } else {
    home_button.click();
  }
});

home_button.addEventListener("click", function() {
  split_href = window.location.href.split("/");
  if (split_href.length == 6) {
    window.location.href = "../";
  } else {
    window.location.href = "../../"
  }
});

if (previous_match != undefined) {
  previous_match.addEventListener("click", function() {changeMatchPart(false);})
}

if (next_match != undefined) {
  next_match.addEventListener("click", function() {changeMatchPart(true);})
}

if (match_nav_toggle != undefined) {
  match_nav_toggle.addEventListener("click", function() {
    if (previous_match != undefined) {
      if (previous_match.classList.contains("not-visible")) {
        previous_match.classList.remove("not-visible");
      } else {
        previous_match.classList.add("not-visible");
      }
    }
    if (next_match != undefined) {
      if (next_match.classList.contains("not-visible")) {
        next_match.classList.remove("not-visible");
      } else {
        next_match.classList.add("not-visible");
      }
    }
  })
}

keyboard_button.addEventListener("click", function() {
  if (keyboard_contents.style.maxHeight == "0px") {
    keyboard_contents.style.maxHeight = `${keyboard_contents.scrollHeight}px`;
    video_container.style.bottom = `${keyboard_contents.scrollHeight}px`;
  } else {
    keyboard_contents.style.maxHeight = "0px";
    video_container.style.bottom = "";
  }
})

document.addEventListener("keydown", function(event) {
  registered_keys[event.code] = true;
  current_keys = getPressedKeys();
  let key_combo = key_data.filter(x => checkKeys(current_keys, getKeyCodes(x.codes)))[0];
  if (key_combo != undefined) {
    if ("func" in key_combo) {
      key_combo.func();
    } else {
      console.log("No Function To Call");
    }
  }
})

document.addEventListener("keyup", function(event) {
  registered_keys[event.code] = false;
})

hover_query.addListener(function() {parseMedia(this, hover_functions)});
mobile_query.addListener(function() {parseMedia(this, transform_functions)});

// ! Setup
parseMedia(hover_query, hover_functions);
parseMedia(mobile_query, transform_functions);
registerKeys();
keyboard_contents.style.maxHeight = "0px";

// ! Extended Video Player Functions

// TODO  make show transition better
function changeSliderValue(slider_data, direction) {
  if (direction) {
    slider_data.element.stepUp();
  } else {
    slider_data.element.stepDown();
  }

  let text_value = slider_data.text[slider_data.element.value];
  let slider_id = slider_data.element.getAttribute("id");
  let button_element = document.getElementById(`${slider_id}-prompt`);
  button_element.innerText = text_value;
  button_element.classList.add("visible");

  if (slider_data.func != null) { slider_data.func(); }

  setTimeout(() => {button_element.classList.remove("visible")}, 1000);
}

// ! General Functions

function changeMatchPart(direction) {
  let split_href = window.location.href.split("/");
  let match_index = parseInt(split_href[split_href.length - 1], 10)

  let new_index = direction ? match_index + 1 : match_index - 1;

  window.location.href = `./${new_index}`;
}

function registerKeys() {
  key_data.forEach(key => {
    for (i in key.codes) {
      key_codes = getKeyCodes(key.codes);
      for (j in key_codes) {
        registered_keys[key_codes[j]] = false;
      }
    }
  });
}

function getKeyCodes(key_string) {
  if (key_string.includes("+")) {
    codes = key_string.split("+").map(x => x.trim());
  } else {
    codes = [key_string];
  }
  return codes
}

function getPressedKeys() {
  let key_entries = Object.entries(registered_keys);
  let pressed_keys = key_entries.filter(x => x[1])
  return pressed_keys.map(x => x[0])
}

function checkKeys (current_keys, registered_data) {
  if (current_keys.length == registered_data.length) {
    let mapper = current_keys.map(x => registered_data.includes(x));
    if (mapper.includes(false)) { return false }
    return true
  }
  return false
}
