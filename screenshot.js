// Get the text input element and the image container element
var textInput = document.getElementById("text-input");
var imageContainer = document.getElementById("image-container");

// Set up event listener for the submit button
document.getElementById("text-form").addEventListener("submit", function(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the text from the text input element
    var text = textInput.value;

    // Send a request to the server with the text
    fetch("/format-text", {
        method: "POST",
        headers: { "Content-Type": "text/plain" },
        body: text
    })
    .then(response => response.text())
    .then(formattedText => {
        // Update the image container with the formatted text
        imageContainer.innerHTML = "";
        var formattedTextElement = document.createElement("div");
        formattedTextElement.style.fontFamily = "monospace";
        formattedTextElement.style.color = "gray";
        formattedTextElement.innerHTML = formattedText;
        imageContainer.appendChild(formattedTextElement);
    })
    .catch(error => console.error("Error:", error));
});