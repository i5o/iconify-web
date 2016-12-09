var keepwaiting = false;

function hover(element) {
    element.setAttribute('src', '/static/img/upload_hover.svg');
}

function unhover(element) {
    element.setAttribute('src', '/static/img/upload_normal.svg');
}

function randomcolor() {
    if (keepwaiting) {
        return;
    }

    keepwaiting = true;
    var xhr = new XMLHttpRequest();
    var random_color = document.getElementById("random-color");
    var waitffs = document.getElementById('waitplz');
    waitffs.style.display = 'inline';
    var icon_name = document.getElementById("icon_name").innerText;

    xhr.open("GET", "/randomcolor?filename=" + icon_name, true);
    xhr.onload = function(e) {
        if (xhr.readyState === 4) {
            document.getElementById("sugarized-icon").innerHTML = "Sugarized icon <small>(testing with random color)</small>";
            random_color.innerHTML = "Test with another random color";
            document.getElementById("sugarized-icon-img").setAttribute('src', '/static/random/' + icon_name + '?=' + new Date().getTime());
            waitffs.style.display = 'none';
            keepwaiting = false;
        }
    };
    xhr.send(null);
}

var file_input = document.getElementById("file-input");
if (file_input) {
    file_input.onchange = function() {
        var form = document.getElementById("form");
        document.getElementById("uploading_file").style.display = "block";
        form.submit();

    }
};

var random_color = document.getElementById("random-color");
if (random_color) {
    random_color.onclick = randomcolor;
};
