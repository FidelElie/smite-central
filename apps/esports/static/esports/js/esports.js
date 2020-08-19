// ! Cached Selectors And Variables
hero_background = document.getElementsByClassName("hero-background")[0];
slide_timer = document.getElementsByClassName("slide-timer")[0];

block = document.getElementsByClassName("block")[0];
error_overflow = document.getElementsByClassName("error-overflow")[0];

scroll_to_content = document.getElementById("down-scroll");

esports_search = document.getElementById("esports-search");

images = document.getElementsByClassName("slideshow-image");
image_index = 0;

mobile_query = window.matchMedia("(max-width: 600px)");
hover_query = window.matchMedia("(hover: hover)");

transform_functions = {
  match: () => {},
  nomatch: () => {}
}

hover_functions = {
  match: () => {
  },
  nomatch: () => {}
}
image_transition_seconds = 2;
timing_multiplier = 2.5;

setBaseTime();
time_interval = setInterval(slideShowTimer, 1000);

// ! Setup
Array.from(images).forEach(image => {
  image.style.transition = `${image_transition_seconds}s`
})

try {
  setIndex(0);
} catch (TypeError) {
  hero_background.style.display = "none";
  block.style.display = "none";
  error_overflow.style.height = "200px";
}

setToggle(esports_search);

// ! Event Handlers
scroll_to_content.addEventListener("click", function() {scrollToY(error_overflow.offsetTop);});

hover_query.addListener(function() {parseMedia(this, hover_functions)});

// ! Runtime Functions
parseMedia(mobile_query, transform_functions);
parseMedia(hover_query, hover_functions);

// ! General Functions
function moveIndex(direction) {
  if (direction) {
    new_index = image_index + 1 <= images.length - 1 ? image_index + 1 : 0;
  } else {
    new_index = image_index - 1 >= 0 ? image_index - 1 : images.length - 1;
  }
  setIndex(new_index);
}

function setIndex(index) {
  images[image_index].classList.remove("active");
  image_index = index;
  images[image_index].classList.add("active");
}

function setBaseTime() {
  time = image_transition_seconds * timing_multiplier
  slide_timer.innerText = `${time}`
}

function slideShowTimer() {
  time -= 1
  slide_timer.innerText = `${time}`
  if (time <= 0) {
    clearInterval(time_interval);
    moveIndex(true);
    setBaseTime();
    time_interval = setInterval(slideShowTimer, 1000);
  }
}

