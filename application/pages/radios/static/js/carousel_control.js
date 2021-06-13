let carousel = new bootstrap.Carousel(document.getElementById('carouselExampleControls'), {ride: false, interval: false});
let toast = new bootstrap.Toast(document.getElementById('liveToast'));
let toastHeader = document.getElementById('toastHeader');
let toastBody = document.getElementById('toastBody');
let pageHeader = document.getElementById('pageHeader');


if(getCookie('user_id') ){
    selectUserRadios(getCookie('user_id'));
    selectUserSettings(getCookie('user_id'));
}

function showImports(){
    showNextSlide();
    document.getElementById('tableHeaders').innerHTML = '' +
        '<th scope="col">Export Date</th>\n' +
        '<th scope="col">Tracks Added</th>\n' +
        '<th scope="col">Exported</th>\n' +
        '<th scope="col">Reviewed</th>'

}

function showExports(){
    showNextSlide();
    document.getElementById('tableHeaders').innerHTML = '' +
        '<th scope="col">Import Date</th>\n' +
        '<th scope="col">Tracks Added</th>'
}

function showTracks(){
//    showNextSlide();
    document.getElementById('tableHeaders').innerHTML = '' +
        '<th scope="col">Artist</th>\n' +
        '<th scope="col">Title</th>\n' +
        '<th scope="col">Rank</th>'
}


function showNextSlide(){
  carousel.next();
  let nextBtn = document.getElementById('carouselNext');

//  If it's not 'Radio' slide
  if (nextBtn.style.display == 'none'){
    nextBtn.style.display = '';
    document.querySelector('audio').pause();
    document.querySelector('audio').style.display = 'none';
    }

// If it's 'Radio' slide
  else{
    nextBtn.style.display = 'none';
    document.querySelector('audio').style.display = '';
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