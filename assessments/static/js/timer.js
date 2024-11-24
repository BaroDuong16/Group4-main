function startTimer(duration, display) {
    var start = new Date(document.querySelector("#time_start").getAttribute("time_start")).getTime(),
        diff,
        minutes,
        seconds;
    function timer() {
        diff = duration - (((Date.now() - start) / 1000) | 0);

        minutes = (diff / 60) | 0;
        seconds = (diff % 60) | 0;

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = "Time Left: " + minutes + ":" + seconds;

        if (diff <= 0) {
            document.querySelector('#submit_btn').click();
        }
    };
    // Run the timer function every second
    timer();
    setInterval(timer, 1000);
}

window.onload = function () {
    var duration = document.querySelector('#time_limit').getAttribute('value');
    var display = document.querySelector('#timer');

    startTimer(duration, display);
};