const video = document.querySelector("#video");
// const startCamera = document.querySelector("#start_camera");

let is_scanning = false;
const dropdownMenu = document.querySelector("#dropdown-camera-menu-item")
const buttonMenu = document.querySelector("#dropdown-camera-menu-button")

const detectedImg = document.querySelector("#detected_frame");


function startCameraWithID(deviceId) {
    const constraints = {
        video: {
            deviceId: deviceId ? { exact: deviceId } : undefined,
            // width: { max: 640 },
            // height: { max: 480 },
            width: { max: 160 },
            height: { max: 160 },
        }
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            const video = document.getElementById('video');
            video.srcObject = stream;
        })
        .catch(error => {
            console.error("Something went wrong!", error);
        });
}


navigator.mediaDevices.enumerateDevices()
    .then(devices => {
        devices.forEach((device, index) => {
            if (device.kind === 'videoinput') {
                dropdownMenu.insertAdjacentHTML('beforeend',
                    `<button class="dropdown-item camera" value="${device.deviceId}" href="#">${device.label}</button>`
                )
            }
        });
        var buttons = document.querySelectorAll(`.camera`)
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].addEventListener('click', function () {
                startCameraWithID(this.value)
                buttonMenu.textContent = this.textContent
            });
        }
        startCameraWithID(buttons[0].value)
        buttonMenu.textContent = buttons[0].textContent
        scanning();
    })
    .catch(error => {
        console.error("Error enumerating devices:", error);
    });


function scanning() {
    // if (!is_scanning) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL("image/jpeg");

    if (imageData.startsWith("data:image/jpeg")) {
        id = getCookie("id");
        target = getCookie("target");
        body = JSON.stringify({
            id: id,
            target: target,
            type: 'face',
            data: {
                image: imageData,
            },
        })
        fetch("/cheat_logger/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: body,
        }).then(response => response.json())
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    } else {
        console.error("Waiting for image!");
    }

    

    setTimeout(() => {
        requestAnimationFrame(scanning);
    }, 500);
}


// startCamera.addEventListener('click', () => {
//     is_scanning = !is_scanning;
//     if (is_scanning) {
//         startCamera.textContent = "Stop Scan"
//         requestAnimationFrame(scanning);
//     } else {
//         startCamera.textContent = "Start Scan"
//     }
// });