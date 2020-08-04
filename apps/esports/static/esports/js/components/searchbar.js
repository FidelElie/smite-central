search_bar = document.getElementsByClassName("searchbar")[0];
search_input = document.getElementById("desired-search");

search_bar.style.maxHeight = "0px";

function setToggle(element) {
  element.addEventListener("click", function() {
    if (search_bar.style.maxHeight == "0px") {
      addIcon(element, "mdi-close");
      search_bar.style.maxHeight = `${search_bar.scrollHeight}px`;
    } else {
      addIcon(element, "mdi-magnify");
      search_bar.style.maxHeight = "0px";
    }
    search_input.focus();
  })
}
