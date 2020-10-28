var audioObj = document.createElement('audio');
audioObj.controls = true;
audioObj.autoplay = true;
document.body.appendChild(audioObj);

 document.querySelector('.container').addEventListener('click', function(){
   if(event.target.classList.contains('do-import'))
      makeImportExport(event.target, '/api/radios/update/');


   if(event.target.classList.contains('do-export'))
      makeImportExport(event.target, '/api/radios/export/');

    if(event.target.classList.contains('play-radio'))
       playRadio(event.target.id);

    if(event.target.classList.contains('pause-radio'))
      pauseRadio();
 })

function setRadiosStreams(){
  if(!sessionStorage.getItem('streamsSet'))
  {
    fetch('/api/radios/')
      .then(response => response.json())
      .then(data => {
        if(data)
            {
              for (let i = 0; i < data.length; i++){
                sessionStorage.setItem(data[i].name, data[i].stream_url);}
            }
          sessionStorage.setItem('streamsSet', 'yes');
        });
    }
}
setRadiosStreams();
// document.querySelectorAll('.card')
// document.querySelectorAll('.card .do-import')


function makeImportExport(elem, url){
// replace setTimeout with api request fetch
  let makeExport = url.includes('export');
  console.log(makeExport);
  let currentBtn = elem.outerHTML;
  let radioName = elem.id.split('-').pop();
  url += radioName;
  let tracksEl = '';
  let dateEl = '';

  if(makeExport)
      {
          tracksEl = document.querySelector('#card-' + radioName + ' .tracks-num-to-export');
          dateEl = document.querySelector('#card-' + radioName + ' .export-date');
          for(let exportBtn of document.querySelectorAll('.do-export'))
            exportBtn.disabled = true;
      }
  else
      {
          tracksEl = document.querySelector('#card-' + radioName + ' .tracks-num');
          dateEl = document.querySelector('#card-' + radioName + ' .import-date');
      }

  let tracksNum = parseInt(tracksEl.innerText);
  // event.target.outerHTML = document.querySelector(".spinner.template").outerHTML.replace('display:none', '');
  // event.target.style.display = "";
  elem.innerHTML = '';
  elem.disabled = true;
  let border = elem.style.borderColor;
  elem.style.borderColor = 'rgba(0,0,0,0)';
  let clonedElem = document.querySelector(".spinner.template").cloneNode(true);

  clonedElem.style.display = 'flex';
  elem.appendChild(clonedElem);
  fetch(url)
    .then(response => response.json())
    .then(data => {
      for(let exportBtn of document.querySelectorAll('.do-export'))
        exportBtn.disabled = false;
      clonedElem.remove();
      elem.outerHTML = currentBtn;
      // if (data.success)
      //   {
          if(makeExport){
            tracksNum -= data.num_tracks_exported;
            tracksEl.innerText = tracksNum.toString();
            dateEl.innerText = data.export_date;
          }
          else{
            tracksNum += data.num_tracks_added;
            tracksEl.innerText = tracksNum.toString();
            dateEl.innerText = data.import_date;
          }

        // }
        // if (!data.success)
        // make alarm
      });
}

function importAllRadios(){
  let radios = document.querySelectorAll('.card .do-import');
  for (let i = 0; i < radios.length; i++)
    radios[i].click();
}

function liveSearch(objectsQuery){
  let searcher = document.getElementById('liveSearch');
  let objs = document.querySelectorAll(objectsQuery);
  searcher.addEventListener('input', function(){
  let input = searcher.value.toLowerCase();
  if(input.length > 0)
    {
      for (let i = 0; i < objs.length; i++) {
        if(!objs[i].children[0].innerText.toLowerCase().includes(input))
          objs[i].style.display = 'none';
        else
          objs[i].style.display = 'block';
      }
    }
  else {hideElements(objs, false)}
    console.log();
  })
}

liveSearch('.card');

function hideElements(objs, bool=true){
  if(bool === true)
        {
          for (let i = 0; i < objs.length; i++)
            objs[i].style.display = 'none';
        }
  else
        {
          for (let i = 0; i < objs.length; i++)
            objs[i].style.display = 'block';
        }
}

document.querySelector('.card').style.backgroundColor = 'rgb(11 0 255 / 9%) !important';

function playRadio(elemId){
  let radioName = elemId.split('-').pop();
  if(sessionStorage.getItem('playingNow'))
      pauseRadio();
  sessionStorage.setItem('playingNow', radioName);
  audioObj.src = sessionStorage.getItem(radioName);
  audioObj.play();
  document.getElementById('pause-' + radioName).style.display = '';
  document.getElementById('play-' + radioName).style.display = 'none';
  document.getElementById('card-' + radioName).style.cssText = 'rgb(11 0 255 / 9%) !important';
}

function pauseRadio(){
  audioObj.pause();
  let tmp = audioObj;
  audioObj = document.createElement('audio');
  tmp.remove();
  audioObj.controls = true;
  document.body.appendChild(audioObj);
  let radioName = sessionStorage.getItem('playingNow');
  document.getElementById('pause-' + radioName).style.display = 'none';
  document.getElementById('play-' + radioName).style.display = '';
  sessionStorage.removeItem('playingNow');
  document.getElementById('card-' + radioName).style.cssText = '';
}

function keepPlayingHere(){
  let radioName = sessionStorage.getItem('playingNow');
  if(radioName){
      playRadio('play-' + radioName);
  }
}
keepPlayingHere();
