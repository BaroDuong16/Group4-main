document.addEventListener("DOMContentLoaded", function () {
    const timeElements = document.querySelectorAll(".time");

    timeElements.forEach(function (element) {
        let totalSeconds = parseInt(element.textContent, 10);
        let minutes = Math.floor(totalSeconds / 60);
        let seconds = totalSeconds % 60;
        element.textContent = `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    });
});