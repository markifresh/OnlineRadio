let carousel = new bootstrap.Carousel(document.getElementById('carouselExampleControls'), {ride: false, interval: false});
let toast = new bootstrap.Toast(document.getElementById('liveToast'));
let toastHeader = document.getElementById('toastHeader');
let toastBody = document.getElementById('toastBody');
let pageHeader = document.getElementById('pageHeader');


if(getCookie('user_id') ){
    selectUserRadios(getCookie('user_id'));
    selectUserSettings(getCookie('user_id'));
}


function showNextSlide(){
  carousel.next();
  let nextBtn = document.getElementById('carouselNextText');
  if (nextBtn.innerText == 'Options >')
    nextBtn.innerText = 'Radios >';
  else
    nextBtn.innerText = 'Options >';
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

// WORKING WITH RADIO CARDS //
function selectUserRadios(user_id){
let url = '/api/users/' + user_id + '/radios'
fetch(url)
  .then(response => response.json())
  .then(radios => {
        for(let radio of radios){
            let domObj = document.getElementById('card-' + radio.name);
            domObj.classList.toggle('selectedCard');
            domObj.querySelector('.selected').style.display = "";
            domObj.querySelector('.unselected').style.display = "none";
        }
        return true;
  })
  .then(result => {
      if(document.querySelectorAll('.selectedCard').length == 0){
      document.getElementById('navbarToggleExternalContent').remove();
      headerMissing();
      pageHeader.style.display = "";
      // document.querySelector('.navbar-toggler-icon').style.display = "table-row";
}
  })
}


function cardClick(domObj) {
  let radioName = domObj.replace('card-', '');
  domObj = document.getElementById(domObj);

  if (!domObj.classList.contains('selectedCard'))
    addRadio(getCookie('user_id'), radioName);

  else
    deleteRadio(getCookie('user_id'), radioName);
}

function addRadio(user_id ,radioName) {
  let url = '/api/users/' + user_id + '/radios';
  let data = {"radio_name": radioName};
  commonFetch(url, 'PUT', data, addRadioCard, errorToast);
}

function deleteRadio(user_id, radioName){
  let url = '/api/users/' + user_id + '/radios';
  let data = {"radio_name": radioName};
  commonFetch(url, 'DELETE', data, deleteRadioCard, errorToast);
}

function addRadioCard(data){
  let radioName = data.radio_name;
  let domObj = document.getElementById('card-' + radioName);
  domObj.classList.toggle('selectedCard');
  toastHeader.innerText = 'Radio added';
  toastBody.innerText = 'Radio "' + radioName.split('_').join(' ').toUpperCase() + '" was successfully added'
  domObj.querySelector('.selected').style.display = "";
  domObj.querySelector('.unselected').style.display = "none";
  if (pageHeader.classList.contains('disabled'))
     headerFilled();
  toast.show();
}

function deleteRadioCard(data){
  let radioName = data.radio_name;
  let domObj = document.getElementById('card-' + radioName);
  domObj.classList.toggle('selectedCard');
  toastHeader.innerText = 'Radio removed';
  toastBody.innerText = 'Radio "' + radioName.split('_').join(' ').toUpperCase() + '" was successfully removed'
  domObj.querySelector('.selected').style.display = "none";
  domObj.querySelector('.unselected').style.display = "";
  if (document.querySelectorAll('.selectedCard').length == 0)
      headerMissing();

  toast.show();
}


// WORKING WITH OPTIONS CARDS //
function selectUserSettings(user_id){
  let url = '/api/users/' + user_id + '/settings'
  fetch(url)
    .then(response => response.json())
    .then(settings => {
          for(let setting of settings.result){
              let domObj = document.getElementById(setting);
              domObj.classList.toggle('selectedOption');
              domObj.querySelector('.option-enabled').style.display = "";
              domObj.querySelector('.option-disabled').style.display = "none";
          }
    })
}

function optionClick(domObj){
  if (!domObj.classList.contains('selectedOption'))
      addSetting(getCookie('user_id'), domObj.id);
  else
      deleteSetting(getCookie('user_id'), domObj.id);
      }

function addSetting(user_id, settingName){
  let url = '/api/users/' + user_id + '/settings';
  let data = {"user_setting": settingName};
  commonFetch(url, 'PUT', data, addOptionCard, errorToast);
}

function addOptionCard(data){
  let domObj = document.getElementById(data.setting);
  domObj.classList.toggle('selectedOption');
  toastHeader.innerText = 'Option added';
  toastBody.innerText = 'Option "' + domObj.querySelector('.optionName').innerText  + '" was successfully added'
  domObj.querySelector('.option-enabled').style.display = "";
  domObj.querySelector('.option-disabled').style.display = "none";
  toast.show();
}

function deleteSetting(user_id, settingName){
  let url = '/api/users/' + user_id + '/settings';
  let data = {"user_setting": settingName};
  commonFetch(url, 'DELETE', data, deleteOptionCard, errorToast);
}

function deleteOptionCard(data){
  let domObj = document.getElementById(data.setting);
  domObj.classList.toggle('selectedOption');
  toastHeader.innerText = 'Option removed';
  toastBody.innerText = 'Option "' + domObj.querySelector('.optionName').innerText + '" was successfully removed'
  domObj.querySelector('.option-enabled').style.display = "none";
  domObj.querySelector('.option-disabled').style.display = "";
  toast.show();
}




