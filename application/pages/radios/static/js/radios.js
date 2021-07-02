function hideElem(domElem){
  domElem.style.transitionDuration = "600ms";
  // domElem.style.transitionDelay  = "500ms";
  domElem.style.opacity = '0';
  setTimeout(function(){
    domElem.style.display = 'none';
    // let tds = domElem.querySelectorAll('td');
    // tds[0].style.display = 'none';
    // for (let td of tds)
    //   td.style.display = 'none';
  }, 600);

}

function showElem(domElem){
  domElem.style.opacity = '1';
}

function toggleEmbed(domElem, width){
  if(!domElem.querySelector('.embed-player')){
    let track = domElem.classList[0].replace('ms_id-','')
    createEmbed(track, domElem, width);
    setTimeout(function(){
      domElem.querySelector('.embed-player').style.display = '';
      domElem.style.opacity = '1';
    }, 600);
}
  else{
      domElem.querySelector('.embed-holder').style.opacity = '1';
    setTimeout(function(){
      domElem.querySelector('.embed-holder').style.display = '';
      domElem.querySelector('.embed-player').remove();
      domElem.style.opacity = '1';
    }, 600);
  }
}

function findBTN(elem){
  let btn = '';
  if(elem.parentElement.tagName == 'BUTTON')
    btn =  elem.parentElement;

  else if(elem.parentElement.parentElement.tagName == 'BUTTON')
    btn = elem.parentElement.parentElement;
  return btn
}

// Play Radio
document.getElementById('live_play').addEventListener('click', function(event){
  let radios = getRadios();
  if (radios.includes(sessionStorage.getItem('lastPlayed')))
    playRadio(sessionStorage.getItem('lastPlayed'));
  else
    playRadio(radios[0]);
});


// Pause Radio
document.getElementById('live_pause').addEventListener('click', pauseRadio);


// Play Previous Radio
document.getElementById('live_prev').addEventListener('click', function(event){
  playRadio(getPrevRadio());
});

// Play Next Radio
document.getElementById('live_next').addEventListener('click', function(event){
  playRadio(getNextRadio());
});

// Like Player
document.getElementById('live_like').addEventListener('click', function(event){
  let trackID = document.querySelector('.live-track').id;
  if (trackID && trackID > 0){
    if(document.querySelector('#live_like path').classList.contains('liked'))
      deleteTrackFromLiked(trackID);
    else
      addTrackToLiked(trackID);
    document.querySelector('#live_like path').classList.toggle('liked');
  }
});


function toggleToLiked(trackID, add=true) {
  let url = '/api/users/' + getCookie('user_id') + '/tracks/liked';
  let data = {'tracks_ids': trackID};
  if(add)
    commonFetch(url, 'POST', data)
  else
    commonFetch(url, 'DELETE', data)
}

function addTrackToLiked(trackID) {
  toggleToLiked(trackID, true)
}

function deleteTrackFromLiked(trackID) {
  toggleToLiked(trackID, false)
}

document.getElementById('carTracks').addEventListener('click', function(event){
// Show Embed and Play
  if(event.target.classList.contains('track-play')){
    let btn = findBTN(event.target);
    btn.classList.toggle('flip');
    let elem = btn.parentElement.parentElement;
      hideElem(elem.children[1]);
      // showEmbed(elem, elem.querySelector('td').offsetWidth);
      toggleEmbed(elem, width="300");
    }

// Like-UnLike track
  else if(event.target.classList.contains('track-like')){
    let btn = findBTN(event.target);
    let trackID = btn.parentElement.parentElement.id;
    if(btn.querySelector('path').classList.contains('liked'))
      deleteTrackFromLiked(trackID);
    else
      addTrackToLiked(trackID);
    btn.querySelector('path').classList.toggle('liked');
    }

// Delete Track from Import
  else if (event.target.classList.contains('track-delete')) {
    let btn = findBTN(event.target);
    let data = {'tracks_ids': btn.parentElement.parentElement.id};
    let importID = document.querySelector('.import-id').id;
    let url = '/api/users/' + getCookie('user_id') + '/imports/' + importID + '/tracks';
    let tr = btn.parentElement.parentElement;
    let trs = document.querySelectorAll('#tableTracks tr');
    let nextTrack = '';
    for(let i=0; i < trs.length; i++){
      if(trs[i] == tr)
      {
        for(let t=i; t < trs.length; t++)
        {
          if(trs[t].style.display == 'none')
              {
                nextTrack = trs[t];
                break;
              }
        }
        break;
      }
    }
    commonFetch(url, "DELETE", data, function(){
      tr.classList.toggle('move-hide');
      setTimeout(function(){
        tr.remove();
        if (nextTrack)
          nextTrack.style.display="";
      }, 1000);
    });

  }

// Export Track
  else if (event.target.classList.contains('track-export')) {
    let btn = findBTN(event.target);
    btn.disabled = true;
    let btnSVG = btn.querySelector('svg');
    btnSVG.classList.toggle('export-animation');
    let exportInterval = setInterval(function(){btnSVG.classList.toggle('export-animation')}, 1500);

    let radioName = document.querySelector('.import-radio-name').id;
    let url = '/api/users/' + getCookie('user_id') + '/exports/' + radioName + '/tracks';
    let data = {'tracks_ids': btn.parentElement.parentElement.id};
    commonFetch(url, "POST", data, function(resData){
      clearInterval(exportInterval);
      console.log(resData);
    })
  }
})
