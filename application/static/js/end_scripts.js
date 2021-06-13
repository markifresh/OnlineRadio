
//audioObj.style.display="none";

 document.querySelector('.container').addEventListener('click', function(){
   if(event.target.classList.contains('do-import'))
        {
            let radioName = event.target.id.split('-').pop();
            makeImportExport(event.target, '/api/users/' + getCookie('user_id') + '/imports/' + radioName);
        }


   if(event.target.classList.contains('do-custom-import'))
      makeImportExport(event.target, '/api/imports/per_date');

   if(event.target.classList.contains('do-export'))
      {
        let radioName = event.target.id.split('-').pop();
        makeImportExport(event.target, '/api/users/' + getCookie('user_id') + '/exports/' + radioName);
      }
    if(event.target.classList.contains('play-radio'))
       playRadio(event.target.id);

    if(event.target.classList.contains('pause-radio'))
      pauseRadio();
 })

disableUpdate();
function disableUpdate(cardID = null){
    let selector = '.card';
    if (cardID)
        selector = cardID;

    let cards = document.querySelectorAll(selector);
    for (let card of cards){
        if (card.querySelector('.import-date')){
            let cardImport = card.querySelector('.import-date').innerText.split('/')[0];
            if (cardImport == new Date().getDate())
                card.querySelector('.do-import').classList.add('disabled')
            }
        }

    }

// document.querySelectorAll('.card')
// document.querySelectorAll('.card .do-import')
function fillInImportData(){
}

function fillInExportData(){
}

function makeImport(user_id, radio_name){
}

function makeExport(user_id, radio_name){
}

function getLatestExport(){
}

function setupImportExportData(data){

}

function makeImportExport(elem, url, funcData){
// replace button with loader
  let btnOuter = elem.outerHTML;
  let height = elem.parentElement.offsetHeight;
  elem.parentElement.style.marginTop = "4.7%";
//  let btnInner = elem.innerHTML;
  let radioName = elem.id.split('-').pop();
  let loader = document.querySelector(".spinner.template");
  elem.outerHTML = loader.outerHTML.replace("template", radioName);
  document.querySelector(".spinner." + radioName).style.height = (height) + "px";
  document.querySelector(".spinner." + radioName).style.display = 'contents';

//  let btnOuter = elem.parentElement.innerHTML;
  let tracksEl = '';
  let dateEl = '';


//  url += radioName;


  if(btnOuter.includes('do-export'))
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

  let data = { 'account_id': getCookie('user_id'),
               'radio_name': radioName}

  if(btnOuter.includes('do-export') && funcData)
      data.import_date = funcData.import_data;

  else if(btnOuter.includes('do-custom-import') && funcData){
      data.start_date = funcData.start_date;
      data.end_date = funcData.end_date;
    }


    setTimeout(function() {commonFetch(url, 'POST', data, function (fetchResult)

  {
      for(let exportBtn of document.querySelectorAll('.do-export')){
        if (!exportBtn.classList.contains('btn'))
            exportBtn.disabled = false;
      }

//      clonedElem.remove();

      // Disable update button if radio was already updated
      if(btnOuter.includes('do-import') && new Date(fetchResult.import_date).getDate() == new Date().getDate())
          btnOuter = btnOuter.replace('do-import', 'do-import disabled');



      document.querySelector(".spinner."+ radioName).parentElement.style.marginTop = "0px";
      document.querySelector(".spinner."+ radioName).outerHTML = btnOuter;
      // if (data.success)
      //   {
          if(btnOuter.includes('do-export')){
            if (fetchResult.num_tracks_exported > 0)
            {
                tracksNum -= fetchResult.num_tracks_exported;
                tracksEl.innerText = tracksNum.toString();
            }
            dateEl.innerText = fetchResult.export_date;
          }

          else{
            if (fetchResult.num_tracks_added > 0){
                tracksNum += data.num_tracks_added;
                tracksEl.innerText = tracksNum.toString();
            }
            dateEl.innerText = fetchResult.import_date;
          }



        // }
        // if (!data.success)
        // make alarm
      },
      function (fetchResult){
        console.log(fetchResult);
      })}, 2000);


}

function importAllRadios(elemID){
  let radios = document.querySelectorAll('.card .do-import:not(.disabled)');;
  for (let i = 0; i < radios.length; i++)
    radios[i].click();
}


if (document.getElementById('importAll') != null){
document.getElementById('importAll').addEventListener('click', function(){
importAllRadios('importAll');
});
}

document.querySelector('.card').style.backgroundColor = 'rgb(11 0 255 / 9%) !important';






//////////////////// RADIO PLAYING ///////////////////////

var audioObj = document.createElement('audio');
audioObj.controls = true;
audioObj.autoplay = true;
document.body.appendChild(audioObj);
audioObj.style.left=0;

function keepPlayingHere(){
  let radioName = sessionStorage.getItem('playingNow');
  if(radioName){
      playRadio('play-' + radioName);
  }
}
keepPlayingHere();

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
  audioObj.style.left=0;
//  audioObj.style.display="none";
  document.body.appendChild(audioObj);
  let radioName = sessionStorage.getItem('playingNow');
  document.getElementById('pause-' + radioName).style.display = 'none';
  document.getElementById('play-' + radioName).style.display = '';
  sessionStorage.removeItem('playingNow');
  document.getElementById('card-' + radioName).style.cssText = '';
}

function setRadiosStreams(){
 fetch('/api/users/' + getCookie('user_id') + '/radios')
   .then(response => response.json())
   .then(data => {
     if(data)
         {
           for (let i = 0; i < data.length; i++)
             sessionStorage.setItem(data[i].name, data[i].stream_url);
         }
     });
}
setRadiosStreams();



////////////// Live Search ////////////////

function liveSearch(objectsQuery){
  let searcher = document.getElementById('liveSearch');
  let objs = document.querySelectorAll(objectsQuery);
  searcher.addEventListener('input', function(){
  let input = searcher.value.toLowerCase();
  if(input.length > 0)
    {
      for (let i = 0; i < objs.length; i++) {
        if(!objs[i].innerText.toLowerCase().includes(input))
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