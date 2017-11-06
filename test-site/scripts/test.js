var init = function(data) {
  var xLabel = 'Year';
  var yLabel = 'Internet Users (millions)';
  var colorLabel = 'Countries';
  var margin = { left: 120, right: 300, top: 20, bottom: 120 };
  
  var xValue = function(d){ return d['Year']; };
  var yValue = function(d){ return +d['Internet Users by World Region']; };
  var colorValue = function(d){ return d['Entity']; };
  var viz = d3.select('#viz-holder');
  var svg = viz.append('svg');
  var width =  +viz.attr('data-width');
  var height = +viz.attr('data-height');
  svg.attr('width', width);
  svg.attr('height', height);
  var innerWidth = width - margin.left - margin.right;
  var innerHeight = height - margin.top - margin.bottom;

  var radius = 5;

  var g = svg.append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
 
  var xAxisG = g.append('g')
    .attr('transform', 'translate(0, '+ innerHeight + ')');
  
  var yAxisG = g.append('g');
  var colorLegendG = g.append('g')
    .attr('transform', 'translate('+ (innerWidth + 60) + ', 150)');

  xAxisG.append('text')
    .attr('class', 'axis-label')
    .attr('x', innerWidth / 2)
    .attr('y', 60)
    .text(xLabel);

  yAxisG.append('text')
    .attr('class', 'axis-label')
    .attr('x', -(innerHeight / 2))
    .attr('y', -60)
    .attr('transform', 'rotate(-90)')
    .style('text-anchor', 'middle')
    .text(yLabel);

  colorLegendG.append('text')
    .attr('class', 'legend-label')
    .attr('x', -30)
    .attr('y', -40)
    .text(colorLabel);

  var xScale = d3.scaleLinear();
  var yScale = d3.scaleLinear();
  var colorScale = d3.scaleOrdinal()
  .range(d3.schemeCategory10);

  var xAxis = d3.axisBottom()
    .scale(xScale)
    .tickPadding(15)
    .tickSize(-innerHeight)
    .tickFormat(d3.format("d"));

  var yAxis = d3.axisLeft()
    .scale(yScale)
    .ticks(8)
    .tickPadding(15)
    .tickSize(-innerWidth)
    .tickFormat(d3.format("d"));

  var colorLegend = d3.legendColor()
    .scale(colorScale)
    .shape('circle')

  var row = function(d){
    d['Year'] = +d['Year'];
    d['Internet Users by World Region'] = +d['Internet Users by World Region']/1000000;
    return d;
  };

  xScale.domain(d3.extent(data, xValue))
    .range([0, innerWidth])
    .nice();

  yScale.domain(d3.extent(data, yValue))
    .range([innerHeight, 0])
    .nice();

  g.selectAll('circle').data(data)
    .enter()
    .append('circle')
    .attr('cx', function(d){ return xScale(xValue(d))})
    .attr('cy', function(d){ return yScale(yValue(d))})
    .attr('fill', function(d){ return colorScale(colorValue(d))})
    .attr('fill-opacity', 0.8)
    .attr('r', radius)
    .on("mouseover", handleMouseOver)
    .on("mouseout",handleMouseOut);


  xAxisG.call(xAxis);
  yAxisG.call(yAxis);
  colorLegendG.call(colorLegend)
    .selectAll('.cell text')
    .attr('dy', '0.1em');



  function handleMouseOver(d, i){    
    d3.select(this).attrs({
      r: radius * 2
    });

    g.append("text").attrs({
      id: "id" + d['Year'] + "-" + Math.round(d['Internet Users by World Region']) +  "-" + i,
      x: function() { return xScale(d['Year']) - 300; },
      y: function() { return yScale(d['Internet Users by World Region']) - 15; },
      fill: colorScale(colorValue(d))
    })
    .text(function() {
      return ["(" + d['Entity'] + '; Year ' + d['Year'] + '; Users ' + Math.round(d['Internet Users by World Region']) + " millions)"];
    });
  }

  function handleMouseOut(d, i) {
    d3.select(this).attrs({
      r: radius
    });

    d3.select("#id" + d['Year'] + "-" + Math.round(d['Internet Users by World Region']) +  "-" + i).remove();
  }
}

var data = "Entity,Code,Year,Internet Users by World Region\nEast Asia & Pacific,,1990,132691.59\nEast Asia & Pacific,,1993,1501300.6\nEast Asia & Pacific,,1994,2250131.3\nEast Asia & Pacific,,1995,4065725.3\nEast Asia & Pacific,,1996,9121098\nEast Asia & Pacific,,1997,21433646\nEast Asia & Pacific,,1998,37775384\nEast Asia & Pacific,,1999,69031400\nEast Asia & Pacific,,2000,114411096\nEast Asia & Pacific,,2001,149704016\nEast Asia & Pacific,,2002,187232864\nEast Asia & Pacific,,2003,221344672\nEast Asia & Pacific,,2004,266393472\nEast Asia & Pacific,,2005,312472896\nEast Asia & Pacific,,2006,356616928\nEast Asia & Pacific,,2007,448706208\nEast Asia & Pacific,,2008,549420416\nEast Asia & Pacific,,2009,646374720\nEast Asia & Pacific,,2010,754627776\nEast Asia & Pacific,,2011,829140032\nEast Asia & Pacific,,2012,910465856\nEast Asia & Pacific,,2013,994101440\nEast Asia & Pacific,,2014,1058220032\nEast Asia & Pacific,,2015,1135598208\nEurope & Central Asia,,1990,405516.66\nEurope & Central Asia,,1992,2230605.8\nEurope & Central Asia,,1993,2709031.3\nEurope & Central Asia,,1994,4826030.5\nEurope & Central Asia,,1995,8764860\nEurope & Central Asia,,1996,15796067\nEurope & Central Asia,,1997,28855642\nEurope & Central Asia,,1998,46741868\nEurope & Central Asia,,1999,79586128\nEurope & Central Asia,,2000,113651216\nEurope & Central Asia,,2001,141667168\nEurope & Central Asia,,2002,199505616\nEurope & Central Asia,,2003,246049616\nEurope & Central Asia,,2004,281550304\nEurope & Central Asia,,2005,307425376\nEurope & Central Asia,,2006,333382080\nEurope & Central Asia,,2007,383639584\nEurope & Central Asia,,2008,417656992\nEurope & Central Asia,,2009,447800928\nEurope & Central Asia,,2010,498933824\nEurope & Central Asia,,2011,525517184\nEurope & Central Asia,,2012,568226496\nEurope & Central Asia,,2013,597322112\nEurope & Central Asia,,2014,628357376\nEurope & Central Asia,,2015,651396608\nLatin America & Caribbean,,1992,63254.625\nLatin America & Caribbean,,1993,140654.11\nLatin America & Caribbean,,1994,239488.78\nLatin America & Caribbean,,1995,535404.94\nLatin America & Caribbean,,1996,1526337.3\nLatin America & Caribbean,,1997,3062660\nLatin America & Caribbean,,1998,6275913\nLatin America & Caribbean,,1999,10636173\nLatin America & Caribbean,,2000,20529908\nLatin America & Caribbean,,2001,30145118\nLatin America & Caribbean,,2002,48072228\nLatin America & Caribbean,,2003,61881540\nLatin America & Caribbean,,2004,80010728\nLatin America & Caribbean,,2005,93593520\nLatin America & Caribbean,,2006,118301200\nLatin America & Caribbean,,2007,136830656\nLatin America & Caribbean,,2008,154885088\nLatin America & Caribbean,,2009,183600208\nLatin America & Caribbean,,2010,207803088\nLatin America & Caribbean,,2011,238327424\nLatin America & Caribbean,,2012,264581888\nLatin America & Caribbean,,2013,286630816\nLatin America & Caribbean,,2014,305474304\nLatin America & Caribbean,,2015,344699296\nMiddle East & North Africa,,1990,4989.8101\nMiddle East & North Africa,,1995,105850.01\nMiddle East & North Africa,,1996,245630.16\nMiddle East & North Africa,,1997,676369.25\nMiddle East & North Africa,,1998,1476618.6\nMiddle East & North Africa,,1999,2840093.3\nMiddle East & North Africa,,2000,5335063.5\nMiddle East & North Africa,,2001,6669439\nMiddle East & North Africa,,2002,12293885\nMiddle East & North Africa,,2003,17099494\nMiddle East & North Africa,,2004,28379684\nMiddle East & North Africa,,2005,33809724\nMiddle East & North Africa,,2006,41735356\nMiddle East & North Africa,,2007,54381972\nMiddle East & North Africa,,2008,69223744\nMiddle East & North Africa,,2009,81528168\nMiddle East & North Africa,,2010,95786264\nMiddle East & North Africa,,2011,108924224\nMiddle East & North Africa,,2012,125402784\nMiddle East & North Africa,,2013,141691952\nMiddle East & North Africa,,2014,165313744\nMiddle East & North Africa,,2015,185348464\nNorth America,,1990,2061729.8\nNorth America,,1991,3107251.3\nNorth America,,1992,4688757\nNorth America,,1993,6251414\nNorth America,,1994,13497925\nNorth America,,1995,25834064\nNorth America,,1996,46273300\nNorth America,,1997,63492716\nNorth America,,1998,90580024\nNorth America,,1999,111092336\nNorth America,,2000,137339792\nNorth America,,2001,158568848\nNorth America,,2002,188422048\nNorth America,,2003,199351360\nNorth America,,2004,210753088\nNorth America,,2005,224042144\nNorth America,,2006,229295552\nNorth America,,2007,250048544\nNorth America,,2008,250578896\nNorth America,,2009,244851552\nNorth America,,2010,249116528\nNorth America,,2011,245896880\nNorth America,,2012,263516048\nNorth America,,2013,256106192\nNorth America,,2014,263777120\nNorth America,,2015,271351008\nSouth Asia,,1992,1289.1177\nSouth Asia,,1993,2580.4053\nSouth Asia,,1994,13306.033\nSouth Asia,,1995,282905.75\nSouth Asia,,1996,523995.63\nSouth Asia,,1997,786485.75\nSouth Asia,,1998,1562359.3\nSouth Asia,,1999,3079257.5\nSouth Asia,,2000,6568352\nSouth Asia,,2001,9364691\nSouth Asia,,2002,21009870\nSouth Asia,,2003,26939710\nSouth Asia,,2004,32468616\nSouth Asia,,2005,38477012\nSouth Asia,,2006,45792896\nSouth Asia,,2007,61932816\nSouth Asia,,2008,69880656\nSouth Asia,,2009,82794544\nSouth Asia,,2010,117372184\nSouth Asia,,2011,155163472\nSouth Asia,,2012,192828384\nSouth Asia,,2013,233430464\nSouth Asia,,2014,331627840\nSouth Asia,,2015,412109408\nSub-Saharan Africa,,1996,412235.94\nSub-Saharan Africa,,1997,793491.19\nSub-Saharan Africa,,1998,1480821.5\nSub-Saharan Africa,,1999,2338062.3\nSub-Saharan Africa,,2000,3346164.3\nSub-Saharan Africa,,2001,4404465.5\nSub-Saharan Africa,,2002,5836959\nSub-Saharan Africa,,2003,8017975.5\nSub-Saharan Africa,,2004,11179489\nSub-Saharan Africa,,2005,15588604\nSub-Saharan Africa,,2006,22919702\nSub-Saharan Africa,,2007,29542962\nSub-Saharan Africa,,2008,46463908\nSub-Saharan Africa,,2009,58850300\nSub-Saharan Africa,,2010,85416360\nSub-Saharan Africa,,2011,108736208\nSub-Saharan Africa,,2012,134855712\nSub-Saharan Africa,,2013,162368064\nSub-Saharan Africa,,2014,190740752\nSub-Saharan Africa,,2015,224100224"; 

init(d3.dsvFormat(',').parse(data));
