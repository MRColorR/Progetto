const input = document.getElementById("number");
input.addEventListener("keyup", function(event) {
  if (event.code === "Enter") {
    event.preventDefault();
    calculate();
  }
});

function calculate() {
  var number = document.getElementById("number").value;
  var result = document.getElementById("result");

  // Make an AJAX call to the backend API
  fetch(`${window.location.origin.replace(/:\d+$/, "")}:30500/factorial`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ number: number })
  })
    .then(response => {
      if (response.ok) {
        return response.json()
      } else {
        throw new Error(response.statusText)
      }
    })
    .then(data => {
      var factorial = data.factorial;
      result.innerHTML = "The factorial of " + number + " is " + factorial;
    })
    .catch(error => console.log(error))
}
