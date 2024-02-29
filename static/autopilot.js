var messageContainer = document.getElementById("messages");

var messageAwaitElement = document.createElement("p");
messageAwaitElement.className = "messageContent";
messageAwaitElement.innerHTML = "..."
messageContainer.appendChild(messageAwaitElement);

sendMessage("Hello", true);

function sendMessage(myMessage, sendMyMessage) {
    if (myMessage.length > 0 && myMessage.length <= 100) {
        let yourMessageElement = document.createElement("p");
        yourMessageElement.className = "messageContent";
        yourMessageElement.innerHTML = myMessage;
        messageContainer.appendChild(yourMessageElement);

        messageAwaitElement.remove();
        messageContainer.appendChild(messageAwaitElement);

        let data = {
            "message" : myMessage,
            "trainModel" : true
        };
        let serializedData = JSON.stringify(data);

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
            setTimeout(sendMessage, 1000, responseData["reply"], false)
        })
        .catch(error => {
        console.error('Error:', error);
        });
    }
}