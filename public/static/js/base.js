loading_contents = document.getElementsByClassName("loading-contents")[0];
setTimeout(() => {
  loading_contents.classList.add("loaded");
}, 500)
setTimeout(() => {
  loading_contents.classList.add("hidden")
}, 1000)
