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

function commonFetch(url, fetchMethod='GET', data={}, func=console.log, errorFunc=console.log){
  let fetchHeaders = new Headers();
  fetchHeaders.append("Content-Type", "application/json");

  let requestOptions = {
    method: fetchMethod,
    headers: fetchHeaders,
  };

  if((Object.keys(data).length > 0))
    requestOptions.body = JSON.stringify(data);

  fetch(url, requestOptions)
  .then(response => response.json())
  .then(json => handleErrors(json))
  .then(json => func(json))
//  .then(json => func(data))
  .catch(error => errorFunc(error));
}

function formatDate(dateString){
  let current_datetime = new Date(dateString)
  let day = current_datetime.getDate();
  day = (day > 9)? day : '0' + day;

  let month = current_datetime.getMonth() + 1;
  month = (month > 9)? month : '0' + month;

  let hours = current_datetime.getHours();
  hours = (hours > 9)? hours : '0' + hours;

  let minutes = current_datetime.getMinutes();
  minutes = (minutes > 9)? minutes : '0' + minutes;

  let seconds = current_datetime.getSeconds();
  seconds = (seconds > 9)? seconds : '0' + seconds;

  let formatted_date = day + "/" +
                      month + "/" +
                      current_datetime.getFullYear() + " " +
                      hours + ":" + minutes + ':' + seconds
  return formatted_date;
}
