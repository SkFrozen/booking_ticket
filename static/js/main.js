//passport_list.html

function addForm() {
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
    element.addEventListener("click", function () {
        element.classList.toggle("bg-secondary");
        element.classList.toggle("booked");
        element.classList.toggle("bg-success");
    });
});

function clearSeats() {
    const inputs = document.querySelectorAll(".book-form input[name='seat']");
    inputs.forEach(function (e) {
        e.remove()
    })
}

function bookSeats(event) {
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