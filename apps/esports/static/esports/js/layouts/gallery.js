home_button = document.getElementById("home-button");

search_toggle = document.getElementById("search-button");

to_top_button = document.getElementsByClassName("top-button")[0];

match_gallery = document.getElementsByClassName("match-gallery")[0];

prev_page_button = document.getElementById("prev-match-page");
next_page_button = document.getElementById("next-match-page");

top_indicator = document.getElementsByClassName("top-indicator")[0];
page_indicator = document.getElementsByClassName("page-indicator")[0];
page_form = document.getElementsByClassName("page-numb-form")[0];
page_input = document.getElementById("page-number");

// ! Setup

page_input.value = page_input.getAttribute("value");

// ! Event Handlers

setToggle(search_toggle);

window.addEventListener("scroll", function() {
  if (window.pageYOffset > 0) {
    to_top_button.classList.remove("not-visible");
  } else {
    to_top_button.classList.add("not-visible");
  }
})

home_button.addEventListener("click", function() {
  window.location.href = "../../"
})

prev_page_button.addEventListener("click", function () {navigatePage(false);})
next_page_button.addEventListener("click", function () {navigatePage(true);})

to_top_button.addEventListener("click", function() {scrollToY(0);})

page_indicator.addEventListener("click", function() {
  if (!page_indicator.classList.contains("collapsed") && page_input.children.length > 1) {
    page_indicator.classList.add("collapsed");
    page_form.classList.remove("collapsed");
    page_input.focus();
  }
})

page_input.addEventListener("focusout", function() {
  page_form.classList.add("collapsed");
  page_indicator.classList.remove("collapsed")
})

page_input.addEventListener("change", function() {
  window.location.href = `${page_input.value}`
})

function navigatePage(direction) {
  let url_array = window.location.href.split("/");
  let current_page_number = parseInt(url_array[url_array.length - 1], 10);

  if (direction) {
    new_page_number = current_page_number + 1;
  } else {
    new_page_number = current_page_number - 1;
  }

  window.location.href = `${new_page_number}`;
}

// ! Ready
window.scroll();
