const initialPageResults = 15;
var currentCarousel = 'carIE';
//  FROM PAGINATION STATIC //

function setTotalPages(carouselID, objectNum=''){

if(!objectNum)
// arguments.includes('objectNum') ||
  objectNum = document.getElementById(carouselID).querySelector('tbody').children.length
// let carouselActive = document.querySelector('.carousel-item.active');

let carouselActive = document.getElementById(carouselID);
let pageLimit = parseInt(carouselActive.querySelector('.limit-select .active a').innerText);
let pageNumbers = Math.round(objectNum / pageLimit);
let pages = carouselActive.querySelectorAll('.page-select .page');
let prevNextBtn = carouselActive.querySelectorAll('a.back-next');

if(pageNumbers < objectNum / pageLimit)
  pageNumbers += 1;

carouselActive.querySelector('.total-pages').innerText = pageNumbers;

  for(let i of pages)
    {
        if(Number(i.innerText) > pageNumbers && i.style.display == '')
            i.style.display = 'none';

        else if (Number(i.innerText) <= pageNumbers && i.style.display == 'none')
            i.style.display = '';
    }

  for(let i of prevNextBtn)
    {
        if(pageNumbers  <= 3 && i.style.display == '')
            i.style.display = 'none';

        else if(pageNumbers > 3 && i.style.display == 'none')
            i.style.display = '';
    }
}


function pagesNextRange(caruselID){
  let carouselActive = document.getElementById(caruselID);
  let totalPages = carouselActive.querySelector('.total-pages').innerText;
  let borderPage = carouselActive.querySelector('.borderPage').parentElement;
  let pages = carouselActive.querySelectorAll('.page');
  if(pages[pages.length-1].innerText !==
            carouselActive.querySelector('.lastPage').innerText.split(' ')[1])
    {
      borderPage.classList.remove('active');
      carouselActive.querySelector('.firstPage').parentElement.classList.add('active');
      let pages = carouselActive.querySelectorAll('.page');
      for (let i=0; i< pages.length;  i++)
        {
          let pageNum = Number(pages[i].innerText) + 3;
          if(pageNum > Number(totalPages))
            pages[i].style.display = 'none';
          pages[i].innerText = Number(pages[i].innerText) + 3;
        }
    }
}

function pagesPrevRange(caruselID){
  let carouselActive = document.getElementById(caruselID);
  let curPage = carouselActive.querySelector('.page-select .active');
  let pages = carouselActive.querySelectorAll('.page');
  if(pages[0].innerText!=='1'){
    for (let i=0; i< pages.length;  i++){
      if(pages[i].style.display == 'none')
        pages[i].style.display = '';
      pages[i].innerText = Number(pages[i].innerText) - 3;
    }

    curPage.classList.remove('active');
    carouselActive.querySelector('.borderPage').parentElement.classList.add('active');
  }
}

function nextPrevBtn(caruselID){
  let carouselActive = document.getElementById(caruselID);
  if(carouselActive.querySelector('.page-select .active').innerText !== '1')
    carouselActive.querySelector('.prevPage').classList.remove('disabled');
  else
    carouselActive.querySelector('.prevPage').classList.add('disabled');

  if(carouselActive.querySelector('.page-select .active').innerText ==
              carouselActive.querySelector('.lastPage').innerText.split(' ')[1])
    carouselActive.querySelector('.nextPage').classList.add('disabled');
  else
  {
    if(carouselActive.querySelector('.nextPage').classList.contains('disabled'))
        carouselActive.querySelector('.nextPage').classList.remove('disabled');
      }
}


function backKey(caruselID){
  let carouselActive = document.getElementById(caruselID);
  let curPage = carouselActive.querySelector('.page-select .active');
  if(curPage && curPage.innerText !== '1')
  {
      let pages = carouselActive.querySelectorAll('.page');
      if(carouselActive.querySelector('.firstPage').parentElement.classList.contains('active'))
          pagesPrevRange(caruselID);
      else
      {
        curPage.classList.remove('active');
        for (let i=0; i< pages.length;  i++)
          if(pages[i].innerText == Number(curPage.innerText) -1)
            {
              pages[i].parentElement.classList.add('active');
              break;
            }
        }
    }
}

function nextKey(caruselID){
  let carouselActive = document.getElementById(caruselID);
  let curPage = carouselActive.querySelector('.page-select .active');
  if(curPage.innerText !==
          carouselActive.querySelector('.lastPage').innerText.split(' ')[1])
  {
      let pages = carouselActive.querySelectorAll('.page');
      if(carouselActive.querySelector('.borderPage').parentElement.classList.contains('active'))
          pagesNextRange(caruselID);
      else
      {
        curPage.classList.remove('active');
        for (let i=0; i< pages.length;  i++)
          if(pages[i].innerText == Number(curPage.innerText) + 1)
            {
              pages[i].parentElement.classList.add('active');
              break;
            }
        }
    }
}

function manipulatePages(event, caruselID){
  let carouselActive = document.getElementById(caruselID);
  let curElem = event.target;
  let curPar = event.target.parentElement;
  if(curElem.classList.contains('page') && !curPar.classList.contains('active')){
      carouselActive.querySelector('.page-select .active').classList.remove('active');
      curPar.classList.add('active');
      if(carouselActive.querySelector('.borderPage').parentElement.classList.contains('active'))
        pagesNextRange(caruselID);
      limitedData(caruselID);
    }
  if(curPar.classList.contains('prevPage'))
    {backKey(caruselID);
    limitedData(caruselID);}

  if(curPar.classList.contains('nextPage'))
    {nextKey(caruselID);
      limitedData(caruselID);}

  nextPrevBtn(caruselID);
}

function manipulateLimits(event, caruselID){
  let carouselActive = document.getElementById(caruselID);
  let curElem = event.target;
  let curPar = event.target.parentElement;
  if(curElem.classList.contains('page-link')){
    if(!curPar.classList.contains('active')){
      carouselActive.querySelector('.limit-select .active').classList.remove('active');
      curPar.classList.add('active');
      limitedData(caruselID);
      setTotalPages(caruselID);
    }
  }

}

////////////////// REPLACED ////////////////////////
function initListeners(caruselID){
document.querySelector('#' + caruselID + ' .page-select').addEventListener('click', function(){manipulatePages(event, caruselID)});
document.querySelector('#' + caruselID + ' .limit-select').addEventListener('click', function(){manipulateLimits(event, caruselID)});
}

function resetPagination(caruselID){
  // set limit to minimal
  // set pages to minimal
  // set total pages
}

initListeners('carIE');
initListeners('carTracks');
///////////////////////////////////////////////////////////
function limitedData(caruselID){
  // carouselActive.querySelector('table').id)
  let carouselActive = document.getElementById(caruselID);
  let tableElements = carouselActive.querySelector('tbody').children;
  let curPage = Number(carouselActive.querySelector('.page-select .active').innerText);
  let perPage = Number(carouselActive.querySelector('.limit-select .active').innerText);
  let start = curPage * perPage - perPage;
  let end = curPage * perPage;
  for(let i=0; i < tableElements.length; i++){
    if(i >= start && i < end)
        tableElements[i].style.display = '';
    else
        tableElements[i].style.display = 'none'
  }
}


function setTracksData(data){
  setTotalPages('carTracks', data.length);
  let ths = document.getElementById('tableTracksHeaders');
  ths.innerHTML = '<th class="col-1"></th>\n';
  ths.innerHTML += '<th class="col-3">Artist</th>\n';
  ths.innerHTML += '<th class="col-4">Title</th>\n';
  ths.innerHTML += '<th class="col-2">Play Date</th>\n';
  ths.innerHTML += '<th class="col-1">Rank</th>\n';
  ths.innerHTML += '<th class="col-1"></th>\n';


  let table = document.getElementById('tableTracks');

  table.querySelector('tbody').remove();
  let newTbody = document.createElement('tbody');
  for (let i = 0; i < data.length; i++)
      {
          let newTr = document.createElement('tr');
          if( i>= initialPageResults)
            newTr.style.display = 'none';

          let innerTds = '';
          newTr.id = data[i]['id'];
          newTr.classList.add('ms_id-' + data[i]['ms_id']);
          let pathLikedClass = data[i]['liked'] ? 'liked' : '';
          innerTds += '<td>';
          innerTds += '<button class="btn btn-sm shadow-none track-like">' +
                          '<svg height="23px" class="track-like" viewBox="0 0 24 24" width="23px" fill="#000000">' +
                                '<path class="track-like ' + pathLikedClass + '" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="darkgray"/>' +
                          '</svg></button>';



          innerTds += '<button class="btn btn-sm shadow-none track-play">' +
                          '<svg class="track-play" height="32px" viewBox="0 0 24 24" width="32px" fill="#000000">' +
                                '<path class="track-play" d="M10 8.64L15.27 12 10 15.36V8.64M8 5v14l11-7L8 5z" fill="darkgray"/>' +
                          '</svg></button>';
          innerTds += '</td>';

          innerTds += '<td class="embed-holder">' + data[i]['artist'] + '</td>';
          innerTds += '<td>' + data[i]['title'] + '</td>';
          innerTds += '<td>' + formatDate(data[i]['play_date']) + '</td>';
          innerTds += '<td>' + data[i]['rank'] + '</td>';
          innerTds += '<td>';
          innerTds += '<button class="btn btn-sm shadow-none track-delete" >' +
                          '<svg class="track-delete" height="24px" viewBox="0 0 24 24" width="24px" fill="#000000">' +
                                '<path class="track-delete" d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1zM18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z" fill="darkgray"/>' +
                          '</svg></button>';

          innerTds += '<button class="btn btn-sm shadow-none track-export"">' +
                          '<svg class="track-export" height="26px" viewBox="0 0 24 24" width="26px" fill="#000000">' +
                                '<path class="track-export" d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z" fill="darkgray"/>' +
                          '</svg></button>';
                          innerTds += '</td>';
          newTr.innerHTML = innerTds;
          newTbody.appendChild(newTr);
          // newTr = document.createElement('tr');
          // iframeCreator(data[i]['ms_id'], newTr);
          // newTbody.appendChild(newTr);

      }

  table.appendChild(newTbody);
}

function setImportsData(data){
  setTotalPages('carIE', data.length);
  let ths = document.getElementById('tableHeaders');
  ths.innerHTML = '<th class="col-5">Import Date</th>\n';
  ths.innerHTML += '<th class="col-5">Tracks added</th>\n';
  ths.innerHTML += '<th class="col-3">Exported</th>\n';
  ths.innerHTML += '<th class="col-2">Reviewed</th>\n';

  let table = document.getElementById('tableIE');
  table.querySelector('tbody').remove();
  let newTbody = document.createElement('tbody');
  for (let i = 0; i < data.length; i++)
      {
          let newTr = document.createElement('tr');
          if( i>= initialPageResults)
            newTr.style.display = 'none';

          let innerTds = '';
          newTr.id = data[i]['import_date'];
          innerTds += '<td>' + formatDate(data[i]['import_date']) + '</td>';
          innerTds += '<td>' + data[i]['num_tracks_added'] + '</td>';
          innerTds += '<td>' + data[i]['exported'] + '</td>';
          innerTds += '<td>' + data[i]['reviewed'] + '</td>';

          newTr.innerHTML = innerTds;
          newTr.onclick = showTracks;
          newTbody.appendChild(newTr)
      }

  table.appendChild(newTbody);
}

function setExportsData(data){
  setTotalPages('carIE', data.length);
  let ths = document.getElementById('tableHeaders');
  ths.innerHTML = '<th class="col-5">Export Date</th>\n';
  ths.innerHTML += '<th class="col-5">Tracks added</th>\n';

  let table = document.getElementById('tableIE');
  table.querySelector('tbody').remove();
  let newTbody = document.createElement('tbody');
  for (let i = 0; i < data.length; i++)
      {
          let newTr = document.createElement('tr');
          if( i>= initialPageResults)
            newTr.style.display = 'none';

          let innerTds = '';
          newTr.id = data[i]['import_date'];
          innerTds += '<td>' + formatDate(data[i]['export_date']) + '</td>';
          innerTds += '<td>' + data[i]['num_tracks_exported'] + '</td>';

          newTr.innerHTML = innerTds;
          newTbody.appendChild(newTr)
      }

  table.appendChild(newTbody);
}


function getSetData(url, dataFunc){
  commonFetch(url, 'GET', {}, dataFunc);
}
