var botMessage = "";

function sendMessage() {
    let messageContainer = document.getElementById("messages");
    let message = document.getElementById("message").value;

    if (message.length > 0 && message.length <= 100) {
        document.getElementById("welcome").style.display = "none";
        let yourMessageElement = document.createElement("p");
        yourMessageElement.className = "messageContent";
        yourMessageElement.innerHTML = "<b>You:</b> " + message;
        messageContainer.appendChild(yourMessageElement);

        let botMessageElement = document.createElement("p");
        botMessageElement.className = "messageContent";
        botMessageElement.innerHTML = "...";
        messageContainer.appendChild(botMessageElement);

        let data = {
            "message" : message,
            "trainModel" : true,
            "botMessage" : botMessage
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
            if(responseData["success"]) {
                botMessage = responseData["reply"];
                botMessageElement.innerHTML = "<b>crimbot:</b> " + responseData["reply"];
            }
        })
        .catch(error => {
        console.error('Error:', error);
        });
    }
}

function checkKeyPress(event) {
    if (event.keyCode === 13) {
      sendMessage();
    }
  }