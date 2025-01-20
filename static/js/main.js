//passport_list.html

function addForm() {
    // Adds a new form to the list
    // and increments the form counter
    let formIdx = document.querySelector('#id_form-TOTAL_FORMS').value;
    let newForm = document.querySelector('.passport-form').cloneNode(true);
    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formIdx);
    newForm.querySelectorAll('input, select').forEach(function (input) {
        let name = input.getAttribute('name');
        if (name) {
            input.setAttribute('name', name.replace(/-\d+-/, '-' + formIdx + '-'));
        }
        var id = input.getAttribute('id');
        if (id) {
            input.setAttribute('id', id.replace(/-\d+-/, '-' + formIdx + '-'));

        }
    })
    document.querySelector("#forms-container").appendChild(newForm);
    document.querySelector("#id_form-TOTAL_FORMS").value = Number(formIdx) + 1;
};

const bookButton = document.querySelector(".book-trip");
const bookForm = document.querySelector(".book-form");
document.querySelectorAll(".seat").forEach(function (element) {
    // Mark seat as booked
    element.addEventListener("click", function (e) {
        e.preventDefault();
        element.classList.toggle("bg-secondary");
        element.classList.toggle("booked");
        element.classList.toggle("bg-success");
    });
});

function clearSeats() {
    // Remove all hidden inputs from the form
    const inputs = document.querySelectorAll(".book-form input[name='seat']");
    inputs.forEach(function (e) {
        e.remove()
    })
}

function bookSeats(event) {
    // Creates a hidden input for each selected seat 
    // and adds it to the form

    const bookedSeats = document.querySelectorAll(".booked");
    if (bookedSeats.length > 0) {
        bookedSeats.forEach(function (e) {
            let seat = document.createElement("input")
            seat.setAttribute("type", "hidden")
            seat.setAttribute("name", "seat")
            seat.setAttribute("value", e.children[0].getAttribute("data-seat"))
            bookForm.prepend(seat)
        });
    } else {
        event.preventDefault();
        alert("Please select a seat");
    }


}


// Предположим, у вас есть время бронирования в переменной bookingTime
const formPayment = document.querySelector(".nav-form");
let bookingTime = document.querySelector("#bookingTime");
let sessionId

if (bookingTime != null) {
    sessionId = bookingTime.getAttribute("data-session-id");
    bookingTime = bookingTime.value;
    localStorage.setItem('bookingTime', bookingTime);
    localStorage.setItem('sessionId', sessionId);
}
function updateTimer() {
    bookingTime = localStorage.getItem('bookingTime');
    if (bookingTime) {
        let bookingDate = + bookingTime;
        let now = Math.floor(new Date() / 1000);
        let elapsed = now - bookingDate
        let remaining = 30 * 60 - elapsed;
        let timer = document.getElementById('timer');
        if (remaining > 0) {
            let minutes = Math.floor(remaining / 60);
            let seconds = Math.floor((remaining % 60));
            timer.innerHTML = minutes + ' минут ' + seconds + ' секунд';
        } else {
            localStorage.removeItem("bookingTime")
            localStorage.removeItem('sessionId');
            timer.innerHTML = '';
        }
    } else {
        formPayment.classList.add("opacity-0")
    }
}

// Обновляем таймер каждую секунду
if (localStorage.getItem('sessionId') != "") {
    sessionId = localStorage.getItem('sessionId');
    formPayment.classList.remove("opacity-0")
    formPayment.setAttribute("action", `/booking/payment/${sessionId}/`);
    setInterval(updateTimer, 1000);
    updateTimer(); // Обновить таймер сразу после загрузки страницы
}
