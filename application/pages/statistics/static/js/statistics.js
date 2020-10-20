// create Bar chart from csv file, using default options


// create Donut chart using defined data & customize plot options
// new roughViz.Donut(
//   {
//     element: '#viz1',
//     data: {
//       labels: ['North', 'South', 'East', 'West'],
//       values: [10, 5, 8, 3]
//     },
//     title: "Regions",
//     width: window.innerWidth / 4,
//     roughness: 8,
//     colors: ['red', 'orange', 'blue', 'skyblue'],
//     stroke: 'black',
//     strokeWidth: 3,
//     fillStyle: 'cross-hatch',
//     fillWeight: 3.5,
//   }
// );

function createBar(data, objectID){
  data = {labels: Object.keys(data), values: Object.values(data)};
  new roughViz.Bar({
     element: '#' + objectID,
     data: data,
     height: 570,
     width: window.innerWidth - 100,
 //    xLabel: 'Height',
 //    yLabel: 'Width',
  margin: { top: 10, right: 50, bottom: 150, left: 150 },
padding: 0.1,
     axisFontSize: "1.5rem",
     labelFontSize: '3rem',
     roughness: 4,
//     font: 1,
 //    fillStyle: 'solid'
 });
}

// createBar({labels: ["FIP_ROCK", "FIP_JAZZ", "FIP_GROOVE", "FIP_WORLD", "FIP_NOUVEAUTES", "FIP_ELECTRO", "FIP_POP", "FIP", "DJAM"], values: [1145, 291, 753, 348, 213, 626, 733, 748, 1117]});
// "/api/radio_tracks/per_radios/num"
// "/api/radio_tracks/per_radios/num/not_reviewed"
// "/api/radio_tracks/per_radios/num/reviewed"
// "/api/dbimports/per_radios/num/"
//
// let a = data.result;
// let d_keys = Object.keys(a);
// let d_values = Object.values(a);
function buildGraphic(url, objectID){
  fetch(url)
    .then(response => response.json())
    .then(data => data.result)
    .then(data => createBar(data, objectID))
}
 // let a = {'FIP_ROCK': 19, 'FIP_JAZZ': 2, 'FIP_GROOVE': 5, 'FIP_WORLD': 2, 'FIP_NOUVEAUTES': 2, 'FIP_ELECTRO': 3, 'FIP_POP': 2, 'FIP': 2, 'DJAM': 3};
 // createBar({lables: Object.keys(a), values: Object.values(a)});
buildGraphic("/api/radio_tracks/per_radios/num", 'tracksNum');
buildGraphic("/api/radio_tracks/per_radios/num/not_reviewed", 'tracksReviewedNot');
buildGraphic("/api/radio_tracks/per_radios/num/reviewed", 'tracksReviewed');
buildGraphic("/api/dbimports/per_radios/num/", 'importsNum');
//
//'Number of tracks per radio'
//'Number of not reviewed tracks per radio'
//'Number of reviewed tracks per radio'
//'Number of imports per radio'
// function saveData(url){
//   fetch(url)
//     .then(response => response.json())
//     .then(data => {
//       data = data.result;
//       console.log(data);
//       localStorage.setItem('radios_num', JSON.stringify(data));
//       // console.log(Object.keys(data));
//       // console.log(Object.values(data));
//
//       // createBar({labels: ["FIP_ROCK", "FIP_JAZZ", "FIP_GROOVE", "FIP_WORLD", "FIP_NOUVEAUTES", "FIP_ELECTRO", "FIP_POP", "FIP", "DJAM"], values: [1145, 291, 753, 348, 213, 626, 733, 748, 1117]});
//       });
// }
// function getData(dataName){
//   let a = localStorage.getItem(dataName);
//   a = JSON.parse(a);
//   console.log(a);
//   return {lables: Object.keys(a), values: Object.values(a)};
// }
//
// saveData("/api/radio_tracks/per_radios/num");
// createBar(getData('radios_num'));
