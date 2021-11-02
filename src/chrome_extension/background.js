//Function to send favicon img data as json if needed (stringify needed in sendRequest)
function convertToBase64(url){
    var img = document.createElement('IMG'),
        canvas = document.createElement('CANVAS'),
        ctx = canvas.getContext('2d'),
        data = '';

    // Set the crossOrigin property of the image element to 'Anonymous',
    // allowing us to load images from other domains so long as that domain 
    // has cross-origin headers properly set

    img.crossOrigin = 'Anonymous'

    // Because image loading is asynchronous, we define an event listening function that will be called when the image has been loaded
    img.onLoad = function(){
        // When the image is loaded, this function is called with the image object as its context or 'this' value
        canvas.height = this.height;
        canvas.width = this.width;
        ctx.drawImage(this, 0, 0);
        data = canvas.toDataURL();
    };

    return data;
}

async function checkFav(tab){
    return new Promise(resolve => {
        if (tab.status == 'complete')
        return true;
    });
}

function sendRequest(tab){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
        }
    };

    var favicon = "";
    var url = tab.url;
    var result = "";

/*
    (async () => {
      const result = await checkFav(tab);
      if (result == true)
        favicon = tab.favIconUrl;
    })();
    */

    var iurl = tab.url ? tab.url.replace(/#.*$/, '') : ''; // drop #hash

    if (tab.favIconUrl && tab.favIconUrl != '' 
        && tab.favIconUrl.indexOf('chrome://favicon/') == -1) {
        // favicon appears to be a normal url
        favicon = tab.favIconUrl;
    }
    else {
        // couldn't obtain favicon as a normal url, try chrome://favicon/url
        favicon = 'chrome://favicon/' + iurl;
    }

    console.log(favicon);

    formD = new FormData();
    formD.append("url", url);
    formD.append("ic_link", favicon);
    
    xhttp.open("POST", "http://192.168.1.173:5000/send_url");
    xhttp.send(formD);
}


chrome.tabs.onActivated.addListener((tabId, change, tab) => {
    //sendRequest(tab);
});

chrome.tabs.onUpdated.addListener((tabId, change, tab) => {
    if (tab.active && change.url) {
        sendRequest(change)
    }
});

chrome.tabs.onRemoved.addListener(function (tabId, change, tab) {
    //sendRequest(change);

});