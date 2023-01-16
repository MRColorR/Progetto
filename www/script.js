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
  var factorial = 1;
  
  for (var i = 1; i <= number; i++) {
    factorial *= i;
  }

  result.innerHTML = "The factorial of " + number + " is " + factorial;
}
