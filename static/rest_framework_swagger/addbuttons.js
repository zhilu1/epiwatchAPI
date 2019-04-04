let navbar = document.getElementsByClassName("topbar-wrapper");
let link = document.createElement("a");
let wrapper = document.createElement("div");
wrapper.className = "download-url-wrapper";
link.className = "download-url-button button";
link.href = "logs";
link.innerText = "Logs";
navbar[0].appendChild(wrapper);
wrapper.appendChild(link);
