// Convert the elements of the row
// into appropriate types
var rowConverter = function(d){

    var rslt = {
        nwga: parseFloat(d.nwga),
        wga: parseFloat(d.wga),
        state: d.state,
        color: d.color
    };

    return rslt;

}