const iframeWidth = "200";
const iframeHeight = "80";

function createSpotifyIframe(track){
    let iframe = document.createElement('iframe');
    iframe.width = iframeWidth;
    iframe.height = iframeHeight;
    iframe.frameBorder = "0";
    iframe.allow = "encrypted-media";
    iframe.allowtransparency = "true";
//    iframe.loading = "eager";
    iframe.style.display = "block";
//    iframe.id = "service_player'"
    iframe.src = "https://open.spotify.com/embed/track/" + track;
    document.body.appendChild(iframe);
    iframe.innerHTML += 'onload="access()"';

//    iframe {
//    visibility: hidden;
//    position: absolute;
//    left: 0; top: 0;
//    height:0; width:0;
//    border: none;
//}

}
//createSpotifyIframe('7ckJgqAp6jAUSJ9Av2t9LY');
//createSpotifyIframe('1RqCJLKcugVz6XiEIj96T9');



function createDeezerIframe(track){
    let iframe = document.createElement('iframe');
    iframe.width = iframeWidth;
    iframe.height = iframeHeight;
    iframe.frameBorder = "0";
    iframe.allow = "encrypted-media";
    iframe.allowtransparency = "true";
//    iframe.loading = "eager";
    iframe.style.display = "block";
//    iframe.id = "service_player'"
    iframe.src = "https://widget.deezer.com/widget/dark/track/" + track;
    document.body.appendChild(iframe);
    iframe.innerHTML += 'onload="access()"';

//    iframe {
//    visibility: hidden;
//    position: absolute;
//    left: 0; top: 0;
//    height:0; width:0;
//    border: none;
//}

}

//createDeezerIframe('4677572');
//createDeezerIframe('126534873');





function createPlayer(location_element, service_name){
    let player = '';
    if(service_name.toLocaleLowerCase() == 'spotify')
        player = '<iframe id="service_player"' +
                 'src="https://open.spotify.com/embed/track/1DFixLWuPkv3KT3TnV35m3"' +
                 'width="700"' +
                 'height="80"' +
                 'frameborder="0"' +
                 'allowtransparency="true"' +
                 'allow="encrypted-media"></iframe>'
}


function replaceTrack(url){
    document.querySelector('iframe').src = "https://open.spotify.com/embed/track/" + url;
}

function play(){
    if(document.querySelector('[title="Play"]'))
//    if(document.querySelector('iframe').contentWindow.document.querySelector('[title="Play"]'))
        document.querySelector('[title="Play"]').click();
}

function pause(){
    if(document.querySelector('[title="Pause"]'))
        document.querySelector('[title="Pause"]').click();
}

function playTrack(url){
    pause();
    replaceTrack(url);
    play;
}

function reloadPlayer(){
    document.querySelector('iframe').src += "";
}

