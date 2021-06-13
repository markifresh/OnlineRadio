function getCookie(name) {
    let cookieList = document.cookie.split('; ');
    for(let cookie of cookieList){
        if(cookie.includes(name + '='))
          return cookie.split('=').pop();
          }
    return null;
}


function handleErrors(jsonData) {
    if (Object.keys(jsonData).includes('message'))
        throw jsonData.message;
    return jsonData;
}

function commonFetch(url, fetchMethod, data, func, errorFunc){
  let myHeaders = new Headers();
  myHeaders.append("Content-Type", "application/json");

  let requestOptions = {
    method: fetchMethod,
    body: JSON.stringify(data),
    headers: myHeaders,
  };

  fetch(url, requestOptions)
  .then(response => response.json())
  .then(json => handleErrors(json))
  .then(json => func(json))
//  .then(json => func(data))
  .catch(error => errorFunc(error));
}