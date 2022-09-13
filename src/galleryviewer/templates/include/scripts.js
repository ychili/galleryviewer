let pageIndex = 0;

const tabs = document.getElementsByClassName("tab");
const pages = document.getElementsByClassName("page");
const images = document.getElementsByClassName("image-item");

openPage(pageIndex);

// onclick="openPage(i)"
for (let i = 0; i < tabs.length; i++) {
    tabs[i].addEventListener("click", function() {openPage(i)});
}

document.addEventListener("keydown", processKeyDown);

for (let i = 0; i < images.length; i++) {
    images[i].addEventListener("click", processClick);
}

// Show page (0 indexed) and update pageIndex
function openPage(pageNumber) {
    var i;

    // Hide all elements with class="page"
    for (i = 0; i < pages.length; i++) {
        pages[i].style.display = "none";
    }

    // Remove the class "active" from all elements with class="tab"
    for (i = 0; i < tabs.length; i++) {
        tabs[i].className = tabs[i].className.replace(" active", "");
    }

    // Show the current page
    pages[pageNumber].style.display = "block";
    // Add an "active" class to the tab for the current page
    tabs[pageNumber].className += " active";

    window.scroll(0, 0);

    pageIndex = pageNumber;
}

// Increment page number by *n*
function plusPage(n) {
    let pageNumber = pageIndex + n;

    // Overflow/underflow behavior: wrap around
    if (pageNumber >= pages.length) {pageNumber = 0}
    else if (pageNumber < 0) {pageNumber = pages.length - 1}

    openPage(pageNumber);
}

function processClick(e) {
    const xThreshold = 0.4;
    const xClickPos = e.offsetX / e.currentTarget.clientWidth;

    if (xClickPos < xThreshold) {
        plusPage(-1);
    } else {
        plusPage(1);
    }
}

const SCROLL_AMOUNT = 40;

function processKeyDown(e) {
    switch (e.key.toLowerCase()) {
        case 'a':
            plusPage(-1); return;
        case 'd':
            plusPage(1); return;
        case 'w':
            window.scrollBy(0, -SCROLL_AMOUNT); return;
        case 's':
            window.scrollBy(0, SCROLL_AMOUNT); return;
    }
    switch (e.keyCode) {
        case 37:
            // left arrow
            plusPage(-1); return;
        case 39:
            // right arrow
            plusPage(1); return;
    }
}
