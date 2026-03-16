/*-----0-----------------------------------------------------------------*/
$("#more_tags").click(function(){
    var len = parseInt($('#inputs').children('input').length)+1;
    var newTag = $( "<input />", {type: "text", 'name': 'term_'+len, 'id': 'term_'+len, "placeholder": "Insira um termo"});
    $('#inputs').append(newTag);
});

$("#clear_tags").click(function(){
    $("#inputs").empty();
    var newTag = $( "<input />", {type: "text", 'name': 'term_'+len, 'id': 'term_'+len, "placeholder": "Insira um termo"});
    $('#inputs').append(newTag);
});

/*-----1-----------------------------------------------------------------*/
$.ajax({
    url: 'graph1',
    type: 'GET',
    dataType: 'json'
}).done(function(data){
    new Chartist.Bar('#graph1', {
      labels: data.labels,
      series: data.values
    }, {
      distributeSeries: true
    });
})

/*-----2-----------------------------------------------------------------*/
$.ajax({
    url: 'graph2',
    type: 'GET',
    dataType: 'json'
}).done(function(data){
    new Chartist.Bar('#graph2', {
      labels: data.labels,
      series: data.values
    }, {
      distributeSeries: true
    });
})

/*-----3-----------------------------------------------------------------*/
function getDataToChart(){
    var inp = $('#inputs').children('input');
    var inpTerms = [];
    for(var i=0; i<inp.length; i++){
        inpTerms.push(inp[i].value);
    }
    $.ajax({
        url: 'graph3',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify(inpTerms)
    }).done(function(res){
        if(res.result){
            var options = {
              showLine: true,
              height: 250,
              axisX: {
                labelInterpolationFnc: function(value, index) {
                  return 'R$ ' + value;
                }
              }
            };

            var abz = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'w', 'y', 'z'];
            $("#graph-legend").empty();
            for(var i=0; i<res.data.terms.length; i++){
                var newTag = $( "<span />", {text: res.data.terms[i], "class": "legend-"+abz[i]});
                $("#graph-legend").append(newTag)
            }

            new Chartist.Line('#graph3', res.data, options);
        }else{
            alert(res.message)
        }
    })
};

