let carousel = new bootstrap.Carousel(document.getElementById('carouselExampleControls'), {ride: false, interval: false});
let toast = new bootstrap.Toast(document.getElementById('liveToast'));
let toastHeader = document.getElementById('toastHeader');
let toastBody = document.getElementById('toastBody');
let pageHeader = document.getElementById('pageHeader');

document.addEventListener('click', function(event){
  if(event.target.classList.contains('imports'))
      showImports();
  else if(event.target.classList.contains('exports'))
      showExports();
})

// if(getCookie('user_id') ){
//     selectUserRadios(getCookie('user_id'));
//     selectUserSettings(getCookie('user_id'));
// }

function setImports(){
  let url = '/api/users/' + getCookie('user_id') + '/imports';
  getSetData(url, setImportsData);
}

function showImports(){
  setImports();
  showNextSlide();
}

function setExports(){
  let url = '/api/users/' + getCookie('user_id') + '/exports';
  getSetData(url, setExportsData);

}

function showExports(){
    setExports();
    showNextSlide();
}

function setTracks(){

}

function showTracks(){
  document.getElementById('carouselText').innerText = '< Imports';
  let url = '/api/users/' + getCookie('user_id') + '/imports/' + this.id + '/tracks';
  commonFetch('/api/users/' + getCookie('user_id') + '/imports/' + this.id, 'GET', {}, function(data){
    console.log(data);
    document.querySelector('.tracks-header').id = data.import_date;
    document.querySelector('.tracks-header').innerHTML= 'Import: ' + formatDate(data.import_date) +
                                                          '<br> reviewed: ' + data.reviewed ;

  })

  getSetData(url, setTracksData);
  let textBTN = document.getElementById('carouselText');
  textBTN.innerText == '< Imports'
  carousel.next();
}


function showNextSlide(){
  let prevBTN = document.getElementById('carouselPrev');
  let textBTN = document.getElementById('carouselText');
//  If it's not 'Radio' slide
  if (prevBTN.style.display == 'none'){
    carousel.next();
    prevBTN.style.display = '';
    document.querySelector('audio').pause();
    document.querySelector('audio').style.display = 'none';
    }

// If it's 'Radio' slide
  else{
    carousel.prev();
    if (textBTN.innerText == '< Imports'){
      setTotalPages('carIE');
      textBTN.innerText = '< Radios';
    }

    else{
    prevBTN.style.display = 'none';
    document.querySelector('audio').style.display = '';
  }
  }

}

function errorToast(data){
  toastHeader.innerText = 'ERROR';
  toastBody.innerText = data;
  toast.show();
}

function headerMissing(){
    pageHeader.style.display = "";
    pageHeader.classList.add('disabled', 'btn-secondary');
    pageHeader.classList.remove('btn-success');
    pageHeader.innerText = 'Please select few radios to begin'
}

function headerFilled(){
    pageHeader.style.display = "";
    pageHeader.classList.remove('disabled', 'btn-primary');
    pageHeader.classList.add('btn-success');
    pageHeader.innerText = 'Click me when you are done!'
}
