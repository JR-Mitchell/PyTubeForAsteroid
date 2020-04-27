function requestUrl(inputObj) {
    return function(){
        var requestData = new FormData();
        requestData.set("url",inputObj.value);
        var request = new XMLHttpRequest();
        request.open("POST","request/"+TOOLS.QUERIES.getCurrentSubtabName(),true);
        request.onload = function(){
            if (request.status == "200") {
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Successful request!");
            } else {
                BODY_CONTENT.appendBreak();
                BODY_CONTENT.appendText("Error code: ");
                BODY_CONTENT.appendText(request.status);
            }
        };
        request.onerror = function(){
            BODY_CONTENT.appendBreak();
            BODY_CONTENT.appendText("Request raised unexpected error...");
        };
        request.ontimeout = function(){
            BODY_CONTENT.appendBreak();
            BODY_CONTENT.appendText("Request timed out...");
        };
        request.send(requestData);
    }
}

BODY_CONTENT.appendText("Request by YouTube URL:");
var urlInput = document.createElement("input");
BODY_CONTENT.appendBreak();
BODY_CONTENT.appendNode(urlInput);
var sendButton = document.createElement("button");
sendButton.innerText = "Request!";
sendButton.onclick = requestUrl(urlInput);
BODY_CONTENT.appendNode(sendButton);
