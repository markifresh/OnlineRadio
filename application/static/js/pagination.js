var artistsPage = location.pathname.includes('artists');
var objectNum = 0;

if(artistsPage)
  url = '/api/tracks' + location.pathname + 'num';
else
  url = '/api' + location.pathname + 'num';
  fetch(url)
    .then(response => response.json())
    .then(data => {
      objectNum = data.number;
      setTotalPages(objectNum);
    })

initListeners('/api/users/' + getCookie('user_id') + '/imports');

function setTotalPages(objectNum){
// let objNum = Object.keys(data).length;
let pageLimit = parseInt(document.querySelector('#limitSelect .active a').innerText);
let pageNumbers = Math.round(objectNum / pageLimit);
let pages = document.querySelectorAll('#pageSelect .page');
let prevNextBtn = document.querySelectorAll('a.back-next');

if(pageNumbers < objectNum / pageLimit)
  pageNumbers += 1;

document.getElementById('totalPages').innerText = pageNumbers;

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



function pagesNextRange(){
  let totalPages = document.getElementById('totalPages').innerText;
  let borderPage = document.querySelector('.borderPage').parentElement;
  let pages = document.querySelectorAll('.page');
  if(pages[pages.length-1].innerText !==
            document.querySelector('.lastPage').innerText.split(' ')[1])
    {
      borderPage.classList.remove('active');
      document.querySelector('.firstPage').parentElement.classList.add('active');
      let pages = document.querySelectorAll('.page');
      for (let i=0; i< pages.length;  i++)
        {
          let pageNum = Number(pages[i].innerText) + 3;
          if(pageNum > Number(totalPages))
            pages[i].style.display = 'none';
          pages[i].innerText = Number(pages[i].innerText) + 3;
        }
    }
}

function pagesPrevRange(){
  let curPage = document.querySelector('#pageSelect .active');
  let pages = document.querySelectorAll('.page');
  if(pages[0].innerText!=='1'){
    for (let i=0; i< pages.length;  i++){
      if(pages[i].style.display == 'none')
        pages[i].style.display = '';
      pages[i].innerText = Number(pages[i].innerText) - 3;
    }

    curPage.classList.remove('active');
    document.querySelector('.borderPage').parentElement.classList.add('active');
  }
}

function nextPrevBtn(){
  if(document.querySelector('#pageSelect .active').innerText !== '1')
    document.querySelector('.prevPage').classList.remove('disabled');
  else
    document.querySelector('.prevPage').classList.add('disabled');

  if(document.querySelector('#pageSelect .active').innerText ==
              document.querySelector('.lastPage').innerText.split(' ')[1])
    document.querySelector('.nextPage').classList.add('disabled');
  else
  {
    if(document.querySelector('.nextPage').classList.contains('disabled'))
        document.querySelector('.nextPage').classList.remove('disabled');
      }
}


function backKey(){
  let curPage = document.querySelector('#pageSelect .active');
  if(curPage.innerText !== '1')
  {
      let pages = document.querySelectorAll('.page');
      if(document.querySelector('.firstPage').parentElement.classList.contains('active'))
          pagesPrevRange();
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

function nextKey(){
  let curPage = document.querySelector('#pageSelect .active');
  if(curPage.innerText !==
          document.querySelector('.lastPage').innerText.split(' ')[1])
  {
      let pages = document.querySelectorAll('.page');
      if(document.querySelector('.borderPage').parentElement.classList.contains('active'))
          pagesNextRange();
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


function getData(url=''){
  if(!url){
      let url = '';

      if(artistsPage)
        url = '/api/tracks' + location.pathname.slice(0, -1);
      else
        url = '/api' + location.pathname.slice(0, -1);

        let curPage = Number(document.querySelector('#pageSelect .active').innerText);
        let perPage = Number(document.querySelector('#limitSelect .active').innerText);
        let from = (curPage - 1) * perPage;
        url += '?limit=' + perPage + '&from_id=' + from

        fetch(url)
          .then(response => response.json())
          .then(data => {
            // console.log(data);
            setData(data);
          })
    }
  else{
    commonFetch(url, 'get', func=setData);
  }
  // console.log(url);

}

function setData(data){
  let table = document.querySelector('table');
  document.querySelector('table tbody').remove();
  let newTbody = document.createElement('tbody');
  for (let i = 0; i < data.length; i++)
      {
          // console.log(data[i]);
          let newTr = document.createElement('tr');
          let innerTds = '';
          //
          // if(artistsPage)
          //   innerTds = '<td>' + data[i] + '</td>';
          //
          // else
          // {
            for (let objKey of Object.values(data[i]))
            innerTds += '<td>' + objKey + '</td>';
          // }

          newTr.innerHTML = innerTds;
          // console.log(newTr.innerHTML);
          newTbody.appendChild(newTr)
      }

  table.appendChild(newTbody);
}

function initListeners(url=''){
document.getElementById('pageSelect').addEventListener('click', function(){
let curElem = event.target;
let curPar = event.target.parentElement;
if(curElem.classList.contains('page') && !curPar.classList.contains('active')){
    document.querySelector('#pageSelect .active').classList.remove('active');
    curPar.classList.add('active');
    if(document.querySelector('.borderPage').parentElement.classList.contains('active'))
      pagesNextRange();
    getData(url);
  }
if(curPar.classList.contains('prevPage'))
  {backKey();
  getData(url);}

if(curPar.classList.contains('nextPage'))
  {nextKey();
    getData(url);}

nextPrevBtn();

})


document.getElementById('limitSelect').addEventListener('click', function(){
  let curElem = event.target;
  let curPar = event.target.parentElement;
  if(curElem.classList.contains('page-link')){
    if(!curPar.classList.contains('active')){
      document.querySelector('#limitSelect .active').classList.remove('active');
      curPar.classList.add('active');
      getData(url);
      setTotalPages();
    }
  }
})
}
