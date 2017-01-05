
var timeoutId = 0;
var data = [];

var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 480 - margin.left - margin.right,
    height = 320 - margin.top - margin.bottom;

var parseDate = d3.time.format("%H:%M:%S").parse;

var xcenter =  width/2;

var x = d3.time.scale()
    .range([0, width]);
    
var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickFormat(d3.time.format("%S"));

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var line = d3.svg.line()
    .x(function(d) { return x(d.creatTime);})
    .y(function(d) { return y(d.cpuTime); });

// function

function myGetTime() {
    var dd = new Date();
    var hh = dd.getHours();
    var mm = dd.getMinutes();
    var ss = dd.getSeconds();
    return hh + ":" + mm + ":" + ss;
}

function getRandomArbitrary(min, max) {
  return Math.round (Math.random() * (max - min) + min) -1;
}

function getTime(data) {
  if(data.length === 25) {
    // when length of data equal 60 then pop data[0]
    data.shift();
  }
  data.push({
      "creatTime":  myGetTime(),
      "cpuTime": getRandomArbitrary(0,101),
  });
}

function update() {
  getTime(data);
  render();
  timeoutId = setTimeout("update()", 1000);
}

function render() {
  
d3.select("svg")
       .remove();

var svg = d3.select("#chart2").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom + 40)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  
 data.forEach(function(d) {
     if(typeof d.creatTime === "string") {
       d.cpuTime = +d.cpuTime;
        d.creatTime = parseDate(d.creatTime);
     }
             
 });
  
  x.domain(d3.extent(data, function(d) { return d.creatTime; }));
  y.domain(d3.extent(data, function(d) { return d.cpuTime; }));

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .style("text-anchor", "end")
      .call(xAxis) 
  .append("text")
      .attr("transform", "rotate(0)")
      .attr("y", 40)
      .attr("dx", xcenter)
      .attr("font-size", "1.3em")
      .style("text-anchor", "end")
      .text("time(s)");
     
  svg.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate("+ height +",-180px)")
      .style("text-anchor", "end")
      .call(yAxis)
   .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", -40)
      .attr("dy", ".41em")
      .attr("font-size", "1.3em")
      .style("text-anchor", "end")
      .text("CPU%");

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);
}

// Start
update();
