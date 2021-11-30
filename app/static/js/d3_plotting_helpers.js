
var scatterPlot = function(data){

    if(data == null){
        console.log("Dataset provided is null");
    }
    else{
        console.log("loaded data");
    }

    var svg = d3.select("#canvas");

    var margin = {top: 10, right: 30, bottom: 30, left: 60};
    var width = 460 - margin.left - margin.right;
    var height = 400 - margin.top - margin.bottom;

    //console.log("Width: ", width);
    //console.log("Height: ", height);

    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleLinear().range([ 0, width ]);
    var y = d3.scaleLinear().range([ height, 0 ]);

    console.log(data)


     plot_data(data);

     function plot_data(data){

          //console.log("Plotting data");

          //if(data == null){
          //  console.log("data is null");
          //}
          //else{
          //  console.log(data);
          //}

          console.log(data)
          // Axes
          var xAxisCall = d3.axisBottom(x);
          var xAxis = g.append("g")
                        .attr("class", "x-axis")
                        .attr("transform", "translate(" + 0 + "," + height + ")");

          var yAxisCall = d3.axisLeft(y);
          var yAxis = g.append("g")
                .attr("class", "y-axis");

          // Labels
            xAxis.append("text")
                .attr("class", "axis-title")
                .attr("transform",
            "translate(" + (width/2) + " ," +
                           (height + margin.top + 20) + ")")
                //.attr("transform", "translate(" + width + ", 0)")
                //.attr("y", -6)
                .text("Grade Point Average")
            yAxis.append("text")
                .attr("class", "axis-title")
                .attr("transform", "rotate(-90)")
                .attr("y", 16)
                .text("Height / Centimeters");


         // Update our scales
    x.domain([d3.min(data, function(d){ return d.nwga; }) / 1.05,
        d3.max(data, function(d){ return d.nwga; }) * 1.05])
    y.domain([d3.min(data, function(d){ return d.wga; }) / 1.05,
        d3.max(data, function(d){ return d.wga; }) * 1.05])

          // Update our axes
         xAxis.call(xAxisCall);
         yAxis.call(yAxisCall);
         var circles = g.selectAll("circle").data(data);

          circles.attr("cx", function(d){ return x(d.nwga) })
                 .attr("cy", function(d){ return y(d.wga) })

          circles.enter()
                .append("circle")
                .attr("cx", function(d){ return x(d.nwga) })
                .attr("cy", function(d){ return y(d.wga) })
                .attr("r", 5)
                .attr("fill", function(d){ return d.color }); //"grey");
     }


}