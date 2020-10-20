function keepPlaying(){
  let radioName = sessionStorage.getItem('playingNow');
  if(radioName && !window.location.pathname.includes('/radios/')){
    var audioObj = document.createElement('audio');
    audioObj.autoplay = true;
    // audioObj.controls = true;
    audioObj.src = sessionStorage.getItem(radioName);
    audioObj.play();}
}
keepPlaying();
