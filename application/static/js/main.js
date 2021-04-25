function getCookie(name) {
    let cookieList = document.cookie.split('; ');
    for(let cookie of cookieList){
        if(cookie.includes(name + '='))
          return cookie.split('=').pop();
          }
    return null;
}