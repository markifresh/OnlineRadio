function clearForm(){
  document.getElementById('live_track_left').innerText = "";
  document.getElementById('live_track_artist').innerText = "";
  document.getElementById('live_track_title').innerText = "";
  document.querySelector('#live_like path').classList.remove('liked');
  document.querySelector('.live-track').id ='0';
  document.querySelector('#live_like').disabled = true;
  clearInterval(sessionStorage.getItem('currentCounter'));
  returnBall();

}

function clearPlayer(){
  clearForm();
  clearTimeout(sessionStorage.getItem('live_timeout'));
  document.querySelector('.live_track_radio').id = "";
  document.querySelector('.live_track_radio').innerText = "";
  document.getElementById('live_play').style.display = '';
  document.getElementById('live_pause').style.display = 'none';
}


function setLiveData(){
  let radio = document.querySelector('.live_track_radio');
  if (radio.id){
    let url = '/api/users/' + getCookie('user_id') + '/radios/' + radio.id + '/live';
    clearForm();

    commonFetch(url, "GET", {}, function(data){
      console.log(data);
      if (!data.success)
        console.log('OOPS, looks like live update time took too much time [' + radio.id + ']');

      else if (data.success && data.need_to_wait)
        sessionStorage.setItem('live_timeout', setTimeout(setLiveData, 2000));

      else{
        data = data.result;
        document.getElementById('live_track_left').innerText = secondsToHms(data.check_within);
        moveBall(data.check_within);
        sessionStorage.setItem('currentCounter', setInterval(function(){decreaseSeconds(document.getElementById('live_track_left'))}, 1000));
        document.getElementById('live_track_artist').innerText = data.track.artist;
        document.getElementById('live_track_title').innerText = data.track.title;
        document.querySelector('.live-track').id = data.track.id;
        if (data.track.id > 0)
          document.querySelector('#live_like').disabled = false;
        sessionStorage.setItem('live_timeout', setTimeout(setLiveData, data.check_within * 1000));
      }
    });
  }
}

function secondsToHms(d) {
    d = Number(d);
    var h = Math.floor(d / 3600);
    var m = Math.floor(d % 3600 / 60);
    var s = Math.floor(d % 3600 % 60);

    var hDisplay = h < 10 && h !== 0 ? '0' + h : "";
    var mDisplay = m < 10 ? '0' + m : m;
    var sDisplay = s < 10 ? '0' + s : s;

    let result = mDisplay + ":" + sDisplay;
    if (hDisplay)
      result =  hDisplay + ":" + result;
    return result
}

function HMStoseconds(hms){
  hms = hms.split(':');
  let hours = 0;
  let minsLocation = 0;
  let secsLocation = 1;

  if (hms.length == 3){
      hours = hms[0];
      if (hours[0] == '0')
        hours = Number(hours[1]);
      else
        hours = Number(hours);

      minsLocation = 1;
      secsLocation = 2;
    }

  let mins = hms[minsLocation];
  if (mins[0] == '0')
    mins = Number(mins[1]);
  else
    mins = Number(mins);

  let secs = hms[secsLocation];
  if (secs[0] == '0')
    secs = Number(secs[1]);
  else
    secs = Number(secs);

  return hours*3600 + mins*60 + secs;
}

function decreaseSeconds(elem){
    if (elem.innerText == "00:00" || elem.innerText == "00:00:00")
        clearInterval(sessionStorage.getItem('currentCounter'));
    else{
      let hms = elem.innerText.split(':');
      if (hms.length == 2){
        let mins = hms[0];
        let secs = hms[1];
        if (secs != '00'){
            secs = Number(secs) - 1;
            secs = secs < 10 ? '0' + secs : secs ;
            elem.innerText = mins + ':' + secs
        }
        else if(secs == '00' && mins != '00'){
          mins = Number(mins) - 1;
          mins = mins < 10 ? '0' + mins : mins ;
          elem.innerText = mins + ':' + '59';
        }
      }
      }
}
function returnBall(){
  document.querySelector('.ball').style.transition = "transform 0s";
  document.querySelector('.ball').style.transform = "translateX(0px)";
}

function moveBall(timeOfMove){
  document.querySelector('.ball').style.transition = "transform " + timeOfMove + "s linear";
  document.querySelector('.ball').style.transform = "translateX(0px)";
  let finalPosition = document.querySelector('.time-line').offsetWidth;
  document.querySelector('.ball').style.transform = "translateX(" + finalPosition + "px)";

}
