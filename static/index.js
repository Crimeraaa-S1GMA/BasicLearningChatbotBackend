function sendMessage() {
    let messageContainer = document.getElementById("messages");
    let message = document.getElementById("message").value;

    let yourMessageElement = document.createElement("p");
    yourMessageElement.innerHTML = "<b>You:</b> " + message;
    messageContainer.appendChild(yourMessageElement);

    let data = {
        "message" : message
    };
    let serializedData = JSON.stringify(data);
    document.getElementById("message").value = "";

    var url = '/send-message';
    fetch(url, {
     method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: serializedData
     })
      .then(response => response.json())
      .then(responseData => {
        let yourMessageElement = document.createElement("p");
        yourMessageElement.innerHTML = "<b>Bot:</b> " + responseData["reply"];
        messageContainer.appendChild(yourMessageElement);
     })
     .catch(error => {
       console.error('Error:', error);
      });
}

function checkKeyPress(event) {
    if (event.keyCode === 13) {
      sendMessage();
    }
  }