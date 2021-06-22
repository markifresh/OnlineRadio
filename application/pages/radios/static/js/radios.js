function hideElem(domElem){
  domElem.style.transitionDuration = "600ms";
  // domElem.style.transitionDelay  = "500ms";
  domElem.style.opacity = '0';
  setTimeout(function(){
    domElem.style.display = 'none';
    // let tds = domElem.querySelectorAll('td');
    // tds[0].style.display = 'none';
    // for (let td of tds)
    //   td.style.display = 'none';
  }, 600);

}

function showElem(domElem){
  domElem.style.opacity = '1';
}

function toggleEmbed(domElem, width){
  if(!domElem.querySelector('.embed-player')){
    let track = domElem.classList[0].replace('ms_id-','')
    createEmbed(track, domElem, width);
    setTimeout(function(){
      domElem.querySelector('.embed-player').style.display = '';
      domElem.style.opacity = '1';
    }, 600);
}
  else{
      domElem.querySelector('.embed-holder').style.opacity = '1';
    setTimeout(function(){
      domElem.querySelector('.embed-holder').style.display = '';
      domElem.querySelector('.embed-player').remove();
      domElem.style.opacity = '1';
    }, 600);
  }
}

function findBTN(elem){
  let btn = '';
  if(elem.parentElement.tagName == 'BUTTON')
    btn =  elem.parentElement;

  else if(elem.parentElement.parentElement.tagName == 'BUTTON')
    btn = elem.parentElement.parentElement;
  return btn
}

document.getElementById('carTracks').addEventListener('click', function(event){
  if(event.target.classList.contains('track-play')){
    let btn = findBTN(event.target);
    btn.classList.toggle('flip');
    let elem = btn.parentElement.parentElement;
      hideElem(elem.children[1]);
      // showEmbed(elem, elem.querySelector('td').offsetWidth);
      toggleEmbed(elem, width="300");
    }
  else if(event.target.classList.contains('track-like')){
    let btn = findBTN(event.target);
    btn.querySelector('path').classList.toggle('liked');
    }

})
