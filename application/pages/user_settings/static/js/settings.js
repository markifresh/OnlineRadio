let carousel = new bootstrap.Carousel(document.getElementById('carouselExampleControls'), {ride: false, interval: false});

function showNextSlide(){
  carousel.next();
  let nextBtn = document.getElementById('carouselNextText');
  if (nextBtn.innerText == 'Options >')
    nextBtn.innerText = 'Radios >';
  else
    nextBtn.innerText = 'Options >';
}

let toast = new bootstrap.Toast(document.getElementById('liveToast'));
let toastHeader = document.getElementById('toastHeader');
let toastBody = document.getElementById('toastBody');
let pageHeader = document.getElementById('pageHeader');

if(document.querySelectorAll('.selectedCard').length == 0){
  document.getElementById('navbarToggleExternalContent').remove();
  // document.querySelector('.navbar-toggler-icon').style.display = "table-row";
}


function cardClick(domObj) {
  let radioName = domObj.replace('card-', '').split('_').join(' ').toUpperCase();
  domObj = document.getElementById(domObj);
  domObj.classList.toggle('selectedCard');
  if (domObj.classList.contains('selectedCard')){
    toastHeader.innerText = 'Radio added';
    toastBody.innerText = 'Radio "' + radioName + '" was successfully added'
    domObj.querySelector('.selected').style.display = "";
    domObj.querySelector('.unselected').style.display = "none";
    if (pageHeader.classList.contains('disabled')){
      pageHeader.classList.remove('disabled', 'btn-primary');
      pageHeader.classList.add('btn-success');
      pageHeader.innerText = 'Click me when you are done!'

    }
  }
  else{
    toastHeader.innerText = 'Radio removed';
    toastBody.innerText = 'Radio "' + radioName + '" was successfully removed'
    domObj.querySelector('.selected').style.display = "none";
    domObj.querySelector('.unselected').style.display = "";
    if (document.querySelectorAll('.selectedCard').length == 0){
      pageHeader.classList.add('disabled', 'btn-secondary');
      pageHeader.classList.remove('btn-success');
      pageHeader.innerText = 'Please select few radios to begin'

    }
  }

    toast.show()
}

function optionClick(domObj){
  let optionName = domObj.querySelector('.optionName').innerText;
  domObj.classList.toggle('selectedOption');
  if (domObj.classList.contains('selectedOption')){
    toastHeader.innerText = 'Option added';
    toastBody.innerText = 'Option "' + optionName + '" was successfully added'
    domObj.querySelector('.option-enabled').style.display = "";
    domObj.querySelector('.option-disabled').style.display = "none";
  }
  else{
    toastHeader.innerText = 'Option removed';
    toastBody.innerText = 'Option "' + optionName + '" was successfully removed'
    domObj.querySelector('.option-enabled').style.display = "none";
    domObj.querySelector('.option-disabled').style.display = "";
    }
    toast.show()
}

function updateDB(updateData){
  return true;
}
