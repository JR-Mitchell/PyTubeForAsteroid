function requestUrl(inputObj,buttonObj) {
    return function(){
        buttonObj.parentNode.removeChild(buttonObj);
        inputObj.parentNode.removeChild(inputObj);
        var requestData = new FormData();
        requestData.set("url",inputObj.value);
        var request = new XMLHttpRequest();
        request.open("POST","request/"+TOOLS.QUERIES.getCurrentSubtabName(),true);
        request.onload = function(){
            if (request.status == "200") {
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Successful request! Song added with info:");
                var data = JSON.parse(request.response);
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Song name: ");
                BODY_CONTENT.appendText(data["name"]);
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Artist: ");
                BODY_CONTENT.appendText(data["artist"]);
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Duration: ");
                BODY_CONTENT.appendText(data["duration"]);
            } else {
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Raised error with error code ");
                BODY_CONTENT.appendText(request.status);
                BODY_CONTENT.appendText(". Please try again below:");
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendNode(inputObj);
                BODY_CONTENT.appendNode(buttonObj);
            }
        };
        request.onerror = function(){
            BODY_CONTENT.appendBreak();
            BODY_CONTENT.appendText("Request raised unexpected error. Please try again below:");
            BODY_CONTENT.appendNode(inputObj);
            BODY_CONTENT.appendNode(buttonObj);
        };
        request.ontimeout = function(){
            BODY_CONTENT.appendBreak();
            BODY_CONTENT.appendText("Request timed out. Please try again below:");
            BODY_CONTENT.appendBreak();
            BODY_CONTENT.appendNode(inputObj);
            BODY_CONTENT.appendNode(buttonObj);
        };
        request.send(requestData);
        BODY_CONTENT.appendText("Sent off request for url ")
        BODY_CONTENT.appendText(inputObj.value);
        BODY_CONTENT.appendText(". Awaiting response...")
    }
}

BODY_CONTENT.appendText("Request by YouTube URL:");
var urlInput = document.createElement("input");
BODY_CONTENT.appendBreak();
BODY_CONTENT.appendNode(urlInput);
var sendButton = document.createElement("button");
sendButton.innerText = "Request!";
sendButton.onclick = requestUrl(urlInput,sendButton);
BODY_CONTENT.appendNode(sendButton);
