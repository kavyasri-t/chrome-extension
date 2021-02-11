chrome.extension.onMessage.addListener(function(request, sender, sendResponse) {
    routeMessage(request.type);
    return true;
});

function routeMessage(messageType) {
    switch (messageType) {
        case "openWS":
            openConnection();
            break;
        case "closeWS":
            closeConnection();
            break;
        case "zoom-in":
            zoomIn();
            break;
        case "zoom-out":
            zoomOut();
            break;
		case "scroll-up":
		    scrollUp();
			break;
		case "scroll-down":
		    scrollDown();
			break;	
        default:
            chrome.tabs.getSelected(null, function(tab) {
                chrome.tabs.sendMessage(tab.id, { type: messageType, tabID: tab.id });
            });
            break;
    }
}
	
function scrollDown() {
	chrome.tabs.executeScript({
    code: `document.documentElement.scrollTop+=200;`
  });
}

function scrollUp() {
	chrome.tabs.executeScript({
    code: `document.documentElement.scrollTop-=200;`
  });
}


function zoomIn() {
    chrome.tabs.getSelected(null, function(tab) {
        chrome.tabs.getZoom(tab.id, function(zoomFactor) {
            chrome.tabs.setZoom(tab.id, zoomFactor + 0.2);
        });
    });
}

function zoomOut() {
    chrome.tabs.getSelected(null, function(tab) {
        chrome.tabs.getZoom(tab.id, function(zoomFactor) {
            chrome.tabs.setZoom(tab.id, zoomFactor - 0.2);
        });
    });
}

var ws = null;

function closeConnection() {
    if (ws)
        ws.close();
}

function openConnection() {
    //closeConnection();
    var url = "ws://192.168.1.102:9001";
    ws = new WebSocket(url);
    ws.onopen = onOpen;
    ws.onclose = onClose;
    ws.onmessage = onMessage;
    ws.onerror = onError;
}

function onOpen() {
    console.log("Websocket connected.");
}

function onClose() {
    console.log("Websocket disconnected.");
    ws = null;
}

function onMessage(event) {
    console.log(event);
    routeMessage(event.data);
}

function onError(event) {
    alert("Websocket error.");
}

