const iframeWidth = "1200";
const iframeHeight = "80";

// function createSpotifyIframe(track, domElem, width, height){
//     let iframe = document.createElement('iframe');
//     iframe.width = width;
//     iframe.height = height;
//     iframe.frameBorder = "0";
//     iframe.allow = "encrypted-media";
//     iframe.allowtransparency = "true";
// //    iframe.loading = "eager";
//     iframe.style.display = "block";
// //    iframe.id = "service_player'"
//     iframe.src = "https://open.spotify.com/embed/track/" + track;
//     domElem.appendChild(iframe);
//     iframe.style.display = 'none';
//     iframe.style.paddingBottom = '0px';
//     iframe.innerHTML += 'onload="access()"';

//    iframe {
//    visibility: hidden;
//    position: absolute;
//    left: 0; top: 0;
//    height:0; width:0;
//    border: none;
//}

// }
// createSpotifyIframe('7ckJgqAp6jAUSJ9Av2t9LY');
// createSpotifyIframe('1RqCJLKcugVz6XiEIj96T9');



// function createDeezerIframe(track, domElem, width, height){
//     let iframe = document.createElement('iframe');
//     iframe.width = width;
//     iframe.height = height;
//     iframe.frameBorder = "0";
//     iframe.allow = "encrypted-media";
//     iframe.allowtransparency = "true";
// //    iframe.loading = "eager";
//     iframe.style.display = "block";
// //    iframe.id = "service_player'"
//     iframe.src = "https://widget.deezer.com/widget/dark/track/" + track;
//     iframe.style.display = 'none';
//     iframe.style.paddingBottom = '0px';
//     domElem.appendChild(iframe);
//     iframe.innerHTML += 'onload="access()"';

//    iframe {
//    visibility: hidden;
//    position: absolute;
//    left: 0; top: 0;
//    height:0; width:0;
//    border: none;
//}

// }

function createEmbed(track, domElem, width=iframeWidth, height=iframeHeight){
  let td = document.createElement('td');
  td.style.display = 'none';
  let iframe = document.createElement('iframe');
  iframe.width = width;
  iframe.height = height;
  iframe.frameBorder = "0";
  iframe.allow = "encrypted-media";
  iframe.allowtransparency = "true";
  iframe.style.display = "block";

  if (getCookie('ms_service') == 'spotify')
    iframe.src = "https://open.spotify.com/embed/track/" + track;

  else if (getCookie('ms_service') == 'deezer')
    iframe.src = "https://widget.deezer.com/widget/dark/track/" + track;

  // iframe.style.display = 'none';
  iframe.style.padding = "0px";
  iframe.innerHTML += 'onload="access()"';
  td.style.padding = "0px";
  td.appendChild(iframe);
  
  domElem.insertBefore(td, domElem.children[1])
  // domElem.appendChild(iframe);

}
// createDeezerIframe('4677572');
// createDeezerIframe('126534873');



function replaceTrack(url){
    document.querySelector('iframe').src = "https://open.spotify.com/embed/track/" + url;
}

function playSpotify(){
    if(document.querySelector('[title="Play"]'))
//    if(document.querySelector('iframe').contentWindow.document.querySelector('[title="Play"]'))
        document.querySelector('[title="Play"]').click();
}

function pauseSpotify(){
    if(document.querySelector('[title="Pause"]'))
        document.querySelector('[title="Pause"]').click();
}

function playDeezer(){
    if(document.querySelector('[data-testid="widget-player-play"]'))
//    if(document.querySelector('iframe').contentWindow.document.querySelector('[title="Play"]'))
      document.querySelector('[data-testid="widget-player-play"]').click();
}

function pauseDeezer(){
    if(document.querySelector('[data-testid="widget-player-pause"]'))
        document.querySelector('[data-testid="widget-player-pause"]').click();
}

function playTrack(url){
    pause();
    replaceTrack(url);
    play;
}

function reloadPlayer(){
    document.querySelector('iframe').src += "";
}
