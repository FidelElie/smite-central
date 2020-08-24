central_options = document.getElementsByClassName("central-options")[0];
option_cards = document.getElementsByClassName("option-card");
left_nav = document.getElementById("left-nav");
right_nav = document.getElementById("right-nav");

footer = document.getElementsByClassName("footer")[0];
footer_button = document.getElementsByClassName("swipe-footer")[0];
footer_contents = document.getElementsByClassName("swipe-contents")[0];

mobile_query = window.matchMedia("(max-width: 600px)");
hover_query = window.matchMedia("(hover: hover)");

mobile_swipe_index = 1;
touch_start_x = 0;
touch_start_y = 0;
touch_end_x = 0;
touch_end_y = 0;

swipeable_elements = [
  {
    element: central_options, handler: () => {
      left(manipulateSlider, false);
      right(manipulateSlider, true);
    }
  },
  {
    element: footer_button, handler: () => {
      up(manipulateFooter, true);
      down(manipulateFooter, false);
    }
  }
]

transform_functions = {
  match: () => {
    central_options.style.transform = "translateX(0px)";
    setTimeout(() => { openOptionDesc(option_cards[1]) }, 250);
  },
  nomatch: () => {
    central_options.style.transform = "none";
    mobile_swipe_index = 1;
    Array.from(option_cards).forEach(card => {
      closeOptionDesc(card)
    })
  }
}

hover_functions = {
  match: () => {
    Array.from(option_cards).forEach(card => {
      let desc = card.querySelector(".option-description");
      card.addEventListener("mouseenter", () => { desc.style.maxHeight = `${desc.scrollHeight}px`; });
      card.addEventListener("mouseleave", () => { desc.style.maxHeight = null; });
    })
    footer.addEventListener("mouseenter", () => {
      footer_contents.style.maxHeight = `${footer_contents.scrollHeight}px`;
      footer_button.classList.add("mdi-flip-v");
    })
    footer.addEventListener("mouseleave", () => {
      footer_contents.style.maxHeight = "0px";
      footer_button.classList.remove("mdi-flip-v");
    })
  },
  nomatch: () => { return }
}

navigation_information = ["/toxic", "/esports", "/builder"]


// ! Touch Functions
right = (func, modifier) => {
  touch_end_x > touch_start_x ? func(modifier) : null;
}

left = (func, modifier) => {
  touch_end_x < touch_start_x ? func(modifier) : null;
}

up = (func, modifier) => {
  touch_end_y > touch_start_y ? func(modifier) : null;
}

down = (func, modifier) => {
  touch_end_y < touch_start_y ? func(modifier) : null;
}

// ! Setup

Array.from(option_cards).forEach(card => {
  card.style.marginLeft = "30px";
  card.style.marginRight = "30px";
})

// ! Event Handlers
Array.from(option_cards).forEach(card => {
  card.addEventListener("click", function() {navigateOptions(this);});
})

footer_button.addEventListener("click", () => { manipulateFooter() })
mobile_query.addListener(function () { parseMedia(this, transform_functions) });
hover_query.addListener(function () { parseMedia(this, hover_functions) });

swipeable_elements.forEach(data => {
  data.element.addEventListener("touchstart", function (event) {
    touch_start_x = event.changedTouches[0].screenX;
    touch_start_y = event.changedTouches[0].screenY;
  })
  data.element.addEventListener("touchend", function (event) {
    touch_end_x = event.changedTouches[0].screenX;
    touch_end_y = event.changedTouches[0].screenY;
    data.handler()
  })
})

left_nav.addEventListener("click", function() {manipulateSlider(true);});
right_nav.addEventListener("click", function() {manipulateSlider(false);});


// ! Runtime Calls
footer_contents.style.maxHeight = "0px";
parseMedia(mobile_query, transform_functions);
parseMedia(hover_query, hover_functions);

// ! Navigation Functions
function navigateOptions(element) {
  let index = Array.from(option_cards).indexOf(element);
  window.location = navigation_information[index]
}

// ! Manipulation Functions
function manipulateSlider(direction) {
  let current_transform = extractStyleValue(central_options, "transform");
  let margin_value = extractStyleValue(option_cards[0], "marginLeft");
  let width = option_cards[0].offsetWidth + (margin_value * 2)
  let midpoint_value = Math.floor(option_cards.length / 2);
  let current_index = mobile_swipe_index

  if (direction) {
    new_local = current_transform + width;
    current_index -= 1;

  } else {
    new_local = current_transform - width;
    current_index += 1;
  }

  let transform_min = - midpoint_value * width;
  let transform_max = midpoint_value * width;


  if (new_local < transform_min || new_local > transform_max) { return }

  let transform_string = `translateX(${new_local}px)`;
  closeOptionDesc(option_cards[mobile_swipe_index]);
  central_options.style.transform = transform_string;
  openOptionDesc(option_cards[current_index]);

  mobile_swipe_index = current_index;

  if (new_local >= midpoint_value * width) {
    left_nav.style.opacity = "0";
  } else {
    left_nav.style.opacity = "1";
  }

  if (new_local <= - midpoint_value * width) {
    right_nav.style.opacity = "0";
  } else {
    right_nav.style.opacity = "1";
  }
}

function manipulateFooter() {
  if (footer_contents.style.maxHeight == "0px") {
    footer_contents.style.maxHeight = `${footer_contents.scrollHeight}px`;
    footer_button.classList.add("mdi-flip-v");
  } else {
    footer_contents.style.maxHeight = "0px";
    footer_button.classList.remove("mdi-flip-v");
  }
}

function openOptionDesc(card) {
  let desc = card.querySelector(".option-description");
  desc.style.maxHeight = `${desc.scrollHeight}px`;
}

function closeOptionDesc(card) {
  let desc = card.querySelector(".option-description");
  desc.style.maxHeight = null;
}

// ! Utility Functions

function extractTransform(element) {
  let current_transform = element.style.transform;
  if (current_transform != "") {
    let stripped_value = current_transform.replace("translateX(", "").replace(")", "");
    return parseInt(stripped_value.replace("px", ""), 10);
  } else {
    return 0
  }
}
