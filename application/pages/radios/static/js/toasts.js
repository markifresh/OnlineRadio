function clearForm(){
  document.getElementById('live_track_left').innerText = "";
  document.getElementById('live_track_artist').innerText = "";
  document.getElementById('live_track_title').innerText = "";
  document.querySelector('#live_like path').classList.remove('liked');
  document.querySelector('.live-track').id ='0';
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
        document.getElementById('live_track_artist').innerText = data.track.artist;
        document.getElementById('live_track_title').innerText = data.track.title;
        document.querySelector('.live-track').id = data.track.id;
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

function HmsToSeconds(data){
  console.log('');
}
