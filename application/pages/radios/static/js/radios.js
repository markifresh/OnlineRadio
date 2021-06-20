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

function showEmbed(domElem, width){
  let track = domElem.classList[0].replace('ms_id-','')
  createEmbed(track, domElem, width);
  setTimeout(function(){
    domElem.querySelector('td iframe').parentElement.style.display = '';
    domElem.style.opacity = '1';
  }, 600);

}

document.getElementById('carTracks').addEventListener('click', function(event){
  if(event.target.parentElement.tagName == 'TR'){
    let elem = event.target.parentElement;
    console.log(elem);
    hideElem(elem.children[1]);
    // showEmbed(elem, elem.querySelector('td').offsetWidth);
    showEmbed(elem, width="300");

  }

})
