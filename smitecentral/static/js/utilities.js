function addIcon(element, icon_class) {
  removeIcon(element)
  element.classList.add(icon_class)
}

function removeIcon(element) {
  classes = element.classList
  icon_class = Array.from(classes).filter(x => x.includes("mdi-"));
  if (icon_class.length != 0) {
    element.classList.remove(icon_class[0])
  }
}

function parseMedia(query, options) {
  if (query.matches) {
    options.match();
  } else {
    options.nomatch();
  }
}

function toggleContents(element_to_toggle, element_to_close = null) {
  if (element_to_toggle.classList.contains("hidden")) {
    element_to_toggle.classList.remove("hidden");
  } else {
    element_to_toggle.classList.add("hidden");
  }

  if (element_to_close.classList != null) {
    if (!element_to_close.classList.contains("hidden")) {
      element_to_close.classList.add("hidden")
    }
  }
}

function secondsToTimeString(seconds) {
  if (seconds == 0) {
    return "00:00"
  } else {
    let hours = seconds / 3600;
    let split_hours = hours.toString(10).split(".")
    let minutes = parseFloat(`.${split_hours[1]}`, 10) * 60;
    let split_minutes = minutes.toString(10).split(".")
    let int_hours = split_hours[0].toString();
    let int_minutes = split_minutes[0].toString();
    let time_data = [int_hours, int_minutes]

    for (let i = 0; i < time_data.length; i++) {
      if (time_data[i].length < 2) {
        time_data[i] = `0${time_data[i]}`
      }
    }
    return `${time_data[0]}:${time_data[1]}`
  }
}

function scrollToY(y) {
  window.scrollTo({
    left: 0,
    top: y,
    behavior: "smooth"
  })
}

function extractStyleValue(element, style_rule) {
  let number_regex = new RegExp("-?[0-9]+");
  try {
    number = parseInt(number_regex.exec(element.style[style_rule])[0], 10);
  } catch (TypeError) {
    number = 0;
  }
  return number
}
