// stripe

fetch("/config/")
    .then((result) => { return result.json(); })
    .then((data) => {
        const stripe = Stripe(data.publicKey)
        const submitButton = document.querySelector("#submitButton");
        if (submitButton != null) {
            submitButton.addEventListener("click", () => {
                let django_url = url;
                fetch(django_url)
                    .then((result) => { return result.json(); })
                    .then((data) => {
                        console.log(data);
                        // Redirect to Stripe Checkout
                        return stripe.redirectToCheckout({ sessionId: data.sessionId })
                    })
                    .then((res) => {
                        console.log(res);
                    });
            })
        }
    })


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
        alert("Please select a seat");
        event.preventDefault();
    }


}
// bookButton.addEventListener("click", function (element) {
//     const bookedSeats = document.querySelectorAll(".booked");
//     const seats = [];

//     bookedSeats.forEach(function (e) {
//         let seat = document.createElement("input")
//         seat.setAttribute("type", "hidden")
//         seat.setAttribute("name", "seat")
//         seat.setAttribute("value", e.children[0].getAttribute("data-seat"))
//         bookForm.prepend(seat)
//     });
// if (seats.length > 0) {
//     const currentUrl = window.location.origin + element.target.getAttribute("action");
//     url = new URL(currentUrl);
//     seats.forEach(function (seat) {
//         url.searchParams.append("seat", seat);
//     })
//     element.target.setAttribute("action", url);
// } else {
//     element.preventDefault()
// };

// });
